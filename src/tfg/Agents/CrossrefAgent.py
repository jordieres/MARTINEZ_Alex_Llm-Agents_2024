from tfg.Tools.CrossrefTool import crossref_tool
from tfg.Agents.BaseAgent import BaseAgent

class CrossrefAgent(BaseAgent):
    """
    Agent for searching scientific articles using the Crossref tool.
    """
    def __init__(self):
        system_instruction = """
            You are an academic research assistant specialized in retrieving bibliographic information from scientific publications. 
            You have access to the `CrossRef API` tool, which can provide details such as title, authors, publication date, DOI, 
            and abstract of academic articles. When a user requests information about a specific publication, use this tool 
            by providing the article's title or DOI.
            Example:
            User: Provide details about the article titled "Deep Learning for AI".
            Assistant: (Calls the CrossRef API tool with the title "Deep Learning for AI")
            """
        super().__init__(tools=[crossref_tool],name="crossref_agent", system_instructions=system_instruction)