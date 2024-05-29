## USAGE

How to use this tool to compare two databases?
Suppose you have local installation of MySQL.
If you use Manjaro Linux and you have yet to install MariaDB give look at [here](https://www.linuxcapable.com/how-to-install-mariadb-on-manjaro-21-linux/).
Of course, I suggest to assign a password to root user.

Install a database as the one into the file example_db.sql:
mysql -u root -p < example_db.sql

After that, you have example_db as a new local database.

The `main.py` script uses the python class `CheckMySQLDB` defined in the file `check_mysql_db.py`.

These are the pre-conditions for the script to work:

1. You have a local database `example_db` stored into the server and I'm not sure it's correct.
2. You have an SQL file reference for the database and I know it's correct (in the example is `correct_example_db.sql` but you can name it as you wish).
3. You need mysqlclient python package installed: `pip install mysqlclient` or use directly the one from you Linux distro.

`python-mysqlclient` is available on [github.com here](https://github.com/PyMySQL/mysqlclient).

If into the `correct_example_db.sql` SQL file you have the `USE` SQL instruction, the python script can detect on its own the database name to compare with, if not, you need to specify it
with the '-n' parameter on the command line, or using '--dbname=' one.

## How to get the help menu
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
                        log filename where you get output results (default is check_database.log)
  -d, --debug           write as much information as possible
  -v, --version         print the version of the script
```

`server` is the host where you have your MySQL/MariaDB server operative. It's optional. If you don't assign it, it will be considered as `localhost`.

`user` is the database username and is optional. If you don't assign it, it will be replace by a `root` user as default.

`password` is the database password for the specified database user. It is an optional value. If you have a database without a password you don't need to specify it.

`dbname` is the database name, but it could be detected directly from the SQL_FILENAME into filename option if this is not present.

`debug` is optional and as default value is assigned to `False`. If you specify it as `True`, you'll get some debug output as the list of the parameters the class is using to compare the two databases.

`write-log-to` is optional. If you specify it than the outupt will be redirected to the LOG_FILENAME file.

`filename` is the SQL filename containing SQL statements that defined the correct database structure. It can include database name too by `USE` statement.


## How to get the version number
`python main.py -v`

OR

`python main.py --version`

And you get:
`check_mysql_db v0.2` or higher.


## HERE YOU ARE AN EXAMPLE: #1
Suppose I have the `USE` SQL instruction into the `correct_example_db.sql` SQL file. I don't need to specify the database name to verify.

```
python main.py -f correct_example_db.sql -u root -d
*** Parameters I got:
database user: root
database password: None
database name: example_db
SQL filename: correct_example_db.sql
temporary database name: tmp_example_db
temporary database filename: tmp_example_db.sql

*** in the first place the number of tables is correct.
    +++ counted 1 tables
********** table 'example_table' is NOT the same!
'field01' default value has not the same default value: '1' vs the wanted '0'
'field02' has the max number of characters different: 50 vs the wanted 20
'field04' has different type
'field04' default value has not the same default value: '''' vs the wanted '7'
'field07' has different type
'field07' has a different nullable
'field07' default value has not the same default value: '0' vs the wanted ''''
'field08' default value has not the same default value: 'NULL' vs the wanted '0'
field 'field09' is missing
in the database to verify, field 'field06' seems to be extra (you could remove it)...

1 table has a different structure!
```

## HERE YOU ARE AN EXAMPLE: #2
Suppose I don't have the `USE` SQL instruction into the `correct_example_db.sql` SQL file. I need to specify the database name to verify.

```
python main.py -f correct_example_db.sql -n example_db -u root -d
*** Parameters I got:
database user: root
database password: None
database name: example_db
SQL filename: correct_example_db.sql
temporary database name: tmp_example_db
temporary database filename: tmp_example_db.sql

*** in the first place the number of tables is correct.
    +++ counted 1 tables
********** table 'example_table' is NOT the same!
'field01' default value has not the same default value: '1' vs the wanted '0'
'field02' has the max number of characters different: 50 vs the wanted 20
'field04' has different type
'field04' default value has not the same default value: '''' vs the wanted '7'
'field07' has different type
'field07' has a different nullable
'field07' default value has not the same default value: '0' vs the wanted ''''
'field08' default value has not the same default value: 'NULL' vs the wanted '0'
field 'field09' is missing
in the database to verify, field 'field06' seems to be extra (you could remove it)...

1 table has a different structure!
```
