from Agents.BaseAgent import BaseAgent
from Tools.ElsevierTool import elsevier_tool

class ElsevierAgent(BaseAgent):
    """
    Agent for retrieving article content using the Elsevier API tool.
    """
    def __init__(self):
        system_instruction = """
        You are an academic research assistant.
        Your job is to find the content of scientific articles using the `Elsevier Article Search` tool.
        If a user asks for the abstract or content of an article, call `get_article_content(title)`.
        Example:
        User: Give me the content of 'Deep Learning for AI'.  
        Assistant: (Call get_article_content("Deep Learning for AI")) 
        """
        super().__init__(tools=[elsevier_tool],name="elsevier_agent", system_instructions=system_instruction)