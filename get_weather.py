# This python file will return the weather in a dictionary of the format:
# {
#     "current": {
#         "time": "JUNE 7, 2026 | 11PM",
#         "temperature": 34.1,
#         "humidity": 41,
#         "weather": "sunny"
#     },
#     "hourly": {
#         "time": [
#             "12AM", "1AM", "2AM", "3AM", ...  (12 entries total)
#         ],
#         "temperature":        [28.1, 27.4, 26.9, ..., 36.2, ...],
#         "humidity":  [55,   58,   61,   ..., 38,   ...],
#         "weather":          ["humid", "sunny", "rainy".....]
#     },
#     "daily": {
#         "time":               ["June 7, 2026", "June 8, 2026", ..., "June 13, 2026"],
#         "weather":       ["humid", "sunny", "rainy".....],
#         "temperature_max": [36, 31,  29,  33, 35, 37, 36],
#         "temperature_min": [27, 25,  24,  26, 26, 27, 27]
#     }
# }

import xml.etree.ElementTree as ET
from datetime import datetime
import requests

# ---------------------------------------------------------------------------
# WMO Weather Interpretation Code → human-readable label
# https://open-meteo.com/en/docs#weathervariables
# ---------------------------------------------------------------------------

WMO_CODES = {
    0: "Clear Sky",
    1: "Mostly Clear", 2: "Partly Cloudy", 3: "Overcast",
    45: "Foggy", 48: "Icy Fog",
    51: "Light Drizzle", 53: "Drizzle", 55: "Heavy Drizzle",
    56: "Freezing Drizzle", 57: "Heavy Freezing Drizzle",
    61: "Light Rain", 63: "Rain", 65: "Heavy Rain",
    66: "Freezing Rain", 67: "Heavy Freezing Rain",
    71: "Light Snow", 73: "Snow", 75: "Heavy Snow",
    77: "Snow Grains",
    80: "Light Showers", 81: "Showers", 82: "Heavy Showers",
    85: "Snow Showers", 86: "Heavy Snow Showers",
    95: "Thunderstorm",
    96: "Thunderstorm w/ Hail", 99: "Thunderstorm w/ Heavy Hail",
}

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"


def _geocode(location: str) -> tuple[float, float, str] | tuple[None, None, None]:
    """Return (latitude, longitude, resolved_name) or (None, None, None)."""
    try:
        resp = requests.get(
            GEOCODING_URL,
            params={"name": location, "count": 1,
                    "language": "en", "format": "json"},
            timeout=10,
        )
        resp.raise_for_status()
        results = resp.json().get("results")
        if not results:
            return None, None, None
        r = results[0]
        return r["latitude"], r["longitude"], r.get("name", location)
    except requests.RequestException:
        return None, None, None


def _wmo_label(code: int) -> str:
    return WMO_CODES.get(int(code), f"Code {code}")


def _fetch_weather(lat: float, lon: float) -> dict | None:
    """Fetch hourly + daily forecast from Open-Meteo."""
    params = {
        "latitude":  lat,
        "longitude": lon,
        # Current conditions
        "current": "temperature_2m,relative_humidity_2m,weather_code",
        # Hourly (next 12 h)
        "hourly": "temperature_2m,relative_humidity_2m,weather_code",
        # Daily (7 days)
        "daily": "weather_code,temperature_2m_max,temperature_2m_min",
        "forecast_days": 7,
        "timezone": "auto",
    }
    try:
        resp = requests.get(FORECAST_URL, params=params, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException:
        return None


def _build_hourly(data: dict) -> dict:
    current = data["current"]
    cur_time = datetime.fromisoformat(current["time"])

    hourly_times = data["hourly"]["time"]
    hourly_temps = data["hourly"]["temperature_2m"]
    hourly_hums = data["hourly"]["relative_humidity_2m"]
    hourly_codes = data["hourly"]["weather_code"]

    times, temps, hums, weathers = [], [], [], []

    for i, t_str in enumerate(hourly_times):
        if len(times) >= 12:
            break
        t = datetime.fromisoformat(t_str)
        if t <= cur_time:
            continue
        hour = t.hour
        suffix = "AM" if hour < 12 else "PM"
        display_hour = hour % 12 or 12
        times.append(f"{display_hour}{suffix}")
        temps.append(hourly_temps[i])
        hums.append(round(hourly_hums[i]))
        weathers.append(_wmo_label(hourly_codes[i]))

    return {
        "time":        times,
        "temperature": temps,
        "humidity":    hums,
        "weather":     weathers,
    }


def _build_daily(data: dict) -> dict:
    daily_times = data["daily"]["time"]
    daily_codes = data["daily"]["weather_code"]
    daily_max = data["daily"]["temperature_2m_max"]
    daily_min = data["daily"]["temperature_2m_min"]

    times = [
        datetime.strptime(d, "%Y-%m-%d").strftime("%B %-d, %Y")
        for d in daily_times
    ]

    return {
        "time":            times,
        "weather":         [_wmo_label(c) for c in daily_codes],
        "temperature_max": [round(t) for t in daily_max],
        "temperature_min": [round(t) for t in daily_min],
    }

# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def getWeather(location: str) -> dict:
    lat, lon, _ = _geocode(location)
    if lat is None:
        return

    raw = _fetch_weather(lat, lon)
    if raw is None:
        return

    c = raw["current"]
    cur_time = datetime.fromisoformat(c["time"])
    current = {
        "time":        cur_time.strftime("%B %-d, %Y | %-I%p").upper(),
        "temperature": c["temperature_2m"],
        "humidity":    c["relative_humidity_2m"],
        "weather":     _wmo_label(c["weather_code"]),
    }

    return {
        "current": current,
        "hourly": _build_hourly(raw),
        "daily": _build_daily(raw),
    }


GDACS_URL = "https://www.gdacs.org/xml/rss.xml"


def getDisasters(location_name: str) -> list[dict]:
    """
    Fetch active disasters near a location from GDACS RSS feed.
    Returns a list of dicts: {title, type, severity, link}
    Only returns disasters that mention the country/city in their title.
    """
    try:
        resp = requests.get(GDACS_URL, timeout=10)
        resp.raise_for_status()
        root = ET.fromstring(resp.content)
    except Exception:
        return []

    disasters = []
    search_term = location_name.lower()

    for item in root.findall(".//item"):
        title = item.findtext("title") or ""
        link = item.findtext("link") or ""

        # Only include if location name appears in the title
        if search_term in title.lower():
            disasters.append({
                "title":    title,
                "link":     link,
            })

    return disasters
