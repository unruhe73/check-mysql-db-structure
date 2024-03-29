#!/usr/bin/env python3

# You need python-mysql or python-mysqldb packet

import os
import sys
import string
import argparse
import check_mysql_db


def get_parameters():
    dbhost = "localhost"
    dbuser = ""
    dbpasswd = ""
    dbname = ""
    sql_filename = ""
    outdebug = False
    logfile = ""
    check_mysql_db_version = "0.2"

    parser = argparse.ArgumentParser(description="A python script to compare two MySQL/MariaDB databases structure")
    pyname = sys.argv[0]
    parser.add_argument("-s", "--server", help="MySQL/MariaDB server address", type=str)
    parser.add_argument("-u", "--user", help="database username", type=str)
    parser.add_argument("-p", "--password", help="database password", type=str)
    parser.add_argument("-n", "--dbname", help="database name", type=str)
    parser.add_argument("-w", "--write-log-to", help="log filename where you get output results", type=str)
    parser.add_argument("-d", "--debug", help="write as much information as possible", action="store_true")
    parser.add_argument("-v", "--version", help="print the version of the script", action="store_true")
    parser.add_argument("filename", help="SQL filename to use to compare with the remote server database")
    args = parser.parse_args()

    if args.version:
        print("check_mysql_db v" + check_mysql_db_version)
        sys.exit()

    if args.server:
        dbhost = args.server

    if args.debug:
        outdebug = True

    if args.user:
        dbuser = args.user

    if args.password:
        dbpasswd = args.password

    if args.dbname:
        dbname = args.dbname

    if args.write_log_to:
        logfile = args.write_log_to

    sql_filename = args.filename

    return dbhost, dbuser, dbpasswd, dbname, sql_filename, logfile, outdebug


dbhost, dbuser, dbpasswd, dbname, sql_filename, logfile, outdebug = get_parameters()
checkMySQLDB = check_mysql_db.CheckMySQLDB(dbhost, dbuser, dbpasswd, dbname, sql_filename, logfile, outdebug)

if checkMySQLDB.error() == 1:
    print("*** ERROR: I need a database name!")
    print("\nI can't detect it from '%s', you need to specify it in the parameters with the '-n' option." % sql_filename)
    sys.exit(2)
elif checkMySQLDB.error() == 2:
    print("*** ERROR: I need an SQL filename!")
    print("\nYou need to execute the application in this way:")
    sys.exit(2)
elif checkMySQLDB.error() == 3:
    print("*** ERROR: I got '" + sql_filename + "' as an SQL file name, but it doesn't exist, try again!")
    print("\nYou need to execute the application in this way:")
    sys.exit(2)
elif checkMySQLDB.error() == 4:
    print("*** ERROR: file '%s' contains %d 'DROP DATABASE' SQL instruction. It has to be just one!" % (checkMySQLDB.sqlFilename(), checkMySQLDB.sqlCounter()))
    sys.exit(2)
elif checkMySQLDB.error() == 5:
    print("*** ERROR: file '%s' contains %d 'CREATE DATABASE' SQL instruction. It has to be just one!" % (checkMySQLDB.sqlFilename(), checkMySQLDB.sqlCounter()))
    sys.exit(2)
elif checkMySQLDB.error() == 6:
    print("*** ERROR: file '%s' contains %d 'USE' SQL instruction. It has to be just one!" % (checkMySQLDB.sqlFilename(), checkMySQLDB.sqlCounter()))
    sys.exit(2)

checkMySQLDB.compare_databases()
