from langchain.tools import StructuredTool
from pydantic import BaseModel
from typing import List
import statistics

class CalculatorInput(BaseModel):
    numbers: List[float]
    operation: str  # "mean", "sum", "min", "max"

def calculate(numbers: List[float], operation: str) -> str:
    """
    Performs a calculation on a list of numbers.

    Args:
        numbers (List[float]): List of numerical values.
        operation (str): Operation to perform ("mean", "sum", "min", "max").

    Returns:
        str: Result of the calculation or error message.
    """
    try:
        if operation == "mean":
            return f"The mean is {statistics.mean(numbers):.2f}"
        elif operation == "sum":
            return f"The sum is {sum(numbers):.2f}"
        elif operation == "min":
            return f"The minimum is {min(numbers):.2f}"
        elif operation == "max":
            return f"The maximum is {max(numbers):.2f}"
        else:
            return f"❌ Unsupported operation: {operation}"
    except Exception as e:
        return f"❌ Calculation error: {str(e)}"

calculator_tool = StructuredTool.from_function(
    name="calculator_tool",
    description="Performs simple math operations (mean, sum, min, max) on a list of numbers.",
    func=calculate,
    args_schema=CalculatorInput
)
