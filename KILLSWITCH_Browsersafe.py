import json
import os
import requests
from urllib.parse import urlparse

# ---------------- CONFIG ----------------
CONFIG_FILE = "killswitch_data.json"
CHECKED_URLS_FILE = "checked_urls.json"
SAFE_BROWSING_API_KEY = "<YOUR_API_KEY>"  # User can insert their own
SAFE_BROWSING_ENDPOINT = "https://safebrowsing.googleapis.com/v4/threatMatches:find"

# ---------------- HELPER FUNCTIONS ----------------
def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {"username": "", "kills": 0, "trophies": []}

def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)

def load_checked_urls():
    if os.path.exists(CHECKED_URLS_FILE):
        with open(CHECKED_URLS_FILE, "r") as f:
            return json.load(f)
    return {}

def save_checked_urls(urls):
    with open(CHECKED_URLS_FILE, "w") as f:
        json.dump(urls, f, indent=4)

# ---------------- SAFE BROWSING CHECK ----------------
def check_url_safe(url):
    urls_checked = load_checked_urls()
    if url in urls_checked:
        return urls_checked[url]  # Return cached result

    payload = {
        "client": {"clientId": "KILLSWITCH", "clientVersion": "2.0"},
        "threatInfo": {
            "threatTypes": ["MALWARE", "SOCIAL_ENGINEERING", "UNWANTED_SOFTWARE"],
            "platformTypes": ["ANY_PLATFORM"],
            "threatEntryTypes": ["URL"],
            "threatEntries": [{"url": url}]
        }
    }

    params = {"key": SAFE_BROWSING_API_KEY}

    try:
        response = requests.post(SAFE_BROWSING_ENDPOINT, json=payload, params=params, timeout=5)
        result = response.json()
        is_safe = "matches" not in result
        urls_checked[url] = is_safe
        save_checked_urls(urls_checked)
        return is_safe
    except Exception as e:
        print(f"[!] API error: {e}")
        return True  # Assume safe if API fails

# ---------------- MAIN ----------------
def main():
    config = load_config()
    print("KILLSWITCH Browsersafe - Online URL Checker")

    while True:
        url = input("Enter a URL to check (or 'exit' to quit): ").strip()
        if url.lower() == "exit":
            break
        parsed = urlparse(url)
        if not parsed.scheme:
            url = "http://" + url

        safe = check_url_safe(url)
        if safe:
            print(f"[✓] URL appears safe: {url}")
        else:
            print(f"[⚠] URL may be dangerous: {url}")
            config["kills"] += 1
            save_config(config)
            print(f"Updated total kills: {config['kills']}")

if __name__ == "__main__":
    main()
