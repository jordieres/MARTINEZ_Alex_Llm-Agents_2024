from langchain.agents import initialize_agent, AgentType
from langchain.tools import Tool
from langchain_google_vertexai import VertexAI
from typing import Dict, List
import vertexai

class BaseAgent:
    """
    Base class for creating custom agents with specific tools.

    Args:
        tool (Tool): The tool that the agent will use.
        model_name (str): The name of the Vertex AI model to use.
        model_kwargs (Dict): Additional arguments for the model.
    """
    def __init__(
        self,
        tools: List[Tool],
        system_instructions: str = "",
        model_name: str = "gemini-1.5-flash",
        model_kwargs: Dict = None,
    ):
        # Hardcoded Vertex AI configuration
        project = "summer-surface-443821-r9"
        location = "europe-southwest1"

        # Initialize Vertex AI
        vertexai.init(project=project, location=location)

        # Model configuration
        self.tools = tools
        self.system_instructions = system_instructions
        self.model_kwargs = model_kwargs or {
            "temperature": 0.28,
            "max_output_tokens": 1000,
            "top_p": 0.95,
            "top_k": 40,
        }

        # Initialize the LLM
        llm = VertexAI(model_name=model_name, **self.model_kwargs)

        # Initialize the LangChain Agent
        self.agent = initialize_agent(
            tools=self.tools,
            llm=llm,
            agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,  # Uses tools only if needed
            verbose=True,  # Enables logging for debugging
        )

    def run(self, query: str) -> str:
        """
        Executes the agent with a given query.

        Args:
            query (str): The user query.

        Returns:
            str: The agent's response.
        """
        try:
            print(f"🚀 Query being processed by agent:\n{query}")
            response = self.agent.run(query)
            return response
        except Exception as e:
            print(f"❌ Error executing the agent: {str(e)}")
            return f"Error: {str(e)}"