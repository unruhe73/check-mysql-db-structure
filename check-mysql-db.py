#!/usr/bin/env python3

# You need python-mysql or python-mysqldb packet

import os
from os.path import exists
import sys
import MySQLdb
import string
import getopt

def usage():
    print(sys.argv[0] + " --dbname=database_name --filename=sql_filename [--user=database_user --password=database_password    --debug]")
    print("OR")
    print(sys.argv[0] + " -n database_name -f sql_filename [-u database_user -p database_password -d]")


def get_parameters():
    dbuser = ""
    dbpasswd = ""
    dbname = ""
    sql_filename = ""
    outdebug = False

    try:
        opts, args = getopt.getopt(sys.argv[1:], "hvdu:p:n:f:", ["help", "version", "debug", "user=", "password=", "dbname=", "filename="])

    except getopt.GetoptError as err:
        # print help information and exit:
        print(err)    # will print something like "option -a not recognized"
        usage()
        sys.exit(2)

    for output, argument in opts:
        if output in ("-h", "--help"):
            usage()
            sys.exit()
        elif output in ("-v", "--version"):
            print("check_mysql_db v" + check_mysql_db_version)
            sys.exit()
        elif output in ("-d", "--debug"):
            outdebug = True
        elif output in ("-u", "--user"):
            dbuser = argument
        elif output in ("-p", "--password"):
            dbpasswd = argument
        elif output in ("-n", "--dbname"):
            dbname = argument
        elif output in ("-f", "--filename"):
            sql_filename = argument
        else:
            assert False, "unhandled option"

    return dbuser, dbpasswd, dbname, sql_filename, outdebug


def lookfor(field, table):
    pos = 0
    while pos < len ( table ):
        if table[pos][0] == field:
            return pos
        pos += 1

    return -1


def is_sql_drop_database(sql_line, dbname):
    is_drop_database = False
    is_wanted_database = False
    database_name = ""
    splitted_line = sql_line.strip().split(" ")

    if splitted_line[0].upper() == "DROP" and splitted_line[1].upper() == "DATABASE":
        is_drop_database = True
        n1 = dbname
        n2 = "tmp_" + dbname
        database_name = splitted_line[len(splitted_line) - 1].replace(';', '').replace('`', '')
        if n1 == database_name or n2 == database_name:
            is_wanted_database = True

    return is_drop_database, is_wanted_database, database_name


def is_sql_create_database(sql_line):
    is_create_database = False
    splitted_line = sql_line.strip().split(" ")

    if splitted_line[0].upper() == "CREATE" and splitted_line[1].upper() == "DATABASE":
        is_create_database = True

    return is_create_database


def is_sql_use_database(sql_line):
    is_use_database = False
    splitted_line = sql_line.strip().split(" ")

    if splitted_line[0].upper() == "USE":
        is_use_database = True

    return is_use_database


def create_tmp_sql_file(database_sql_file, correct_database_name, tmp_database_filename):
    if not exists(database_sql_file):
        print("*** ERROR: file '%s' doesn't exist!" % database_sql_file)
        sys.exit(2)

    tmp_database_name = "tmp_" + correct_database_name
    new_database_file = open(tmp_database_filename, 'w')

    with open(database_sql_file) as fp:
        for line in fp:
            is_drop_database, is_wanted_database, database_name = is_sql_drop_database(line, correct_database_name)
            if is_drop_database:
                if is_wanted_database:
                    new_database_file.write("DROP DATABASE IF EXISTS `" + tmp_database_name + "`;\n")
                    new_database_file.write("CREATE DATABASE IF NOT EXISTS `" + tmp_database_name + "`;\n")
                    new_database_file.write("USE `" + tmp_database_name + "`;\n");
                else:
                    print("SQL file contains '%s' database definition that is *NOT* the wanted database '%s'" % (database_name, correct_database_name))
                    os.remove(tmp_database_filename)
                    sys.exit(2)
            else:
                if not is_sql_create_database(line) and not is_sql_use_database(line):
                    new_database_file.write(line)

    new_database_file.close()


def count_drop_create_use_database(database_sql_file):
    error = True
    count_drop = 0
    count_create = 0
    count_use = 0

    if exists(database_sql_file):
        error = False

        with open(database_sql_file) as fp:
            for line in fp:
                splitted_line = line.strip().upper().split(" ")
                if splitted_line[0] == "DROP" and splitted_line[1].upper() == "DATABASE":
                    count_drop += 1
                elif splitted_line[0] == "CREATE" and splitted_line[1].upper() == "DATABASE":
                    count_create += 1
                elif splitted_line[0] == "USE":
                    count_use += 1

    return error, count_drop, count_create, count_use


