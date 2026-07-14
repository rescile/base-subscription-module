import requests
import os

# Configuration
REPO_URL = "https://raw.githubusercontent.com/mwgg/Airports/master/airports.json"

# Paths
# Current directory where the script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# ETag saved in the script's directory
STATE_FILE = os.path.join(SCRIPT_DIR, "airport_etag.txt")

# JSON saved in ../input/airports.json
DATA_FILE = os.path.join(SCRIPT_DIR, "..", "input", "airports.json")

def update_airport_data():
    # Ensure the ../input directory exists
    input_dir = os.path.dirname(DATA_FILE)
    if not os.path.exists(input_dir):
        os.makedirs(input_dir)
        print(f"Created directory: {input_dir}")

    last_etag = None
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            last_etag = f.read().strip()

    headers = {}
    if last_etag:
        headers["If-None-Match"] = last_etag

    try:
        response = requests.get(REPO_URL, headers=headers)

        if response.status_code == 304:
            print("File is up to date.")
            return

        if response.status_code == 200:
            new_etag = response.headers.get("ETag")
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                f.write(response.text)

            if new_etag:
                with open(STATE_FILE, "w") as f:
                    f.write(new_etag)

            print(f"Data saved to: {DATA_FILE}")
        else:
            print(f"Failed to retrieve data: {response.status_code}")

    except requests.RequestException as e:
        print(f"Error checking for updates: {e}")

if __name__ == "__main__":
    update_airport_data()
