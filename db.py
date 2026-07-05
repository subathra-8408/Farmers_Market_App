import mysql.connector

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Suba_pr0",
    database="farmers_market"
)

print("Database Connected Successfully")