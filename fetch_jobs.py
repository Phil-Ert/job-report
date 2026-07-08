import requests
from datetime import datetime

# 1. HIER DEINE ADZUNA KEYS EINTRAGEN
ADZUNA_APP_ID = "689035fc"
ADZUNA_APP_KEY = "669316466ef294ab8acf4e7d01b8faf0"

# 2. Deine Suchkonfiguration
SUCHBEGRIFFE = [
    "Stadtplaner", 
    "Stadtentwickler", 
    "Geograph", 
    "Wissenschaftlicher Mitarbeiter", 
    "Business Development Manager", 
    "Consultant"
]
LAND = "de"                          # "de" steht für Deutschland
JOBS_SEIT_TAGEN = 7                  # Für den wöchentlichen Report

gesehene_urls = set()
job_elements_html = ""
job_count = 0

print("Starte API-Abfrage bei Adzuna...")

for begriff in SUCHBEGRIFFE:
    print(f"Suche nach: '{begriff}'...")
    
    # Adzuna API-URL für das jeweilige Land und den Begriff
    # max_days_old filtert direkt Jobs, die älter als X Tage sind
    url = f"https://api.adzuna.com/v1/api/jobs/{LAND}/search/1"
    
    params = {
        "app_id": ADZUNA_APP_ID,
        "app_key": ADZUNA_APP_KEY,
        "what": begriff,
        "max_days_old": JOBS_SEIT_TAGEN,
        "results_per_page": 20
    }

    try:
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            results = data.get("results", [])
            
            for job in results:
                # Eindeutige URL zur Identifikation nutzen
                redirect_url = job.get("redirect_url", "")
                
                if redirect_url in gesehene_urls:
                    continue
                
                gesehene_urls.add(redirect_url)
                job_count += 1
                
                titel = job.get("title", "Kein Titel angegeben")
                
                # Firma auslesen
                company_info = job.get("company", {})
                arbeitgeber = company_info.get("display_name", "Anonym")
                
                # Ort auslesen
                location_info = job.get("location", {})
                ort = ", ".join(location_info.get("area", [])) or "Nicht angegeben"
                
                # Datum formatieren (Adzuna liefert z.B. 2026-07-06T12:00:00Z)
                created_raw = job.get("created", "")
                if created_raw:
                    try:
                        datum_obj = datetime.strptime(created_raw[:10], "%Y-%m-%d")
                        datum_formatiert = datum_obj.strftime("%d.%m.%Y")
                    except ValueError:
                        datum_formatiert = created_raw[:10]
                else:
                    datum_formatiert = "Neu"

                # HTML-Karte generieren
                job_elements_html += f"""
                <div class="job-card">
                    <span class="badge">{begriff}</span>
                    <h3>{titel}</h3>
                    <p class="company">🏢 <strong>{arbeitgeber}</strong></p>
                    <p class="meta">📍 Ort: {ort} | 📅 Gefunden am: {datum_formatiert}</p>
                    <a href="{redirect_url}" target="_blank">Zum Stellenangebot ↗</a>
                </div>
                """
        else:
            print(f"  [Fehler] Status-Code {response.status_code} für '{begriff}'")
            print(response.text)

    except Exception as e:
        print(f"  [Fehler] Ausnahme bei '{begriff}': {e}")

# Das finale HTML Template
html_template = f"""<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <title>Mein Wöchentlicher Job Report</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #f4f6f9; color: #333; max-width: 800px; margin: 40px auto; padding: 20px; }}
        h1 {{ color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }}
        .job-card {{ background: white; padding: 20px; margin-bottom: 15px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); border-left: 5px solid #3498db; position: relative; }}
        h3 {{ margin-top: 10px; font-size: 1.25rem; color: #2c3e50; }}
        .company {{ margin: 5px 0; color: #555; }}
        .meta {{ font-size: 0.85rem; color: #777; margin-bottom: 15px; }}
        .badge {{ background: #e2e8f0; color: #4a5568; padding: 3px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: bold; text-transform: uppercase; }}
        a {{ display: inline-block; background: #3498db; color: white; padding: 8px 15px; text-decoration: none; font-weight: bold; border-radius: 4px; font-size: 0.9rem; }}
        a:hover {{ background: #2980b9; }}
    </style>
</head>
<body>
    <h1>📋 Mein wöchentlicher Job-Report (via Adzuna)</h1>
    <p>Land: <strong>Deutschland</strong></p>
    <p>In den letzten {JOBS_SEIT_TAGEN} Tagen wurden insgesamt <strong>{job_count}</strong> eindeutige Angebote gefunden.</p>
    {job_elements_html if job_count > 0 else "<p>Keine neuen Jobs für deine Suchbegriffe gefunden.</p>"}
</body>
</html>"""

with open("job_report.html", "w", encoding="utf-8") as f:
    f.write(html_template)

print(f"\nFertig! {job_count} Jobs wurden erfolgreich in 'job_report.html' geschrieben.")
