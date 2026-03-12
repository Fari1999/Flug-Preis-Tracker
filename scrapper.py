import requests
import psycopg2
import os
from datetime import date, datetime, timedelta

DATABASE_URL = os.environ["DATABASE_URL"]

conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

# Tabelle erstellen falls nicht vorhanden
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

# Alte Daten löschen
cur.execute("DELETE FROM flight_prices")
conn.commit()

# Zeitraum: heute bis 1 Jahr
START_DATE = datetime.today()
END_DATE = START_DATE + timedelta(days=365)

# Routen (Hinflug + Rückflug)
routes = [
    ("NRN", "NDR"),
    ("NDR", "NRN"),
    ("NRN", "OUD"),
    ("OUD", "NRN")
]

url = "https://services-api.ryanair.com/farfnd/3/oneWayFares"

today = date.today()

current = START_DATE

while current <= END_DATE:

    flight_date = current.strftime("%Y-%m-%d")

    for origin, destination in routes:

        print("Scraping:", origin, "→", destination, flight_date)

        params = {
            "departureAirportIataCode": origin,
            "arrivalAirportIataCode": destination,
            "outboundDepartureDateFrom": flight_date,
            "outboundDepartureDateTo": flight_date,
            "currency": "EUR"
        }

        try:

            r = requests.get(url, params=params, timeout=10)
            data = r.json()

            if "fares" in data and data["fares"]:

                for flight in data["fares"]:

                    price = flight["outbound"]["price"]["value"]
                    f_date = flight["outbound"]["departureDate"]

                    cur.execute(
                        """
                        INSERT INTO flight_prices
                        (origin, destination, flight_date, price, check_date)
                        VALUES (%s, %s, %s, %s, %s)
                        """,
                        (origin, destination, f_date, price, today)
                    )

                    print(f"{f_date} {origin}->{destination} : {price} €")

            else:
                print(f"{flight_date} {origin}->{destination} : kein Flug")

        except Exception as e:
            print("Fehler:", e)

    current += timedelta(days=1)

conn.commit()
cur.close()
conn.close()

print("✅ Scraping abgeschlossen")
