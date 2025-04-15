from Agents.BaseAgent import BaseAgent
from langchain_core.tools import Tool
from typing import List, Tuple

class PlannerAgent(BaseAgent):
    """
    PlannerAgent is responsible for decomposing user prompts into a sequence of high-level steps.
    """

    def __init__(self):
        system_instructions = """
        You are a planner agent. Your task is to decompose the user's request into a step-by-step plan.
        - Understand the user's objective.
        - Identify what tools or agents would be required.
        - Break down the request into atomic steps, ordered logically.
        - Only use tools that are available in the system (e.g., database, weather, articles).
        - Be explicit, do not make assumptions.
        
        Your output must follow this format:
        Step 1: [description]
        Step 2: [description]
        ...
        """
        super().__init__(tools=[], system_instructions=system_instructions)

    def plan(self, user_input: str) -> Tuple[List[str], str]:
        """
        Generates a list of high-level steps to fulfill the user request.

        Args:
            user_input (str): The original user query.

        Returns:
            Tuple[List[str], str]: The extracted steps as a list, and the full textual trace.
        """
        print("🧠 Generating plan...")
        raw_response = self.agent.run(user_input)
        print("📝 Raw plan:\n", raw_response)

        # Extract steps (you can improve the robustness here if needed)
        steps = []
        for line in raw_response.splitlines():
            if line.lower().startswith("step"):
                parts = line.split(":", 1)
                if len(parts) == 2:
                    steps.append(parts[1].strip())

        return steps, raw_response

