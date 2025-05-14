from typing import Optional
from langchain.tools import StructuredTool
from pydantic import BaseModel
import requests
from datetime import datetime
import pytz

class WeatherInput(BaseModel):
    location: str = "Madrid"
    start_date: Optional[str] = None  # YYYY-MM-DD
    end_date: Optional[str] = None    # YYYY-MM-DD

def get_weather_range(location: str = "Madrid", start_date: Optional[str] = None, end_date: Optional[str] = None) -> str:
    """
    Fetches weather data for a location over a date range using Open-Meteo API.
    If no end_date is provided, assumes a single-day query.

    Args:
        location (str): Location name (e.g., "Madrid")
        start_date (str): ISO date (YYYY-MM-DD)
        end_date (str): ISO date (YYYY-MM-DD)

    Returns:
        str: Summary of temperatures per day and hourly breakdown.
    """
    try:
        # Step 1: Get coordinates
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={location}&count=1"
        geo_response = requests.get(geo_url)
        geo_data = geo_response.json()

        if "results" not in geo_data or not geo_data["results"]:
            return f"❌ Location '{location}' not found."

        lat = geo_data["results"][0]["latitude"]
        lon = geo_data["results"][0]["longitude"]
        tz = geo_data["results"][0].get("timezone", "Europe/Madrid")

        # Defaults to today if no start date is given
        if not start_date:
            start_date = datetime.now().strftime("%Y-%m-%d")
        if not end_date:
            end_date = start_date

        # Step 2: Query weather archive with hourly data
        base_url = "https://archive-api.open-meteo.com/v1/archive"
        params = {
            "latitude": lat,
            "longitude": lon,
            "start_date": start_date,
            "end_date": end_date,
            "daily": "temperature_2m_max,temperature_2m_min",
            "hourly": "temperature_2m",
            "timezone": tz
        }

        response = requests.get(base_url, params=params)
        data = response.json()

        if "daily" not in data or not data["daily"].get("temperature_2m_max"):
            return f"⚠️ No weather data available for {location} between {start_date} and {end_date}."

        # Format output
        summary = [f"📅 Weather in {location} from {start_date} to {end_date}:"]
        for i in range(len(data["daily"]["time"])):
            date = data["daily"]["time"][i]
            t_max = data["daily"]["temperature_2m_max"][i]
            t_min = data["daily"]["temperature_2m_min"][i]
            summary.append(f"- {date}: min {t_min}°C, max {t_max}°C")

            # Add hourly temperatures for the day
            hourly_times = data.get("hourly", {}).get("time", [])
            hourly_temps = data.get("hourly", {}).get("temperature_2m", [])
            if hourly_times and hourly_temps:
                summary.append("  Hourly temperatures:")
                for ht, temp in zip(hourly_times, hourly_temps):
                    if ht.startswith(date):
                        summary.append(f"    {ht[-5:]}: {temp}°C")

        return "\n".join(summary)

    except Exception as e:
        return f"❌ Failed to fetch weather data: {str(e)}"

# LangChain-compatible structured tool
weather_tool = StructuredTool.from_function(
    name="weather_tool_openmeteo",
    description=(
        "Fetches historical weather data (min/max temperature and hourly temperatures) from Open-Meteo. "
        "Input required: location (e.g., 'Madrid'), and optional start_date/end_date (YYYY-MM-DD). "
        "Returns daily summaries with hourly breakdowns."
    ),
    func=get_weather_range,
    args_schema=WeatherInput,
)
