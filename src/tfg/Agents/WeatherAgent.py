from Tools.WeatherTool import weather_tool
from Agents.BaseAgent import BaseAgent


class WeatherAgent(BaseAgent):
    """
    Agent for retrieving weather information using the OpenWeatherMap tool.
    """
    def __init__(self):
        system_instruction = """
        You are a weather assistant. Your task is to retrieve historical or current weather data using the Open-Meteo API.

        - You have access to a tool called `get_weather_openmeteo(location: str = "Madrid", date: Optional[str]`.
        - The tool supports both current and historical data, as long as you specify a valid location and optional date.
        - If no location is provided, assume "Madrid" by default, as the user is working with lab data from the Universidad Politécnica de Madrid.
        - If the user asks for weather data over **multiple days**, make a separate call to the tool for each day in the range.
        - If the user asks for an **average temperature or humidity over time**, you should collect the daily/hourly values and pass them to the `calculator_agent` to compute the result.

        Examples:
        - User: "What was the weather like in Madrid on 2024-11-08?" → (Call get_weather_openmeteo("Madrid", "2024-11-08"))
        - User: "What's the average temperature from Nov 8 to Nov 14?" → (Call tool for each date, then use calculator_agent to average the temperatures)
        """
        super().__init__(tools=[weather_tool],name="weather_agent", system_instructions=system_instruction)