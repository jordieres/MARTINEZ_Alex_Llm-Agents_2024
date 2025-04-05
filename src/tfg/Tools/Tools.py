from langchain.tools import Tool

class IndustrialTool:
    def __init__(self):
        self.name = "industrial-tool"
        self.description = "Handles various industrial problems like unit conversion, optimization tasks, and more."
    
    def run(self, query):
        # Convert the query to lowercase for easier processing
        query = query.lower()

        # Logic for unit conversion
        if "convert" in query:
            if "meters to feet" in query:
                value = self.extract_number(query)
                if value is not None:
                    result = value * 3.28084
                    return f"{value} meters is {result:.2f} feet."
                else:
                    return "No numerical value was found in the query."
            elif "kilograms to pounds" in query:
                value = self.extract_number(query)
                if value is not None:
                    result = value * 2.20462
                    return f"{value} kilograms is {result:.2f} pounds."
                else:
                    return "No numerical value was found in the query."
            # Add more conversion logic as needed
            else:
                return "Sorry, I can't perform that conversion yet."
        
        # Placeholder for optimization tasks
        elif "optimize" in query:
            # Implement optimization logic here
            return "Optimization logic is not yet implemented."
        
        # Handle other industrial problems
        else:
            return "Could not identify the industrial problem or the requested conversion."
    
    def extract_number(self, query):
        # Simple method to extract numbers from the query
        import re
        numbers = re.findall(r'\d+\.?\d*', query)
        if numbers:
            return float(numbers[0])
        else:
            return None

# Create an instance of the tool
industrial_tool_instance = IndustrialTool()

# Initialize the LangChain tool with the `run` method of our class
tools = [Tool(
    name="industrial-tool",
    func=IndustrialTool().run,
    description="Handles various industrial problems like unit conversion, optimization tasks, and more."
)]