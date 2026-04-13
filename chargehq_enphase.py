#!/usr/bin/env python3
"""Push Enphase Envoy solar data to Charge HQ."""

import logging
import os
import sys
import time

import requests
import urllib3
from dotenv import load_dotenv

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

load_dotenv()

API_KEY = os.environ.get("CHARGEHQ_API_KEY", "")
ENVOY_LOCAL_IP = os.environ.get("ENVOY_LOCAL_IP", "")
ACCESS_TOKEN = os.environ.get("ENVOY_ACCESS_TOKEN", "")
LOG_FILE_PATH = os.environ.get("LOG_FILE_PATH", "")
PUSH_INTERVAL = int(os.environ.get("PUSH_INTERVAL") or "60")
BACKOFF_MAX = int(os.environ.get("BACKOFF_MAX") or "300")

CHARGEHQ_URI = "https://api.chargehq.net/api/public/push-solar-data"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[logging.StreamHandler()],
)
if LOG_FILE_PATH:
    logging.getLogger().addHandler(logging.FileHandler(LOG_FILE_PATH))

logger = logging.getLogger("chargehq-enphase")

missing = [
    k
    for k, v in [
        ("CHARGEHQ_API_KEY", API_KEY),
        ("ENVOY_LOCAL_IP", ENVOY_LOCAL_IP),
        ("ENVOY_ACCESS_TOKEN", ACCESS_TOKEN),
    ]
    if not v
]
if missing:
    logger.error("Missing required environment variables: %s", ", ".join(missing))
    sys.exit(1)


def fetch_envoy_data():
    """Fetch data from the Envoy device."""
    try:
        headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
        response = requests.get(
            f"https://{ENVOY_LOCAL_IP}/production.json?details=1",
            headers=headers,
            verify=False,
            timeout=10,
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error("Error fetching data from Envoy: %s", e)
        return None


def calculate_values(data):
    """Calculate required values from the fetched data."""
    try:
        production_kw = max(data["production"][1]["wNow"] / 1000, 0)
        consumption_kw = max(data["consumption"][0]["wNow"] / 1000, 0)
        net_import_kw = round(consumption_kw - production_kw, 3)

        return {
            "production_kw": round(production_kw, 3),
            "consumption_kw": round(consumption_kw, 3),
            "net_import_kw": round(net_import_kw, 3),
        }
    except (KeyError, TypeError, IndexError) as e:
        logger.error("Error calculating values: %s", e)
        return None


def push_to_chargehq(values):
    """Send calculated values to ChargeHQ."""
    payload = {"apiKey": API_KEY, "siteMeters": values}
    try:
        response = requests.post(CHARGEHQ_URI, json=payload, timeout=10)
        if response.status_code == 200:
            logger.info("Pushed to Charge HQ: %s", payload)
        else:
            logger.error(
                "Charge HQ returned %s: %s", response.status_code, response.text
            )
    except requests.exceptions.RequestException as e:
        logger.error("Error pushing data to Charge HQ: %s", e)


def main():
    backoff = PUSH_INTERVAL
    logger.info(
        "Starting Charge HQ / Enphase integration (push interval: %ss)", PUSH_INTERVAL
    )

    try:
        while True:
            envoy_data = fetch_envoy_data()
            if envoy_data:
                calculated_values = calculate_values(envoy_data)
                if calculated_values:
                    push_to_chargehq(calculated_values)
                backoff = PUSH_INTERVAL
            else:
                backoff = min(backoff * 2, BACKOFF_MAX)
                logger.warning("Backing off, retrying in %ss", backoff)
            time.sleep(backoff)
    except KeyboardInterrupt:
        logger.info("Shutting down.")


if __name__ == "__main__":
    main()