def compare_databases(dbuser, dbpasswd, dbname, sql_filename, outdebug):
    try:
        tmpConn = MySQLdb.connect(dbhost, dbuser, dbpasswd, "mysql")

    except MySQLdb.OperationalError as error:
        if outdebug:
            print("Error %d: %s\n" % (error.args[0], error.args[1]))
        if error.args[0] == 2002:
            print("*** ERROR: MySQL/MariaDB server is *NOT* available: I got a connection refused!")
        elif error.args[0] == 1045:
            print("*** ERROR: can't access to the MySQL/MariaDB server")
            print("\nPlease check the database access parameters:")
            print("\tuser: %s\n\tpassword: %s\n" % (dbuser, dbpasswd))
        sys.exit(2) 

    tmpConn.close()

    # add "-pPASSWORD" if root user uses a password
    if dbpasswd == "":
        return_value = os.system("mysql -u " + dbuser + " < " + tmp_database_filename)

    else:
        return_value = os.system("mysql -u " + dbuser + " -p" + dbpasswd + " < " + tmp_database_filename)

    if return_value != 0:
        print("it's NOT possible to import database to compare!")
        sys.exit (2)

    try:
        tmpConn = MySQLdb.connect(dbhost, dbuser, dbpasswd, "tmp_" + dbname)

    except MySQLdb.OperationalError as e:
        print("tmp_" + dbname + " is not in the list as a local database. I can't compare!")
        sys.exit(2)

    tmp_cursor_table = tmpConn.cursor()
    tmp_cursor_table.execute("show tables")

    try:
        conn = MySQLdb.connect(dbhost, dbuser, dbpasswd, dbname)

    except MySQLdb.OperationalError as e:
        print(dbname + " is not present as local database. I can't compare!")
        sys.exit(2)

    cursor_table = conn.cursor()
    cursor_table.execute("show tables")

    if cursor_table.rowcount == tmp_cursor_table.rowcount:
        print("*** in the first place the number of tables is correct.")
        print("    +++ counted %d tables" % cursor_table.rowcount)

    else:
        print("*** I got a different number of tables as in the reference database: %d vs the wanted %d!" % (cursor_table.rowcount, tmp_cursor_table.rowcount))

    table_index = 0
    database = {}
    lista = []
    while (table_index < cursor_table.rowcount):
        row = cursor_table.fetchone ()
        cursor_field = conn.cursor ()
        cursor_field.execute("SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE, COLUMN_KEY, COLUMN_DEFAULT, NUMERIC_PRECISION, CHARACTER_MAXIMUM_LENGTH FROM INFORMATION_SCHEMA.COLUMNS WHERE table_name = '"
            + row[0] + "' AND table_schema = '" + dbname + "'")

        while (1):
            rowfield = cursor_field.fetchone()
            if rowfield == None:
                break

            else:
                lista.append([ rowfield[0], rowfield[1], rowfield[2], rowfield[3], rowfield[4], rowfield[5], rowfield[6] ])

        database[row[0] ] = lista
        lista = []

        table_index += 1

    cursor_field.close()
    cursor_table.close()
    conn.close()

    table_index = 0
    tmp_database = {}
    lista = []
    while (table_index < tmp_cursor_table.rowcount):
        row = tmp_cursor_table.fetchone()
        cursor_field = tmpConn.cursor()
        cursor_field.execute("SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE, COLUMN_KEY, COLUMN_DEFAULT, NUMERIC_PRECISION, CHARACTER_MAXIMUM_LENGTH FROM INFORMATION_SCHEMA.COLUMNS WHERE table_name = '"
            + row[0] + "' AND table_schema = '" + "tmp_" + dbname + "'")

        while (1):
            rowfield = cursor_field.fetchone()
            if rowfield == None:
                break

            else:
                lista.append([ rowfield[0], rowfield[1], rowfield[2], rowfield[3], rowfield[4], rowfield[5], rowfield[6] ])

        tmp_database[row[0]] = lista
        lista = []

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
                print("********** table '" + k + "' is NOT the same!")
                dim = len( tmp_database[ k ] )
                index = 0
                while index < dim:
                    item = tmp_database[k][index]
                    pos = lookfor(item[0], database[k])
                    if pos == -1:
                        print("field '%s' is missing" % item[0])

                    else:
                        litem = database[k][pos]
                        if litem[1] != item[1]:
                            print("'%s' has different type" % item[0])
                        if litem[2] != item[2]:
                            print("'%s' has a different nullable" % item[0])
                        if litem[3] != item[3]:
                            print("'%s' has NOT the same key configuration: '%s' vs '%s'" % (item[0], litem[3], item[3]))
                        if litem[4] != item[4]:
                            print("'%s' default value has not the same default value: '%s' vs the wanted '%s'" % (item[0], litem[4], item[4]))
                        if litem[5] != item[5] and litem[5] != None and item[5] != None:
                            print("'%s' has precision (%d) setted in different way (%d)" % (item[0], litem[5], item[5]))
                        if litem[6] != item[6] and litem[6] != None and item[6] != None:
                            print("'%s' has the max number of characters different: %d vs the wanted %d" % (item[0], litem[6], item[6]))
                    index += 1

        else:
            not_existing_table_from_installed_db.append(k)
            print("table '%s' is NOT into the local database, considered the reference database file '%s'" % (k, sql_filename))

    for k in database.keys():
        if k in tmp_database.keys():
            if database[k] != tmp_database[k]:
                dim = len(database[k])
                index = 0
                while index < dim:
                    item = database[k][index]
                    if lookfor(item[0], tmp_database[k]) == -1:
                        print("in the database to verify, field '%s' seems to be extra (you could remove it)..." % item[0])
                    index += 1
                count += 1

        else:
            not_existing_table_from_installed_db.append(k)
            print("table '" + k + "' seems to be an extra")

    checked = 0
    if count == 0:
        if len(not_existing_table_from_installed_db) == 0:
            print("\n*** database structure is correct")

        else:
            print("\n*** database structure is incomplete!")
        checked = 1

    else:
        if count == 1:
            print("\n1 table has a different structure!")

        else:
            print("\n%d tables have different structure!" % count)

    # check extra tables (should be not there but it's not a real problem)
    count = 0
    for k in database.keys ():
        if k not in tmp_database.keys ():
            print("*** '" + k + "' table into the local database is extra, you could delete it!")
            checked = 0
            count += 1

    if count == 1:
        print("\n*** 1 table exceed in the local database: how come?")
        checked = 0

    else:
        if count > 1:
            print("\n*** %d tables exceed in the local database: how come?" % count)
            checked = 0

    if checked == 1:
        tmpConn = MySQLdb.connect(dbhost, dbuser, dbpasswd, "tmp_" + dbname)
        tmp_cursor = tmpConn.cursor()

        conn = MySQLdb.connect(dbhost, dbuser, dbpasswd, dbname )
        cursor = conn.cursor()

        for k in tmp_database.keys():
            if k not in not_existing_table_from_installed_db:
                tmp_cursor.execute("select count(*) from %s" % k)
                rowfield1 = tmp_cursor.fetchone()

                cursor.execute("select count(*) from %s" % k)
                rowfield2 = cursor.fetchone()

                if rowfield1[0] != rowfield2[0]:
                    if rowfield1[0] > 0:
                        print("\n\nrows number for '%s' maybe is NOT correct: it should be %s (according to the reference database file) but in local it's : %s" % (k, rowfield1[0], rowfield2[0]))
                        print("do you want to take a look at the differences (Y/N)?")
                        answer = raw_input ()
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
                                        print("missing or NOT correctly corresponds: (%s)" % query)
                                i += 1

        tmp_cursor.execute("DROP DATABASE `" + tmpDB + "`")
        tmp_cursor.close()
        tmpConn.close()
        cursor.close()
        conn.close()

    else:
        # drop the tmp database
        tmpConn = MySQLdb.connect(dbhost, dbuser, dbpasswd, "tmp_" + dbname )
        tmp_cursor = tmpConn.cursor()
        tmp_cursor.execute("DROP DATABASE `" + tmpDB + "`")
        tmp_cursor.close()
        tmpConn.close()


