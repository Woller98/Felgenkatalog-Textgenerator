from flask import Flask, request
from playwright.sync_api import sync_playwright
import re

app = Flask(__name__)

def extract_data(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, timeout=60000)
        page.wait_for_timeout(2000)
        content = page.content()
        browser.close()

    modell = re.search(r"<h1[^>]*>(.*?)</h1>", content)
    modell = modell.group(1).strip() if modell else "Unbekanntes Modell"

    teilenummern = list(set(re.findall(r"A\d{10}", content)))
    teilenummern = teilenummern[:5]

    beschreibung = f"Die Original {modell} Felgen sind optisch wie technisch perfekt abgestimmt. Die Teilenummer(n): {', '.join(teilenummern)} bestätigen die Echtheit."
    hashtags = "#felgenkatalog #originalfelgen #oemfelgen #" + modell.lower().replace(" ", "") + " " + ' '.join(f"#{tn.lower()}" for tn in teilenummern)

    return beschreibung + "\n\n" + hashtags

@app.route("/scrape")
def scrape():
    url = request.args.get("url")
    if not url:
        return "Bitte eine URL angeben.", 400
    return extract_data(url)

if __name__ == "__main__":
    app.run(debug=True)
