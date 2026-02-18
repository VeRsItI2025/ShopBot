import sqlite3

conn = sqlite3.connect("shop.db")
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

cursor.execute("SELECT * FROM products")
rows = cursor.fetchall()

for row in rows:
    print(dict(row))