check_mysql_db_version = "0.1"
dbhost = "localhost"
dbuser, dbpasswd, dbname, sql_filename, outdebug = get_parameters()

if dbuser == "":
    dbuser = "root"

if dbname == "":
    print("*** ERROR: I need a database name!")
    print("\nYou need to execute the application in this way:")
    usage()
    sys.exit(2)

if sql_filename == "":
    print("*** ERROR: I need an SQL filename!")
    print("\nYou need to execute the application in this way:")
    usage()
    sys.exit(3)

if not exists(sql_filename):
    print("*** ERROR: I got '" + sql_filename + "' as an SQL file name, but it doesn't exist, try again!")
    print("\nYou need to execute the application in this way:")
    usage()
    sys.exit(3)

tmpDB = "tmp_" + dbname

file_error, count_drop, count_create, count_use = count_drop_create_use_database(sql_filename)
if not file_error:
    if count_drop > 1:
        print("*** ERROR: file '%s' contains %d 'DROP DATABASE' SQL instruction. It has to be just one!" % (sql_filename, count_drop))
        sys.exit(2)
    if count_create > 1:
        print("*** ERROR: file '%s' contains %d 'CREATE DATABASE' SQL instruction. It has to be just one!" % (sql_filename, count_create))
        sys.exit(2)
    if count_use > 1:
        print("*** ERROR: file '%s' contains %d 'USE' SQL instruction. It has to be just one!" % (sql_filename, count_use))
        sys.exit(2)
else:
    print("*** ERROR: file '%s' doesn't exist!" % sql_filename)
    sys.exit(2)

tmp_database_filename = tmpDB + ".sql"
create_tmp_sql_file(sql_filename, "example_db", tmp_database_filename)

if outdebug:
    print("*** Parameters I got:")
    print("database user: " + dbuser)
    if dbpasswd == "":
        print("database password: None")
    else:
        print("database password: " + dbpasswd)
    print("database name: " + dbname)
    print("SQL filename: " + sql_filename)
    print("temporary database name: " + tmpDB)
    print("temporary database filename: " + tmp_database_filename)
    print("")

compare_databases(dbuser, dbpasswd, dbname, sql_filename, outdebug)
os.remove(tmp_database_filename)
