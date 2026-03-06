import requests
import psycopg2
import os
from datetime import datetime

DATABASE_URL = os.environ["DATABASE_URL"]

conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

# Beispiel Daten speichern
cur.execute("""
CREATE TABLE IF NOT EXISTS flight_prices (
    id SERIAL PRIMARY KEY,
    origin TEXT,
    destination TEXT,
    price INT,
    collected_at TIMESTAMP
)
""")

cur.execute("""
INSERT INTO flight_prices
(origin, destination, price, collected_at)
VALUES (%s,%s,%s,%s)
""", ("NRN", "NDR", 50, datetime.now()))

conn.commit()

cur.close()
conn.close()

print("Data inserted")
