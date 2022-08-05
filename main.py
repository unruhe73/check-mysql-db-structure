#!/usr/bin/env python3

# You need python-mysql or python-mysqldb packet

import os
import sys
import string
import getopt
import check_mysql_db


def usage():
    print(sys.argv[0] + " is a python script to compare two MySQL/MariaDB databases structure")
    print("")
    print("Usage: " + sys.argv[0] + " [OPTIONS]")
    print("")
    print("Optional parameters:")
    print("-d,--debug                            write as much as information possible")
    print("-s,--server=DATABASE_HOST             MySQL/MAriaDB server address")
    print("-u,--user=DATABASE_USER               database username")
    print("-p,--password=DATABASE_PASSOWRD       database password")
    print("-n,--dbname=DATABASE_NAME             database name")
    print("-w,--write-log-to=LOG_FILENAME        log filename where you get output results")
    print("")
    print("Needed parameters:")
    print("-f,--filename=SQL_FILENAME            SQL filename to use to compare with the remote server database")


def get_parameters():
    dbhost = "localhost"
    dbuser = ""
    dbpasswd = ""
    dbname = ""
    sql_filename = ""
    outdebug = False
    logfile = ""
    check_mysql_db_version = "0.1"

    try:
        opts, args = getopt.getopt(sys.argv[1:], "hvdu:p:n:f:s:w:", ["help", "version", "debug", "user=", "password=", "dbname=", "filename=", "server=", "write-log-to="])

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
        elif output in ("-w", "--write-log-to"):
            logfile = argument
        else:
            assert False, "unhandled option"

    return dbhost, dbuser, dbpasswd, dbname, sql_filename, logfile, outdebug

dbhost, dbuser, dbpasswd, dbname, sql_filename, logfile, outdebug = get_parameters()
checkMySQLDB = check_mysql_db.CheckMySQLDB(dbhost, dbuser, dbpasswd, dbname, sql_filename, logfile, outdebug)

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
