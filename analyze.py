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
    cheapest_overall["flight_date"] = cheapest_overall["flight_date"].isoformat()
    cheapest_overall["check_date"] = cheapest_overall["check_date"].isoformat()

# -----------------------------
# 2️⃣ Billigster Hinflug (NRN → *)
# -----------------------------
cur.execute("""
SELECT *
FROM flight_prices
WHERE origin='NRN'
ORDER BY price ASC
LIMIT 1
""")

row = cur.fetchone()

cheapest_outbound = dict(zip(columns, row))
cheapest_outbound["flight_date"] = cheapest_outbound["flight_date"].isoformat()
cheapest_outbound["check_date"] = cheapest_outbound["check_date"].isoformat()

# -----------------------------
# 3️⃣ Billigster Rückflug (* → NRN)
# -----------------------------
cur.execute("""
SELECT *
FROM flight_prices
WHERE destination='NRN'
ORDER BY price ASC
LIMIT 1
""")

row = cur.fetchone()

cheapest_return = dict(zip(columns, row))
cheapest_return["flight_date"] = cheapest_return["flight_date"].isoformat()
cheapest_return["check_date"] = cheapest_return["check_date"].isoformat()

# -----------------------------
# 4️⃣ Top 10 billigste Rückflüge
# -----------------------------
cur.execute("""
SELECT *
FROM flight_prices
WHERE destination='NRN'
ORDER BY price ASC
LIMIT 10
""")

rows = cur.fetchall()

top10_returns = []

for r in rows:
    d = dict(zip(columns, r))
    d["flight_date"] = d["flight_date"].isoformat()
    d["check_date"] = d["check_date"].isoformat()
    top10_returns.append(d)

# -----------------------------
# 5️⃣ Graph Daten erstellen
# Jeder Graph zeigt Preise über 1 Jahr
# -----------------------------

def build_graph(origin, destination):

    cur.execute("""
    SELECT flight_date, price
    FROM flight_prices
    WHERE origin=%s AND destination=%s
    ORDER BY flight_date
    """,(origin,destination))

    rows = cur.fetchall()

    return {
        "dates":[r[0].isoformat() for r in rows],
        "prices":[r[1] for r in rows]
    }

# Vier Graphen erzeugen

graph_nrn_ndr = build_graph("NRN","NDR")
graph_nrn_oud = build_graph("NRN","OUD")
graph_ndr_nrn = build_graph("NDR","NRN")
graph_oud_nrn = build_graph("OUD","NRN")

# -----------------------------
# 6️⃣ JSON Struktur erstellen
# -----------------------------
data = {

"cheapest_overall":cheapest_overall,
"cheapest_outbound":cheapest_outbound,
"cheapest_return":cheapest_return,

"top10_returns":top10_returns,

"graphs":{
"nrn_ndr":graph_nrn_ndr,
"nrn_oud":graph_nrn_oud,
"ndr_nrn":graph_ndr_nrn,
"oud_nrn":graph_oud_nrn
}

}

# -----------------------------
# 7️⃣ JSON speichern
# -----------------------------
with open("cheapest_flight.json","w") as f:
    json.dump(data,f,indent=2)

print("✅ cheapest_flight.json erfolgreich erstellt")

cur.close()
conn.close()
