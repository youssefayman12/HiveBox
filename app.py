"""HiveBox - Phase 3

A small Flask API that exposes:
  - /version      : returns the deployed app version.
  - /temperature  : returns the current average temperature across all
                    configured senseBoxes, using data no older than 1 hour.
"""

from datetime import datetime, timedelta, timezone

import requests
from flask import Flask, jsonify

__version__ = "0.0.1"

# Three senseBox IDs close to each other, as suggested by the project.
SENSEBOX_IDS = [
    "5eba5fbad46fb8001b799786",
    "5c21ff8f919bf8001adf2488",
    "5ade1acf223bd80019a1011c",
]

OPENSENSEMAP_URL = "https://api.opensensemap.org/boxes/{box_id}/sensors"
MAX_DATA_AGE = timedelta(hours=1)
REQUEST_TIMEOUT = 10  # seconds

app = Flask(__name__)


def _is_recent(measured_at: str) -> bool:
    """Return True if an ISO-8601 timestamp is within the last hour."""
    measured = datetime.fromisoformat(measured_at.replace("Z", "+00:00"))
    return datetime.now(timezone.utc) - measured <= MAX_DATA_AGE


def get_temperatures() -> list[float]:
    """Collect recent temperature readings from all configured senseBoxes."""
    temperatures: list[float] = []

    for box_id in SENSEBOX_IDS:
        try:
            response = requests.get(
                OPENSENSEMAP_URL.format(box_id=box_id),
                timeout=REQUEST_TIMEOUT,
            )
            response.raise_for_status()
        except requests.RequestException:
            # Skip unreachable boxes; a partial result is still useful.
            continue

        for sensor in response.json().get("sensors", []):
            if sensor.get("title", "").lower() != "temperatur":
                continue

            measurement = sensor.get("lastMeasurement")
            if not measurement or "value" not in measurement:
                continue

            if _is_recent(measurement.get("createdAt", "")):
                try:
                    temperatures.append(float(measurement["value"]))
                except (TypeError, ValueError):
                    continue

    return temperatures


@app.route("/version")
def version():
    """Return the version of the deployed app."""
    return jsonify({"version": __version__})


@app.route("/temperature")
def temperature():
    """Return the current average temperature based on all senseBox data."""
    temperatures = get_temperatures()

    if not temperatures:
        return jsonify({"error": "No recent temperature data available"}), 503

    average = round(sum(temperatures) / len(temperatures), 2)
    return jsonify({
        "average_temperature": average,
        "sensor_count": len(temperatures),
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
