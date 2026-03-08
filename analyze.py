import os
import psycopg2
import json

DATABASE_URL = os.environ.get("DATABASE_URL")

if not DATABASE_URL:
    print("DATABASE_URL not found")
    exit()

conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

cur.execute("""
SELECT *
FROM flight_prices
ORDER BY price ASC
LIMIT 1
""")

row = cur.fetchone()

if row is None:
    print("No data in database")
    exit()

columns = [desc[0] for desc in cur.description]

data = dict(zip(columns, row))

with open("cheapest_flight.json", "w") as f:
    json.dump(data, f, indent=4, default=str)

print("cheapest_flight.json created successfully")

cur.close()
conn.close()
