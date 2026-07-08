import os
import requests
from datetime import datetime

# 1. GEHEIMEN KEYS VON GITHUB ODER LOKAL LADEN
ADZUNA_APP_ID = os.environ.get("ADZUNA_APP_ID", "689035fc")
ADZUNA_APP_KEY = os.environ.get("ADZUNA_APP_KEY", "669316466ef294ab8acf4e7d01b8faf0")

# 2. DEINE KEYWORDS NACH BEREICHEN SORTIERT
KEYWORDS_BUSINESS = [
    '"Innovation Manager"',
    '"Strategy Consultant"',
    '"Strategic Assistant"',
    '"Business Development Manager"',
    '"Change Manager"',
    '"Transformation Lead"',
    '"Employee Experience Manager"',
    '"Organizational Development"',
    '"Senior Project Manager"',
    '"Product Owner"',
    '"Agile Coach"',
    '"Agile Transformation"',
    '"Human Capital"'
]

KEYWORDS_GOVERNMENT = [
    '"Stadtplaner"',
    '"Stadtentwickler"'
]

# 3. GEOGRAFIE-FILTER (Ganz Deutschland)
ORT = "Germany" 

print(f"Starte API-Abfrage bei Adzuna für Ort: {ORT}...")
all_jobs = []
seen_job_ids = set()  # Verhindert, dass doppelte Jobs auf der Liste landen

def fetch_from_adzuna(keywords, categories, max_results):
    for keyword in keywords:
        for category in categories:
            # Adzuna API URL für Deutschland v1
            url = f"https://api.adzuna.com/v1/api/jobs/de/search/1"
            params = {
                "app_id": ADZUNA_APP_ID,
                "app_key": ADZUNA_APP_KEY,
                "results_per_page": max_results,
                "what": keyword,
                "where": ORT,
                "category": category,
                "content-type": "application/json"
            }
            try:
                response = requests.get(url, params=params)
                if response.status_code == 200:
                    data = response.json()
                    results = data.get("results", [])
                    for job in results:
                        job_id = job.get("id")
                        if job_id not in seen_job_ids:
                            seen_job_ids.add(job_id)
                            all_jobs.append(job)
                else:
                    print(f"  [Fehler] Status-Code {response.status_code} für {keyword} ({category})")
            except Exception as e:
                print(f"  [Fehler] Verbindung fehlgeschlagen für {keyword}: {e}")

# --- BEIDE BEREICHE ABFRAGEN ---
fetch_from_adzuna(KEYWORDS_BUSINESS, ["consultancy-jobs", "it-jobs", "admin-jobs"], max_results=15)
fetch_from_adzuna(KEYWORDS_GOVERNMENT, ["admin-jobs"], max_results=20)

print(f"\nFertig! {len(all_jobs)} Jobs wurden erfolgreich geladen.")

# 4. HTML-DATEI SCHREIBEN
html_content = f"""
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Wöchentlicher Job Report</title>
    <style>
        body {{ font-family: 'Helvetica Neue', Arial, sans-serif; background-color: #f4f7f6; color: #333; margin: 0; padding: 20px; }}
        .container {{ max-width: 900px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }}
        h1 {{ color: #2c3e50; border-bottom: 2px solid #ecf0f1; padding-bottom: 15px; font-size: 28px; }}
        .meta {{ color: #7f8c8d; font-size: 14px; margin-bottom: 30px; }}
        .job-card {{ padding: 20px; border: 1px solid #e2e8f0; border-radius: 6px; margin-bottom: 15px; transition: transform 0.2s; }}
        .job-card:hover {{ transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.05); border-color: #cbd5e1; }}
        .job-title {{ font-size: 18px; font-weight: bold; color: #1e3a8a; margin: 0 0 8px 0; }}
        .job-details {{ font-size: 14px; color: #475569; margin-bottom: 12px; }}
        .job-details span {{ margin-right: 15px; font-weight: 500; }}
        .job-desc {{ font-size: 14px; color: #334155; line-height: 1.5; }}
        .btn {{ display: inline-block; background-color: #2563eb; color: white; padding: 8px 16px; border-radius: 4px; text-decoration: none; font-size: 14px; font-weight: 500; margin-top: 10px; }}
        .btn:hover {{ background-color: #1d4ed8; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🔍 Dein Strategischer & Planerischer Job-Report</h1>
        <div class="meta">Aktualisiert am: {datetime.now().strftime('%d.%m.%Y um %H:%M')} Uhr | Region: Ganz Deutschland</div>
"""

if not all_jobs:
    html_content += "<p>Keine neuen Jobs für diese Filterkombination in dieser Woche gefunden.</p>"
else:
    for job in all_jobs:
        title = job.get("title", "Kein Titel")
        company = job.get("company", {}).get("display_name", "Unbekanntes Unternehmen")
        location = job.get("location", {}).get("display_name", "Deutschland")
        description = job.get("description", "Keine Beschreibung verfügbar.")
        redirect_url = job.get("redirect_url", "#")
        
        html_content += f"""
        <div class="job-card">
            <div class="job-title">{title}</div>
            <div class="job-details">
                <span>🏢 {company}</span>
                <span>📍 {location}</span>
            </div>
            <div class="job-desc">{description}</div>
            <a href="{redirect_url}" target="_blank" class="btn">Stelle anzeigen ➔</a>
        </div>
        """

html_content += """
    </div>
</body>
</html>
"""

with open("job_report.html", "w", encoding="utf-8") as f:
    f.write(html_content)