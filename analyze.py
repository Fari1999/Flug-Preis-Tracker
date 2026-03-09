import psycopg2
import json
import os

DATABASE_URL = os.environ.get("DATABASE_URL")

conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

# billigster Flug insgesamt
cur.execute("""
SELECT * 
FROM flight_prices
ORDER BY price ASC
LIMIT 1
""")

cheapest_overall = cur.fetchone()
columns = [desc[0] for desc in cur.description]
cheapest_overall = dict(zip(columns, cheapest_overall))

# aktuellstes Datum
cur.execute("""
SELECT MAX(scrape_date)
FROM flight_prices
""")

latest_date = cur.fetchone()[0]

# billigster Flug vom aktuellsten Datum
cur.execute("""
SELECT *
FROM flight_prices
WHERE scrape_date = %s
ORDER BY price ASC
LIMIT 1
""", (latest_date,))

cheapest_latest = dict(zip(columns, cur.fetchone()))

# Top 10 vom aktuellsten Datum
cur.execute("""
SELECT *
FROM flight_prices
WHERE scrape_date = %s
ORDER BY price ASC
LIMIT 10
""", (latest_date,))

rows = cur.fetchall()
top10 = [dict(zip(columns, r)) for r in rows]

# Graph Daten (letzte 3 Monate)
cur.execute("""
SELECT flight_date, price
FROM flight_prices
WHERE scrape_date >= NOW() - INTERVAL '3 months'
ORDER BY flight_date
""")

rows = cur.fetchall()

graph_dates = [str(r[0]) for r in rows]
graph_prices = [r[1] for r in rows]

data = {
    "cheapest_overall": cheapest_overall,
    "cheapest_latest": cheapest_latest,
    "top10_latest": top10,
    "graph": {
        "dates": graph_dates,
        "prices": graph_prices
    }
}

os.makedirs("website", exist_ok=True)

with open("cheapest_flight.json", "w") as f:
    json.dump(data, f)

cur.close()
conn.close()
