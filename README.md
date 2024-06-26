# Check MySQL DB Structure

[![GitHub license](./license-GPL-blue.svg)](https://github.com/unruhe73/check-mysql-db-structure/blob/main/LICENSE)
[![Made with Python 3](./python-3.x-powered.svg)](https://www.python.org/)


This project is a tool to compare two MySQL or MariaDB databases structure showing these details in form of text in a terminal, or writing them into a log file as you prefer. This tool is available by the python class `CheckMySQLDB`.

![Python](./python-powered-w-100x40.png)
![Produced-by-Human](./Produced-By-Human-Not-By-AI-Badge-black.png)

## Overview
You need a database server host. Suppose you have local installation of MySQL.
If you use Manjaro Linux and you have yet to install MariaDB give look at [here](https://www.linuxcapable.com/how-to-install-mariadb-on-manjaro-21-linux/).
I suggest to assign a password to root user if you just installed the server for the first time.

Install a database as the one into the file example_db.sql:
mysql -u root -p < example_db.sql

After that, you have example_db as a new local database.

To use the python class you need to keep installed `mysqlclient` python module.
You need to execute:

`pip install mysqlclient`

or install it directly through you Linux distro packages. For example, if you're using Arch Linux or Manjaro Linux you can run:

`sudo pacman -S python-mysqlclient`

if you configured `pacman` command into `sudo`.

## Pre-conditions
These are the pre-conditions for the script to work:

 1. You have a local database `example_db` stored into the server and I'm not sure it's correct.
 2. You have an SQL file reference for the database and I know it's correct (in the example is `correct_example_db.sql` but you can name it as you wish).
 3. You need mysqlclient python package installed: `pip install mysqlclient` or use directly the one from you Linux distro.


## How to use this project
You can get the compare of two database in two ways:

 1. using the `CheckMySQLDB` class including it in your python file
 2. using the ready-to-use `main.py` in this project

## Using the CheckMySQLDB class
You can use the `CheckMySQLDB` class including it in your python file:

`import check_mysql_db`

then you need to create an object of this class:

`checkMySQLDB = check_mysql_db.CheckMySQLDB(dbhost, dbuser, dbpasswd, dbname, sql_filename, logfile, outdebug)`

the parameters of the CheckMySQLDB() are all necessary:

`dbhost`: is the host where you have your MySQL/MariaDB server operative. If you assign it as an empty string, it will be considered as `localhost` as default.

`dbuser`: is the database username and it could be an empty string, in that case it will be replace by a `root` user as default.

`dbpasswd`: is the database password for the specified database user. Use an empty string if you have a database without a password.

`dbname`: is the name of the database it has to be verified on the server. It can be an empty string if this information can be detected from the SQL filename in the next parameter.

`sql_filename`: is the filename of the SQL server containing the correct wanted database on the dbhost server.

`logfile`: specify a text filename it will be created to write the result of the compare into. If it's an empty string than the results will be showed on the terminal.

`outdebug`: it has to be assigned as a boolen value: `True` or `False`. If you assign it as `True`, you'll get some debug output as the list of the parameters the class is using to compare the two databases.


After this assignment you can print the `checkMySQLDB.error()`. To go on with the compare, the returned value has to be 0.

To get the compare call `checkMySQLDB.compare_databases()`. Anyway you can also call it directly.
This function will verify on its own the `error()` value and it proceeds to compare just if it is 0.


## Using the ready-to-use main.py
For the details try to execute:

`python main.py -h`

OR

`python main.py --help`

And you get:
```
./main.py -h
usage: main.py [-h] [-s SERVER] [-u USER] [-p PASSWORD] [-n DBNAME] [-w WRITE_LOG_TO] [-d] [-v] filename

A python script to compare two MySQL/MariaDB databases structure

positional arguments:
  filename              SQL filename to use to compare with the remote server database

options:
  -h, --help            show this help message and exit
  -s SERVER, --server SERVER
                        MySQL/MAriaDB server address
  -u USER, --user USER  database username
  -p PASSWORD, --password PASSWORD
                        database password
  -n DBNAME, --dbname DBNAME
                        database name
  -w WRITE_LOG_TO, --write-log-to WRITE_LOG_TO
                        log filename where you get output results
  -d, --debug           write as much information as possible
  -v, --version         print the version of the script
```

`server` is the host where you have your MySQL/MariaDB server operative. It's optional. If you don't assign it, it will be considered as `localhost`.

`user` is the database username and is optional. If you don't assign it, it will be replace by a `root` user as default.

`password` is the database password for the specified database user. It is an optional value. If you have a database without a password you don't need to specify it.

`dbname` is the database name, but it could be detected directly from the SQL_FILENAME into filename option if this is not present.

`debug` is optional and as default value is assigned to `False`. If you specify it as `True`, you'll get some debug output as the list of the parameters the class is using to compare the two databases.

`write-log-to` is optional. If you specify it than the outupt will be redirected to the LOG_FILENAME file, otherwise it's going to write into the check_database.log filename.

`filename` is the SQL filename containing SQL statements that defined the correct database structure. It can include database name too by `USE` statement.

More datails in the file usage.md.



## License

check-mysql-db-structure (c) 2022 Giovanni Venturi and contributors

SPDX-License-Identifier: GPL-3.0


