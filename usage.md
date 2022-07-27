## USAGE

How to use this tool to compare two databases?
Suppose you have local installation of MySQL.

Install a database as the one into the file example_db.sql:
mysql -u root < example_db.sql

After that, you will have example_db as a new local database.
Is this correct? You need a `tmp_example_db` that is the correct and wanted database.
Just one thing.
The reference database, the one that is correct. Need to add a "tmp_" in front of the name of the installed database to check.
This because the Python tool will create the database to check with the local database, so it cannot have the same name.
This is a convention used by this script:

1. I have a local database `example_db` I'm not sure it's correct.
2. I have a reference database I know it's correct and it has `tmp_` in front of the name.
3. You need MySQLdb python package installed: `pip3 install MySQLdb` or use directly the one from you Linux distro.

## TO GET HELP
`python check-mysql-db.py -h`

OR

`python check-mysql-db.py --help`

And you get:
```
./check-mysql-db.py --dbname=database_name --filename=sql_filename [--user=database_user --password=database_password  --debug]

OR

./check-mysql-db.py -n database_name -f sql_filename [-u database_user -p database_password -d]
```

`user` is optional. If you don't assign it, it will be user `root`.
`password` is optional. If you have a database without password you don't need to specify it.
`debug` is optional. If you specify it, you'll get the list of the parameters the app is using.


## TO GET THE VERSION NUMBER
`python check-mysql-db.py -v`

OR

`python check-mysql-db.py --version`

And you get:
`check_mysql_db v0.1`


## HERE YOU ARE AN EXAMPLE
```
python check-mysql-db.py -n example_db -f correct_example_db.sql -u root -d
*** Parameters I got:
database user: root
database password: None
database name: example_db
SQL filename: correct_example_db.sql
temporary database name: tmp_example_db

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
