from pyowm import OWM
from langchain.tools import Tool
from pydantic import BaseModel
from langchain.tools import StructuredTool

# OpenWeatherMap configuration
API_KEY = "54b1d6c1af466db06bee6219ddb33f7c"
owm = OWM(API_KEY)
mgr = owm.weather_manager()

# Define expected input schema for the tool using Pydantic
class WeatherInput(BaseModel):
    location: str

# Define a function to obtain climate
def get_weather(location: str) -> str:
    """
    Fetches the current weather information for a specified location using OpenWeatherMap.

    Args:
        location (str): The name of the location (e.g., "Madrid" or "New York, US").
    
    Returns:
        str: A string describing the current weather conditions and temperature in Celsius.
             If an error occurs, returns a string explaining the failure.
    """
    
    try:
        observation = mgr.weather_at_place(location)
        weather = observation.weather
        return (
            f"The current weather in {location} is {weather.status} with a temperature of "
            f"{weather.temperature('celsius')['temp']}°C."
        )
    except Exception as e:
        return f"Failed to fetch weather data for {location}: {str(e)}"

# Create compatible tool
weather_tool = StructuredTool.from_function(
    name="weather_tool",
    description="Fetches current weather for a given location.",
    func=get_weather,
    args_schema=WeatherInput,
)