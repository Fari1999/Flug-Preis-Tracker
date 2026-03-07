import requests
import psycopg2
import os
from datetime import date, timedelta

DATABASE_URL = os.environ["DATABASE_URL"]

conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()


DATABASE_URL = os.environ["DATABASE_URL"]

START_DATE = date(2026, 6, 1)     # Startdatum der Flüge die wir abfragen wollen
END_DATE   = date(2026, 8, 31)    # Enddatum der Flüge

ORIGIN = "NRN"                    # Startflughafen: Düsseldorf Weeze
DESTINATIONS = ["NDR", "OUD"]     # Ziel-Flughäfen: Nador und Oujda

DB_NAME = "flight_prices.db"      # Name der SQLite Datenbankdatei

# URL der Flugpreis API von Ryanair
url = "https://services-api.ryanair.com/farfnd/3/oneWayFares"


# Tabelle erstellen falls sie noch nicht existiert
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


today = str(date.today())         # heutiges Datum speichern (wann wir die Daten sammeln)

current = START_DATE              # Variable current startet beim Startdatum


# -------- DATEN SAMMELN --------

# Schleife läuft über jeden Tag zwischen Start und Enddatum
while current <= END_DATE:

    # Schleife läuft über alle Ziele (Nador und Oujda)
    for DEST in DESTINATIONS:

        # Parameter für die API Anfrage
        params = {
            "departureAirportIataCode": ORIGIN,        # Startflughafen
            "arrivalAirportIataCode": DEST,            # Ziel
            "outboundDepartureDateFrom": str(current), # Flugdatum von
            "outboundDepartureDateTo": str(current),   # Flugdatum bis
            "currency": "EUR"                          # Währung
        }

        try:
            # Anfrage an die API senden
            r = requests.get(url, params=params, timeout=10)

            # Antwort der API als JSON umwandeln
            data = r.json()

            # Prüfen ob Flüge gefunden wurden
            if data["fares"]:

                # Durch alle gefundenen Flüge iterieren
                for flight in data["fares"]:

                    # Preis aus der JSON Struktur lesen
                    price = flight["outbound"]["price"]["value"]

                    # Flugdatum auslesen
                    flight_date = flight["outbound"]["departureDate"]

                    # Datensatz in Datenbank speichern
                    cur.execute("""
                    INSERT INTO flight_prices
                    (origin, destination, flight_date, price, check_date)
                    VALUES (?, ?, ?, ?, ?)
                    """, (ORIGIN, DEST, flight_date, price, today))

                    # Ausgabe im Terminal
                    print(f"{flight_date} {ORIGIN}->{DEST} : {price} €")

            else:
                # Wenn kein Flug gefunden wurde
                print(f"{current} {ORIGIN}->{DEST} : kein Flug")

        except Exception as e:
            # Fehler abfangen (z.B. Netzwerkproblem)
            print("Fehler:", e)

    # Einen Tag zum aktuellen Datum hinzufügen
    current += timedelta(days=1)


# Änderungen in der Datenbank speichern
conn.commit()

# Datenbankverbindung schließen
conn.close()


print("Data inserted")
