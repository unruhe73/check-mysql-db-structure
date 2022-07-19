USAGE
How to use this tool to compare two databases?
Suppose you have local installation of MySQL.

Install a database as the one into the file example_db.sql:
mysql -u root < example_db.sql

After that, you will have example_db as a new local database.
Is this correct? You need a "tmp_example_db" that is the correct and wanted database.
Just one thing.
The reference database, the one that is correct. Need to add a "tmp_" in front of the name of the installed database to check.
This because the Python tool will create the database to check with the local database, so it cannot have the same name.
This is a convention used by this script:

1. I have a local database "example_db" I'm not sure it's correct.
2. I have a reference database I know it's correct and it has "tmp_" in front of the name.

After that I can execute:

./check-mysql-db.py example_db correct_example_db.sql

Or:

python3 check-mysql-db.py example_db correct_example_db.sql

So you will see:

version 0.1
dbname: example_db
tmpDB: tmp_example_db
dbpath: correct_example_db.sql
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
