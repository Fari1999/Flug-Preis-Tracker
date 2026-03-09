import psycopg2
import json
import os

# -----------------------------
# Verbindung zur Neon/Postgres DB
# -----------------------------
DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL nicht gesetzt")

conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

# -----------------------------
# 1️⃣ Billigster Flug insgesamt
# -----------------------------
cur.execute("""
SELECT *
FROM flight_prices
ORDER BY price ASC
LIMIT 1
""")
cheapest_overall_row = cur.fetchone()
columns = [desc[0] for desc in cur.description]

cheapest_overall = None
if cheapest_overall_row:
    cheapest_overall = dict(zip(columns, cheapest_overall_row))
    # Datum in String konvertieren
    cheapest_overall["flight_date"] = cheapest_overall["flight_date"].isoformat()
    cheapest_overall["check_date"] = cheapest_overall["check_date"].isoformat()

# -----------------------------
# 2️⃣ Aktuellstes Check-Datum
# -----------------------------
cur.execute("SELECT MAX(check_date) FROM flight_prices")
latest_date = cur.fetchone()[0]

if latest_date is None:
    raise ValueError("Keine Daten in der Tabelle vorhanden")

# -----------------------------
# 3️⃣ Billigster Flug vom aktuellsten Datum
# -----------------------------
cur.execute("""
SELECT *
FROM flight_prices
WHERE check_date = %s
ORDER BY price ASC
LIMIT 1
""", (latest_date,))
cheapest_latest_row = cur.fetchone()
cheapest_latest = dict(zip(columns, cheapest_latest_row))
cheapest_latest["flight_date"] = cheapest_latest["flight_date"].isoformat()
cheapest_latest["check_date"] = cheapest_latest["check_date"].isoformat()

# -----------------------------
# 4️⃣ Top 10 Preise vom aktuellsten Datum
# -----------------------------
cur.execute("""
SELECT *
FROM flight_prices
WHERE check_date = %s
ORDER BY price ASC
LIMIT 10
""", (latest_date,))
rows = cur.fetchall()
top10_latest = []
for r in rows:
    d = dict(zip(columns, r))
    d["flight_date"] = d["flight_date"].isoformat()
    d["check_date"] = d["check_date"].isoformat()
    top10_latest.append(d)

# -----------------------------
# 5️⃣ Graph Daten vom aktuellsten Datum
# -----------------------------
cur.execute("""
SELECT flight_date, price
FROM flight_prices
WHERE check_date = %s
ORDER BY flight_date ASC
""", (latest_date,))
graph_rows = cur.fetchall()

graph = {
    "dates": [r[0].isoformat() for r in graph_rows],
    "prices": [r[1] for r in graph_rows]
}

# -----------------------------
# 6️⃣ JSON erstellen
# -----------------------------
data = {
    "cheapest_overall": cheapest_overall,
    "cheapest_latest": cheapest_latest,
    "top10_latest": top10_latest,
    "graph": graph
}

# -----------------------------
# 7️⃣ JSON speichern
# -----------------------------
with open("cheapest_flight.json", "w") as f:
     json.dump(data, f, indent=2, default=str)

print("✅ cheapest_flight.json erfolgreich erstellt")

cur.close()
conn.close()
