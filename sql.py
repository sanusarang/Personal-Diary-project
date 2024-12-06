import mysql.connector

connection= mysql.connector.connect(host="localhost", user="root", password="", db="project")

if connection.is_connected():
    print("Connected Successfully")
else:
    print("Failed to Connect")

#db operations
connection.close()