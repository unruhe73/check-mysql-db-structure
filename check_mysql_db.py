#!/usr/bin/env python3

# You need python-mysqlclient or python-mysqldb packet

import os
from os.path import exists
import sys
import MySQLdb
import string
import getopt
import re
import shutil


class CheckMySQLDB:
    def __init__(self, dbhost, dbuser, dbpasswd, dbname, sql_filename, log_filename, outdebug):
        self.check_mysql_db_version = "0.2"
        self.error_code = 0
        self.dbhost = dbhost

        if dbuser == "":
            self.dbuser = "root"
        else:
            self.dbuser = dbuser

        self.dbpasswd = dbpasswd
        self.dbname = dbname
        if self.dbname == "":
            self.error_code = 1

        if sql_filename == "":
            self.error_code = 2
        else:
            if not exists(sql_filename):
                self.error_code = 3

        self.sql_filename = sql_filename
        self.outdebug = outdebug
        self.writeLogTo = True
        if not log_filename:
            self.log_filename = "check_database.log"

        if self.writeLogTo:
            try:
                self.logfile = open(self.log_filename, 'w')
                self.logfile.write("check_mysql_db v" + str(self.check_mysql_db_version) + "\n\n")
            except FileNotFoundError as error:
                print("*** Error: I cannot access log filename '%s' for witing!\n" % self.log_filename)
                sys.exit(2)

        self.count_drop = 0
        self.drop_db = ""

        self.count_create = 0
        self.create_db = ""

        self.count_use = 0
        self.use_db = ""
        self._count_drop_create_use_database()

        if self.count_drop > 1:
            self.error_code = 4
        elif self.count_create > 1:
            self.error_code = 5
        elif self.count_use > 1:
            self.error_code = 6

        self.tmp_database_name = "tmp_" + self.dbname
        self.tmp_database_filename = self.tmp_database_name + ".sql"

        self.writeLog("*** Command line parameters:")
        self.writeLog("database user: " + self.dbuser)
        if not self.dbpasswd:
            self.writeLog("database password: None")
        else:
            self.writeLog("database password: " + self.dbpasswd)
        self.writeLog("database name: " + self.dbname)
        self.writeLog("SQL filename: " + self.sql_filename)
        self.writeLog("temporary database name: " + self.tmp_database_name)
        self.writeLog("temporary database filename: " + self.tmp_database_filename)
        self.writeLog()

        self.binary_client = shutil.which("mariadb")
        if not self.binary_client:
            self.binary_client = shutil.which("mysql")

        if not self.binary_client:
            print("*** ERROR: sorry, but I can't find MySQL/MariaDB client on your system!")
            sys.exit(2)


    def writeLog(self, text = ""):
        if self.writeLogTo:
            self.logfile.write(text + "\n")

        if self.outdebug:
            print(text)


    def version(self):
        return self.check_mysql_db_version


    def versionStr(self):
        print("check_mysql_db v" + str(self.check_mysql_db_version))


    def error(self):
        return self.error_code


    def sqlCounter(self):
        if self.error_code == 4:
          ret = self.count_drop
        elif self.error_code == 5:
            ret = self.count_create
        elif self.error_code == 6:
            ret = self.count_use

        return ret


    def sqlFilename(self):
        return self.sql_filename


    def _lookfor(self, field, table):
        pos = 0
        while pos < len ( table ):
            if table[pos][0] == field:
                return pos
            pos += 1

        return -1


    def _cleanLine(self, line):
        # Define the pattern for matching comments
        pattern = re.compile(r'/\*.*?\*/', re.DOTALL)

        # Substitute the comments with an empty string
        removed_chars = re.sub(pattern, '', line)

        # Remove ';' and '`'
        result = removed_chars.replace(' ;', '').replace(';', '').replace('`', '').replace('\n', '').replace('  ', ' ')

        return result.split(' ')


    def _setDatabaseName(self, line, sql_keyword):
        keyword = sql_keyword.upper()
        clean_line = self._cleanLine(line)

        if keyword == "DROP":
            self.drop_db = clean_line[len(clean_line) - 1]
            self.writeLog("DROP database: " + self.drop_db)
        elif keyword == "CREATE":
            self.create_db = clean_line[len(clean_line) - 1]
            self.writeLog("CREATE database: " + self.create_db)
        elif keyword == "USE":
            self.use_db = clean_line[len(clean_line) - 1]
            self.writeLog("USE database: " + self.use_db)
            self.writeLog()


    def _count_drop_create_use_database(self):
        if self.error_code == 0 or self.error_code == 1:
            self.count_drop = 0
            self.count_create = 0
            self.count_use = 0

            with open(self.sql_filename) as fp:
                for line in fp:
                    splitted_line = line.strip().split(" ")
                    if splitted_line[0].upper() == "DROP" and splitted_line[1].upper() == "DATABASE":
                        self._setDatabaseName(line, "drop")
                        self.count_drop += 1
                    elif splitted_line[0].upper() == "CREATE" and splitted_line[1].upper() == "DATABASE":
                        self._setDatabaseName(line, "create")
                        self.count_create += 1
                    elif splitted_line[0].upper() == "USE":
                        self._setDatabaseName(line, "use")
                        self.count_use += 1

                if self.drop_db == self.create_db and self.create_db == self.use_db:
                    if not self.drop_db:
                        if not self.dbname:
                            self.error_code = 1
                        else:
                            self.error_code = 0
                    else:
                        if not self.dbname:
                            self.dbname = self.use_db
                            self.error_code = 0
                        else:
                            if self.dbname == self.use_db:
                                self.error_code = 0
                            else:
                                self.error_code = 7
                else:
                    self.error_code = 8


    def _is_sql_drop_database(self, sql_line):
        is_drop_database = False
        splitted_line = sql_line.strip().split(" ")

        if splitted_line[0].upper() == "DROP" and splitted_line[1].upper() == "DATABASE":
            is_drop_database = True

        return is_drop_database


    def _is_sql_create_database(self, sql_line):
        is_create_database = False
        splitted_line = sql_line.strip().split(" ")

        if splitted_line[0].upper() == "CREATE" and splitted_line[1].upper() == "DATABASE":
            is_create_database = True

        return is_create_database


    def _is_sql_use_database(self, sql_line):
        is_use_database = False
        splitted_line = sql_line.strip().split(" ")

        if splitted_line[0].upper() == "USE":
            is_use_database = True

        return is_use_database


    def _create_tmp_sql_file(self):
        if self.error_code == 0:
            new_database_file = open(self.tmp_database_filename, 'w')
            if self.count_drop == 0:
                new_database_file.write("DROP DATABASE IF EXISTS `" + self.tmp_database_name + "`;\n")
                new_database_file.write("CREATE DATABASE IF NOT EXISTS `" + self.tmp_database_name + "`;\n")
                new_database_file.write("USE `" + self.tmp_database_name + "`;\n\n\n");

            with open(self.sql_filename) as fp:
                for line in fp:
                    if self._is_sql_drop_database(line):
                        new_database_file.write("DROP DATABASE IF EXISTS `" + self.tmp_database_name + "`;\n")
                        new_database_file.write("CREATE DATABASE IF NOT EXISTS `" + self.tmp_database_name + "`;\n")
                        new_database_file.write("USE `" + self.tmp_database_name + "`;\n");
                    else:
                        if not self._is_sql_create_database(line) and not self._is_sql_use_database(line):
                            new_database_file.write(line)

            new_database_file.close()


    def compare_databases(self):
        self._create_tmp_sql_file()

        if self.error_code == 0:
            try:
                tmpConn = MySQLdb.connect(self.dbhost, self.dbuser, self.dbpasswd, "mysql")

            except MySQLdb.OperationalError as error:
                if self.outdebug:
                    print("Error %d: %s\n" % (error.args[0], error.args[1]))

                if error.args[0] == 2002:
                    print("*** ERROR: MySQL/MariaDB server is *NOT* available: I got a connection refused!")
                elif error.args[0] == 1045 or error.args[0] == 1698:
                    print("*** ERROR: can't access to the MySQL/MariaDB server")
                    print("\nPlease check the database access parameters:")
                    print("\tuser: %s\n\tpassword: %s\n" % (self.dbuser, self.dbpasswd))
                sys.exit(2)

            tmpConn.close()

            # add "-pPASSWORD" if root user uses a password
            if self.dbpasswd == "":
                return_value = os.system(f"{self.binary_client} -h " + self.dbhost + " -u " + self.dbuser + " < " + self.tmp_database_filename)
            else:
                return_value = os.system(f"{self.binary_client} -h " + self.dbhost + " -u " + self.dbuser + " -p" + self.dbpasswd + " < " + self.tmp_database_filename)

            if return_value != 0:
                print("it's NOT possible to import database to compare!")
                sys.exit (2)

            try:
                tmpConn = MySQLdb.connect(self.dbhost, self.dbuser, self.dbpasswd, self.tmp_database_name)

            except MySQLdb.OperationalError as e:
                print(self.tmp_database_name + " is not in the list as a local database. I can't compare!")
                sys.exit(2)

            tmp_cursor_table = tmpConn.cursor()
            tmp_cursor_table.execute("show tables")

            try:
                conn = MySQLdb.connect(self.dbhost, self.dbuser, self.dbpasswd, self.dbname)

            except MySQLdb.OperationalError as e:
                print(self.dbname + " is not present as local database. I can't compare!")
                sys.exit(2)

            cursor_table = conn.cursor()
            cursor_table.execute("show tables")

            if cursor_table.rowcount == tmp_cursor_table.rowcount:
                self.writeLog("*** in the first place the number of tables is correct.")
                self.writeLog("    +++ counted %d tables" % cursor_table.rowcount)

            else:
                self.writeLog("*** I got a different number of tables as in the reference database: %d vs the wanted %d!" % (cursor_table.rowcount, tmp_cursor_table.rowcount))

            table_index = 0
            database = {}
            fields_list = []
            while (table_index < cursor_table.rowcount):
                row = cursor_table.fetchone()
                cursor_field = conn.cursor()
                cursor_field.execute("SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE, COLUMN_KEY, COLUMN_DEFAULT, NUMERIC_PRECISION, CHARACTER_MAXIMUM_LENGTH FROM INFORMATION_SCHEMA.COLUMNS WHERE table_name = '"
                    + row[0] + "' AND table_schema = '" + self.dbname + "'")

                while (1):
                    rowfield = cursor_field.fetchone()
                    if rowfield == None:
                        break

                    else:
                        fields_list.append([ rowfield[0], rowfield[1], rowfield[2], rowfield[3], rowfield[4], rowfield[5], rowfield[6] ])

                database[row[0]] = fields_list
                fields_list = []

                table_index += 1

            cursor_field.close()
            cursor_table.close()
            conn.close()

            table_index = 0
            tmp_database = {}
            fields_list = []
            while (table_index < tmp_cursor_table.rowcount):
                row = tmp_cursor_table.fetchone()
                cursor_field = tmpConn.cursor()
                cursor_field.execute("SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE, COLUMN_KEY, COLUMN_DEFAULT, NUMERIC_PRECISION, CHARACTER_MAXIMUM_LENGTH FROM INFORMATION_SCHEMA.COLUMNS WHERE table_name = '"
                    + row[0] + "' AND table_schema = '" + "tmp_" + self.dbname + "'")

                while (1):
                    rowfield = cursor_field.fetchone()
                    if rowfield == None:
                        break

                    else:
                        fields_list.append([ rowfield[0], rowfield[1], rowfield[2], rowfield[3], rowfield[4], rowfield[5], rowfield[6] ])

                tmp_database[row[0]] = fields_list
                fields_list = []

                table_index += 1

            cursor_field.close()
            tmp_cursor_table.close()
            tmpConn.close()

            # to store not existing tables
            not_existing_table_from_installed_db = []

            count = 0
            for k in tmp_database.keys():
                if k in database.keys():
                    if tmp_database[k] != database[k]:
                        self.writeLog("********** table '" + k + "' is NOT the same!")
                        dim = len( tmp_database[ k ] )
                        index = 0
                        while index < dim:
                            item = tmp_database[k][index]
                            pos = self._lookfor(item[0], database[k])
                            if pos == -1:
                                self.writeLog("field '%s' is missing" % item[0])
                            else:
                                litem = database[k][pos]
                                if litem[1] != item[1]:
                                    self.writeLog("'%s' has different type" % item[0])
                                if litem[2] != item[2]:
                                    self.writeLog("'%s' has a different nullable" % item[0])
                                if litem[3] != item[3]:
                                    self.writeLog("'%s' has NOT the same key configuration: '%s' vs '%s'" % (item[0], litem[3], item[3]))
                                if litem[4] != item[4]:
                                    self.writeLog("'%s' default value has not the same default value: '%s' vs the wanted '%s'" % (item[0], litem[4], item[4]))
                                if litem[5] != item[5] and litem[5] != None and item[5] != None:
                                    self.writeLog("'%s' has precision (%d) setted in different way (%d)" % (item[0], litem[5], item[5]))
                                if litem[6] != item[6] and litem[6] != None and item[6] != None:
                                    self.writeLog("'%s' has the max number of characters different: %d vs the wanted %d" % (item[0], litem[6], item[6]))
                            index += 1
                else:
                    not_existing_table_from_installed_db.append(k)
                    self.writeLog("table '%s' is NOT into the local database, considered the reference database file '%s'" % (k, self.sql_filename))

            for k in database.keys():
                if k in tmp_database.keys():
                    if database[k] != tmp_database[k]:
                        dim = len(database[k])
                        index = 0
                        while index < dim:
                            item = database[k][index]
                            if self._lookfor(item[0], tmp_database[k]) == -1:
                                self.writeLog("in the database to verify, field '%s' seems to be extra (you could remove it)..." % item[0])
                            index += 1
                        count += 1
                else:
                    not_existing_table_from_installed_db.append(k)
                    self.writeLog("table '" + k + "' seems to be an extra")

            checked = 0
            if count == 0:
                if len(not_existing_table_from_installed_db) == 0:
                    self.writeLog("\n*** database structure is correct")
                else:
                    self.writeLog("\n*** database structure is incomplete!")
                checked = 1
            else:
                if count == 1:
                    self.writeLog("\n1 table has a different structure!")
                else:
                    self.writeLog("\n%d tables have different structure!" % count)

            # check extra tables (should be not there but it's not a real problem)
            count = 0
            for k in database.keys():
                if k not in tmp_database.keys():
                    self.writeLog("*** '" + k + "' table into the local database is extra, you could delete it!")
                    checked = 0
                    count += 1

            if count == 1:
                self.writeLog("\n*** 1 table exceed in the local database: how come?")
                checked = 0

            else:
                if count > 1:
                    self.writeLog("\n*** %d tables exceed in the local database: how come?" % count)
                    checked = 0

            if checked == 1:
                tmpConn = MySQLdb.connect(self.dbhost, self.dbuser, self.dbpasswd, self.tmp_database_name)
                tmp_cursor = tmpConn.cursor()

                conn = MySQLdb.connect(self.dbhost, self.dbuser, self.dbpasswd, self.dbname)
                cursor = conn.cursor()

                for k in tmp_database.keys():
                    if k not in not_existing_table_from_installed_db:
                        tmp_cursor.execute("select count(*) from %s" % k)
                        rowfield1 = tmp_cursor.fetchone()

                        cursor.execute("select count(*) from %s" % k)
                        rowfield2 = cursor.fetchone()

                        if rowfield1[0] != rowfield2[0]:
                            if rowfield1[0] > 0:
                                self.writeLog("\n\nrows number for '%s' maybe is NOT correct: it should be %s (according to the reference database file) but in local it's : %s" % (k, rowfield1[0], rowfield2[0]))
                                answer = input("do you want to take a look at the differences (Y/N)?")
                                if answer == "Y":
                                    tmp_cursor.execute("select * from %s" % k)
                                    i = 0
                                    queryCursor = conn.cursor()
                                    while i < tmp_cursor.rowcount:
                                        rowfield = tmp_cursor.fetchone()
                                        if rowfield != None:
                                            query = "SELECT * FROM %s WHERE" % k
                                            j = 0
                                            while j < len ( rowfield ):
                                                if rowfield[ j ] != None:
                                                    query += " %s = '%s' and " % (database[k][j][0], rowfield[j])
                                                else:
                                                    query += " %s = NULL and " % database[k][j][0]
                                                    j += 1
                                            query += "1=1"
                                            queryCursor.execute(query)
                                            if queryCursor.rowcount == 0:
                                                j = 0
                                                query = ""
                                                while j < len(rowfield):
                                                    query += " %s='%s'" % (database[k][j][0], rowfield[j])
                                                    j += 1
                                                self.writeLog("missing or NOT correctly corresponds: (%s)" % query)
                                        i += 1

                tmp_cursor.execute("DROP DATABASE `" + self.tmp_database_name + "`")
                tmp_cursor.close()
                tmpConn.close()
                cursor.close()
                conn.close()
            else:
                # drop the tmp database
                tmpConn = MySQLdb.connect(self.dbhost, self.dbuser, self.dbpasswd, self.tmp_database_name)
                tmp_cursor = tmpConn.cursor()
                tmp_cursor.execute("DROP DATABASE `" + self.tmp_database_name + "`")
                tmp_cursor.close()
                tmpConn.close()

            os.remove(self.tmp_database_filename)
            if self.writeLogTo:
                self.logfile.flush()
                self.logfile.close()
