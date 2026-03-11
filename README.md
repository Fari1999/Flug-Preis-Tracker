# Flug-Preis-Tracker
```
│
├── index.html
│   # Hauptseite der Website
│   # Lädt cheapest_flight.json und zeigt:
│   # - billigsten Flug
│   # - billigsten aktuellen Flug
│   # - Top 10 billigste Flüge
│   # - Preisdiagramm (Chart.js)
│
├── cheapest_flight.json
│   # Wird automatisch von analyze.py erzeugt
│   # Enthält:
│   # - billigster Flug aller Zeiten
│   # - billigster Flug des neuesten Scans
│   # - Top 10 billigste Flüge
│   # - Daten für das Preisdiagramm
│
├── analyze.py
│   # Python Analyse Script
│   # Verbindet sich mit der PostgreSQL Datenbank
│   # Holt Flugdaten aus der Tabelle flight_prices
│   # Berechnet:
│   #   - billigster Flug insgesamt
│   #   - billigster Flug vom neuesten Scan
│   #   - Top 10 billigste Flüge
│   #   - Preisdaten für das Diagramm
│   # Speichert das Ergebnis in cheapest_flight.json
│
├── scraper.py
│   # Scraper Script
│   # Holt Flugpreise von der Airline Website
│   # Speichert sie in der PostgreSQL Datenbank
│   # Tabelle: flight_prices
│
├── create_alert.py
│   # API Script für Preis Alerts
│   # Wird von der Website aufgerufen
│   # Speichert:
│   # - email
│   # - flugdatum
│   # - maximalpreis
│   # in der Tabelle price_alerts
│
├── send_alerts.py
│   # Prüft alle gespeicherten Alerts
│   # Wenn ein Flugpreis unter dem gewünschten Preis liegt:
│   # -> wird automatisch eine Email gesendet
│
├── requirements.txt
│   # Python Abhängigkeiten
│   # z.B.
│   # psycopg2-binary
│   # python-dotenv
│
├── .env
│   # Lokale Umgebungsvariablen (nicht in GitHub)
│   # z.B.
│   # DATABASE_URL
│   # EMAIL_USER
│   # EMAIL_PASSWORD
│
├── .gitignore
│   # Verhindert das Hochladen sensibler Dateien
│   # z.B.
│   # .env
│   # __pycache__
│
└── workflows
        │
        └── update.yml
            # GitHub Actions Workflow
            # Läuft automatisch jede Stunde
            # Schritte:
            # 1. Repository klonen
            # 2. Python installieren
            # 3. Dependencies installieren
            # 4. analyze.py ausführen
            # 5. cheapest_flight.json aktualisieren
            # 6. Änderungen committen und pushen
```
