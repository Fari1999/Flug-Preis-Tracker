import os
import psycopg2
import json

# Database URL aus GitHub Secrets oder Environment
DATABASE_URL = os.environ["DATABASE_URL"]

# Verbindung zur Neon Datenbank
conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

# günstigsten Flug finden
cur.execute("""
SELECT origin, destination, flight_date, price
FROM flight_prices
ORDER BY price ASC
LIMIT 1
""")

result = cur.fetchone()

if result:

    data = {
        "origin": result[0],
        "destination": result[1],
        "date": str(result[2]),
        "price": result[3]
    }

    # JSON Datei speichern
    with open("cheapest_flight.json", "w") as f:
        json.dump(data, f, indent=4)

    print("Cheapest flight saved")

else:
    print("No data found")

cur.close()
conn.close()
