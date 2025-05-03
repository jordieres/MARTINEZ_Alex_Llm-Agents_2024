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


def get_weather_openmeteo(location: str, date: Optional[str] = None, hour: Optional[int] = None) -> str:
    """
    Fetches weather information from Open-Meteo API for a specific location.
    It supports both current and historical weather data, and allows querying for either
    full-day hourly data or a specific hour.

    Args:
        location (str): The name of the location (e.g., "Madrid").
        date (Optional[str]): The target date in format "YYYY-MM-DD". If not provided, today's date is used.
        hour (Optional[int]): The specific hour (0-23) to retrieve. If not provided, data for the full day is returned.

    Returns:
        str: A string summarizing the weather conditions, including temperature and humidity, either for a full day or a specific hour.
             If the request fails or data is unavailable, a failure message is returned.
    """
    try:
        # Step 1: Get coordinates using Open-Meteo's geocoding API
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={location}&count=1"
        geo_response = requests.get(geo_url)
        geo_data = geo_response.json()

        if "results" not in geo_data or not geo_data["results"]:
            return f"Location '{location}' not found."

        lat = geo_data["results"][0]["latitude"]
        lon = geo_data["results"][0]["longitude"]
        tz = geo_data["results"][0].get("timezone", "Europe/Madrid")

        # Step 2: Determine the appropriate endpoint
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

        if hour is not None:
            # Specific hour requested
            target_time = f"{date}T{hour:02d}:00"
            if target_time not in times:
                return f"No data available for {location} at {target_time}."
            idx = times.index(target_time)
            return (
                f"Weather in {location} at {target_time}:\n"
                f"- Temperature: {temps[idx]}°C\n"
                f"- Humidity: {humidity[idx]}%"
            )
        else:
            # Return summary for all available hours
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
        "Fetches weather information using Open-Meteo. "
        "Accepts location (e.g., 'Madrid'), optional date (YYYY-MM-DD), "
        "and optional hour (0–23). Returns either the full day's hourly data or data for the specified hour."
    ),
    func=get_weather_openmeteo,
    args_schema=WeatherInput,
)