import mysql.connector

mydb = mysql.connector.connect(
    host = "localhost",
    user = "root",
    password = "bancod2830/*",
)

my_cursor = mydb.cursor()

#my_cursor.execute("CREATE DATABASE usuarios")

my_cursor.execute("SHOW DATABASES")

for db in my_cursor:
    print(db)