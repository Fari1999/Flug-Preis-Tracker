import requests
import psycopg2
import os
from datetime import date, timedelta

DATABASE_URL = os.environ["DATABASE_URL"]

conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

# Alte Daten löschen
cur.execute("DELETE FROM flight_prices")
conn.commit()

START_DATE = date(2026, 6, 1)
END_DATE = date(2026, 8, 31)

ORIGIN = "NRN"
DESTINATIONS = ["NDR", "OUD"]

url = "https://services-api.ryanair.com/farfnd/3/oneWayFares"

cur.execute("""
CREATE TABLE IF NOT EXISTS flight_prices (
    id SERIAL PRIMARY KEY,
    origin TEXT,
    destination TEXT,
    flight_date DATE,
    price REAL,
    check_date DATE
)
""")

today = date.today()

current = START_DATE

while current <= END_DATE:

    for DEST in DESTINATIONS:

        params = {
            "departureAirportIataCode": ORIGIN,
            "arrivalAirportIataCode": DEST,
            "outboundDepartureDateFrom": str(current),
            "outboundDepartureDateTo": str(current),
            "currency": "EUR"
        }

        try:

            r = requests.get(url, params=params, timeout=10)
            data = r.json()

            if data["fares"]:

                for flight in data["fares"]:

                    price = flight["outbound"]["price"]["value"]
                    flight_date = flight["outbound"]["departureDate"]

                    cur.execute(
                        """
                        INSERT INTO flight_prices
                        (origin, destination, flight_date, price, check_date)
                        VALUES (%s, %s, %s, %s, %s)
                        """,
                        (ORIGIN, DEST, flight_date, price, today)
                    )

                    print(f"{flight_date} {ORIGIN}->{DEST} : {price} €")

            else:
                print(f"{current} {ORIGIN}->{DEST} : kein Flug")

        except Exception as e:
            print("Fehler:", e)

    current += timedelta(days=1)

conn.commit()
conn.close()

print("Data inserted")
