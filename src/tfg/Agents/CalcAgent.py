from Tools.CalcTool import calculator_tool
from Agents.BaseAgent import BaseAgent

class CalculatorAgent(BaseAgent):
    """
    Agent for performing simple mathematical operations like mean, sum, min, and max on lists of numbers.
    """
    def __init__(self):
        system_instruction = """
        You are a calculator assistant. Your task is to perform mathematical operations on a list of numbers.
        You have access to a calculator tool that supports the following operations:
        - mean: Compute the average value.
        - sum: Compute the total sum.
        - min: Get the smallest value.
        - max: Get the largest value.

        The tool expects a list of numbers and the operation to perform.
        Example:
        User: What is the average of [1, 2, 3]?
        Assistant: (Call calculator_tool with numbers=[1, 2, 3], operation="mean")
        """
        super().__init__(tools=[calculator_tool], name="calculator_agent", system_instructions=system_instruction)
