import psycopg2
import json
import os
import smtplib

from datetime import date, timedelta
from email.mime.text import MIMEText

# -----------------------------
# Verbindung zur Neon/Postgres DB, Secrets laden
# -----------------------------
DATABASE_URL = os.environ.get("DATABASE_URL")

EMAIL_USER = os.environ.get("EMAIL_USER")
EMAIL_PASS = os.environ.get("EMAIL_PASS")
#ALERT_EMAIL = os.environ.get("ALERT_EMAIL")
ALERT_EMAIL = os.environ.get("farfifa@hotmail.com")


if not DATABASE_URL:
    raise ValueError("DATABASE_URL nicht gesetzt")

# --------------------------------------------------
#  Email Funktion
# sendet eine Email wenn eine Bedingung erfüllt ist
# --------------------------------------------------

def send_email(subject, message):

    # Falls Email Secrets fehlen → keine Email
    if not EMAIL_USER or not EMAIL_PASS or not ALERT_EMAIL:
        print("Email Secrets fehlen")
        return

    msg = MIMEText(message)

    msg["Subject"] = subject
    msg["From"] = EMAIL_USER
    msg["To"] = ALERT_EMAIL

    try:

        server = smtplib.SMTP("smtp.gmail.com", 587)

        server.starttls()

        server.login(EMAIL_USER, EMAIL_PASS)

        server.sendmail(
            EMAIL_USER,
            ALERT_EMAIL,
            msg.as_string()
        )

        server.quit()

        print("✅ Email gesendet")

    except Exception as e:

        print("Email Fehler:", e)


# --------------------------------------------------
#   Verbindung zur Datenbank
# --------------------------------------------------

conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

# -----------------------------
# Spaltennamen der Tabelle holen
# -----------------------------
cur.execute("""
SELECT *
FROM flight_prices
LIMIT 1
""")

columns = [desc[0] for desc in cur.description]

# --------------------------------------------------
#  Zeitraum für nächsten Monat berechnen
# Beispiel:
# Heute: 16 März
# → prüft nur Flüge von 1 April bis 30 April
# --------------------------------------------------

today = date.today()

# erster Tag vom nächsten Monat
next_month_start = (today.replace(day=1) + timedelta(days=32)).replace(day=1)

# letzter Tag vom nächsten Monat
next_month_end = (next_month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)

# --------------------------------------------------
#  Billigster Hinflug im nächsten Monat
# --------------------------------------------------

cur.execute("""
SELECT *
FROM flight_prices
WHERE origin = 'NRN'
AND flight_date BETWEEN %s AND %s
ORDER BY price ASC
LIMIT 1
""", (next_month_start, next_month_end))

row = cur.fetchone()

cheapest_outbound = None

if row:

    cheapest_outbound = dict(zip(columns, row))

    cheapest_outbound["flight_date"] = cheapest_outbound["flight_date"].isoformat()
    cheapest_outbound["check_date"] = cheapest_outbound["check_date"].isoformat()

    # --------------------------------------------------
    # Email senden wenn Hinflug unter 30€
    # --------------------------------------------------

    if cheapest_outbound["price"] < 50:

        message = f"""
Cheap Flight Alert!

Route: {cheapest_outbound['origin']} → {cheapest_outbound['destination']}
Date: {cheapest_outbound['flight_date']}
Price: €{cheapest_outbound['price']}
"""

        send_email(
            "Cheap Flight Found!",
            message
        )

# --------------------------------------------------
#  Billigste komplette Reise
# Hinflug + Rückflug innerhalb 7 Tage
# nur im nächsten Monat
# --------------------------------------------------

cur.execute("""
SELECT
    o.flight_date,
    r.flight_date,
    o.price + r.price as total
FROM flight_prices o
JOIN flight_prices r
    ON r.origin = o.destination
    AND r.destination = o.origin
    AND r.flight_date BETWEEN o.flight_date
    AND o.flight_date + INTERVAL '7 days'
WHERE o.flight_date BETWEEN %s AND %s
ORDER BY total ASC
LIMIT 1
""", (next_month_start, next_month_end))

trip = cur.fetchone()

if trip:

    outbound_date = trip[0]
    return_date = trip[1]
    total_price = trip[2]

    # --------------------------------------------------
    # Email wenn komplette Reise unter 50€
    # --------------------------------------------------

    if total_price < 100:

        message = f"""
Cheap Trip Found!

Outbound: {outbound_date}
Return: {return_date}

Total Price: €{total_price}
"""

        send_email(
            "Cheap Trip Alert!",
            message
        )


# -----------------------------
#  Billigster Hinflug (NRN → *)
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
#  Billigster Rückflug (* → NRN)
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
# Top 10 billigste Hinflüge
# -----------------------------
cur.execute("""
SELECT *
FROM flight_prices
WHERE origin='NRN'
ORDER BY price ASC
LIMIT 10
""")

rows = cur.fetchall()

top10_outbound = []

for r in rows:
    d = dict(zip(columns, r))
    d["flight_date"] = d["flight_date"].isoformat()
    d["check_date"] = d["check_date"].isoformat()
    top10_outbound.append(d)

# -----------------------------
# Top 10 billigste Rückflüge
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
#  Graph Daten erstellen
# Jeder Graph zeigt Preise über 1 Jahr
# -----------------------------

# -----------------------------
# Graph Daten erstellen
# -----------------------------

def build_graph(origin, destination):

    cur.execute("""
    SELECT flight_date, price
    FROM flight_prices
    WHERE origin = %s AND destination = %s
    ORDER BY flight_date
    """, (origin, destination))

    rows = cur.fetchall()

    return {
        "dates": [r[0].isoformat() for r in rows],
        "prices": [r[1] for r in rows]
    }


# Vier Graphen erzeugen

graph_nrn_ndr = build_graph("NRN", "NDR")
graph_nrn_oud = build_graph("NRN", "OUD")
graph_ndr_nrn = build_graph("NDR", "NRN")
graph_oud_nrn = build_graph("OUD", "NRN")
# -----------------------------
#  JSON Struktur erstellen
# -----------------------------
data = {

"cheapest_outbound":cheapest_outbound,
"cheapest_return":cheapest_return,

"top10_outbound":top10_outbound,   # NEU
"top10_returns":top10_returns,
    
"graphs":{
"nrn_ndr":graph_nrn_ndr,
"nrn_oud":graph_nrn_oud,
"ndr_nrn":graph_ndr_nrn,
"oud_nrn":graph_oud_nrn
}

}

# -----------------------------
#  JSON speichern
# -----------------------------
with open("cheapest_flight.json","w") as f:
    json.dump(data,f,indent=2)

print("✅ cheapest_flight.json erfolgreich erstellt")

cur.close()
conn.close()
