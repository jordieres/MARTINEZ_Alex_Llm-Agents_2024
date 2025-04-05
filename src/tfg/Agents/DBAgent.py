from Agents.BaseAgent import BaseAgent
from Tools.DBTool import influx_tool
import re

class DBAgent(BaseAgent):
    """
    Agent for retrieving time-series data from InfluxDB.
    """

    def __init__(self):
        system_instruction = """
        You are a database assistant specialized in sensor data stored in InfluxDB.
        - Identify the relevant metric (e.g., humidity, temperature, light).
        - Extract the time range (e.g., "last 24 hours", "past week").
        - Determine if an aggregation is needed (mean, max, min).
        - Pass only these extracted parameters to the database tool.

        Example interactions:
        User: "What was the average humidity in the last 24 hours?"
        Assistant: (Extracted parameters: {metric: "humidity", time_range: "24h", aggregation: "mean"})

        User: "Show me the max temperature last week."
        Assistant: (Extracted parameters: {metric: "temperature", time_range: "7d", aggregation: "max"})
        """
        super().__init__(tools=[influx_tool], system_instructions=system_instruction)
