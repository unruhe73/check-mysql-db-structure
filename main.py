#!/usr/bin/env python3

# You need python-mysql or python-mysqldb packet

import os
import sys
import string
import getopt
import check_mysql_db


def usage():
    print(sys.argv[0] + " --filename=sql_filename [--server=database_host --user=database_user --password=database_password --dbname=database_name --debug]")
    print("OR")
    print(sys.argv[0] + " -f sql_filename [-s database_host -u database_user -p database_password -n database_name -d]")


def get_parameters():
    dbhost = "localhost"
    dbuser = ""
    dbpasswd = ""
    dbname = ""
    sql_filename = ""
    outdebug = False
    check_mysql_db_version = "0.1"

    try:
        opts, args = getopt.getopt(sys.argv[1:], "hvdu:p:n:f:s:", ["help", "version", "debug", "user=", "password=", "dbname=", "filename=", "server="])

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
        elif output in ("-s", "--server"):
            dbhost = argument
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

    return dbhost, dbuser, dbpasswd, dbname, sql_filename, outdebug

dbhost, dbuser, dbpasswd, dbname, sql_filename, outdebug = get_parameters()
checkMySQLDB = check_mysql_db.CheckMySQLDB(dbhost, dbuser, dbpasswd, dbname, sql_filename, outdebug)

if checkMySQLDB.error() == 1:
    print("*** ERROR: I need a database name!")
    print("\nI can't detect it from '%s', you need to specify it in the parameters with the '-n' option." % sql_filename)
    usage()
    sys.exit(2)
elif checkMySQLDB.error() == 2:
    print("*** ERROR: I need an SQL filename!")
    print("\nYou need to execute the application in this way:")
    usage()
    sys.exit(2)
elif checkMySQLDB.error() == 3:
    print("*** ERROR: I got '" + sql_filename + "' as an SQL file name, but it doesn't exist, try again!")
    print("\nYou need to execute the application in this way:")
    usage()
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
