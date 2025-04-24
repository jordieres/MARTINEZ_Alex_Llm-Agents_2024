from Tools.WeatherTool import weather_tool
from Agents.BaseAgent import BaseAgent


class WeatherAgent(BaseAgent):
    """
    Agent for retrieving weather information using the OpenWeatherMap tool.
    """
    def __init__(self):
        system_instruction = """
        You are a weather assistant. Your task is to provide current weather information.
        You have access to a weather tool called `get_weather(location)`.  
        If the user asks about the weather, use this tool by providing a valid city or location.
        Example:
        User: What's the weather like in Madrid?  
        Assistant: (Call get_weather("Madrid"))  
        """
        super().__init__(tools=[weather_tool],name="weather_agent", system_instructions=system_instruction)