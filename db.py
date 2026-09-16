import mysql.connector

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Suba_pr0",
    database="farmers_market",
    buffered=True
)

print("Database Connected Successfully")