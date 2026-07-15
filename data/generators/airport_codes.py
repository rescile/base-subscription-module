import requests
import os
import json

# Configuration
REPO_URL = "https://raw.githubusercontent.com/mwgg/Airports/master/airports.json"

# Paths
# Current directory where the script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# ETag saved in the script's directory
STATE_FILE = os.path.join(SCRIPT_DIR, "airport_etag.txt")
# JSON saved in ../input/airports.json
DATA_FILE = os.path.join(SCRIPT_DIR, "..", "input", "airports.json")


def filter_airports_with_iata(raw_json: str) -> dict:
    """Parse the raw airports.json and keep only entries with a non-empty IATA code."""
    all_airports = json.loads(raw_json)
    return {
        icao: airport
        for icao, airport in all_airports.items()
        if airport.get("iata")
    }


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

            filtered = filter_airports_with_iata(response.text)

            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(filtered, f, ensure_ascii=False, indent=2)

            if new_etag:
                with open(STATE_FILE, "w") as f:
                    f.write(new_etag)

            print(f"Filtered {len(filtered)} airports with IATA codes saved to: {DATA_FILE}")
        else:
            print(f"Failed to retrieve data: {response.status_code}")

    except requests.RequestException as e:
        print(f"Error checking for updates: {e}")
    except (json.JSONDecodeError, AttributeError) as e:
        print(f"Error parsing airport data: {e}")


if __name__ == "__main__":
    update_airport_data()
