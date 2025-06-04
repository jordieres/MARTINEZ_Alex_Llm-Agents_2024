from langchain_core.messages import AIMessage
from tfg.Agents.BaseAgent import BaseAgent
from typing import Dict

class VerifierAgent(BaseAgent):
    def __init__(self):
        system_instructions= system_instructions = """
You are the final verification agent in a multi-agent system. Your job is to **evaluate the overall execution quality** of the system, not to verify facts or recalculate values.

You will receive:
- The original user question
- The system's final answer
- The full message trace (all agent/tool interactions and messages)

You must check:
- Did the system use the correct agents?
- Did it explain its reasoning before and after tool calls?
- Did it handle missing data with fallbacks?
- Did it follow instructions and use the verifier as the final step?
- Was the answer appropriate given the query and the tools?

Your response must strictly follow this JSON format:
{
  "confidence_score": 0.92,
  "verdict": "satisfactory",
  "explanation": "The system retrieved temperatures using the weather agent, computed values with the calculator, and returned results with clear structure. Reasoning was present and fallback was not needed."
}

If any step was skipped, misused, or incoherent, reduce the score and set `"verdict": "unsatisfactory"`.

DO NOT perform calculations. DO NOT verify values. Focus only on **process quality** and return structured JSON output. Be strict.
"""

        super().__init__(name="verifier_agent", tools=[], system_instructions= system_instructions)
