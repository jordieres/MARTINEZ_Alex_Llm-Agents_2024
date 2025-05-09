from typing import Optional
from langchain.tools import StructuredTool
from pydantic import BaseModel
import requests
from datetime import datetime
import pytz


class WeatherInput(BaseModel):
    location: str
    date: Optional[str] = None  # Format: YYYY-MM-DD
    hour: Optional[int] = None  # 0 to 23


def get_weather_openmeteo(location: str = "Madrid", date: Optional[str] = None) -> str:
    """
    Fetches daily weather data (hourly breakdown) from Open-Meteo for a given date and location.
    Historical dates are supported. Hour-level queries are not supported in this version.

    Args:
        location (str): City name (e.g., "Madrid").
        date (Optional[str]): Target date (YYYY-MM-DD). Defaults to today if not provided.

    Returns:
        str: Text summary of hourly weather data for the date (temperature and humidity).
    """
    try:
        # Step 1: Get coordinates
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={location}&count=1"
        geo_response = requests.get(geo_url)
        geo_data = geo_response.json()

        if "results" not in geo_data or not geo_data["results"]:
            return f"Location '{location}' not found."

        lat = geo_data["results"][0]["latitude"]
        lon = geo_data["results"][0]["longitude"]
        tz = geo_data["results"][0].get("timezone", "Europe/Madrid")

        # Step 2: Select archive or forecast endpoint
        if date:
            base_url = "https://archive-api.open-meteo.com/v1/archive"
        else:
            base_url = "https://api.open-meteo.com/v1/forecast"
            date = datetime.now(pytz.timezone(tz)).strftime("%Y-%m-%d")

        params = {
            "latitude": lat,
            "longitude": lon,
            "start_date": date,
            "end_date": date,
            "hourly": "temperature_2m,relative_humidity_2m",
            "timezone": tz,
        }

        response = requests.get(base_url, params=params)
        data = response.json()

        if "hourly" not in data or "temperature_2m" not in data["hourly"]:
            return f"No weather data available for {location} on {date}."

        times = data["hourly"]["time"]
        temps = data["hourly"]["temperature_2m"]
        humidity = data["hourly"]["relative_humidity_2m"]

        summary_lines = [f"Weather in {location} on {date}:"]
        for i in range(len(times)):
            hour_str = times[i].split("T")[1]
            summary_lines.append(f"- {hour_str}: {temps[i]}°C, {humidity[i]}% humidity")

        return "\n".join(summary_lines)

    except Exception as e:
        return f"Failed to fetch weather data: {str(e)}"

# Register as LangChain StructuredTool
weather_tool = StructuredTool.from_function(
    name="weather_tool_openmeteo",
    description=(
        "Fetches historical or current weather data using Open-Meteo. "
        "Accepts a location (e.g., 'Madrid') and an optional date (YYYY-MM-DD). "
        "Returns hourly breakdown (temperature and humidity) for the day."
    ),
    func=get_weather_openmeteo,
    args_schema=WeatherInput,
)