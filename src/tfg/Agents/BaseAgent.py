from langchain.agents import Tool
from langgraph.prebuilt import create_react_agent
from langchain_google_vertexai import ChatVertexAI
from typing import Dict, List
import vertexai
from langchain_core.messages import AIMessage
from tfg.utils.config import get_config_value

class BaseAgent:
    """
    BaseAgent is responsible for creating a specialized agent that can use a specific set of tools
    and execute reasoning and actions through LangGraph-compatible interfaces.

    This base class leverages `create_react_agent` to enable compatibility with the langgraph-supervisor
    model routing logic.

    Args:
        tools (List[Tool]): A list of LangChain-compatible tools the agent can use.
        name (str): A unique name for the agent (used by the supervisor).
        system_instructions (str): Prompt instructions to guide the agent's behavior.
        model_name (str): Name of the VertexAI chat model to use.
        model_kwargs (Dict): Optional model configuration overrides.
    """
    def __init__(self, tools: List[Tool], name: str, system_instructions: str = "", model_name: str = "gemini-2.0-flash", model_kwargs: Dict = None):
        # Vertex AI project/location setup (hardcoded for this use case)
        project = get_config_value("project", "default-project")
        location = get_config_value("location", "default-location")

        # Initialize Vertex AI context
        vertexai.init(project=project, location=location)

        # Default model config (can be overridden by user)
        self.model_kwargs = model_kwargs or {"temperature": 0.28, "max_output_tokens": 1000, "top_p": 0.95, "top_k": 40}

        # Create the VertexAI chat model
        llm = ChatVertexAI(model_name=model_name, **self.model_kwargs)

        # Create the LangGraph-compatible React-style agent
        self.name = name  # Needed by langgraph-supervisor for routing
        self.agent = create_react_agent(model=llm, tools=tools, name=name, prompt=system_instructions)

    from langchain_core.messages import AIMessage

    def invoke(self, input_data: dict) -> dict:
        """
        Entry point for langgraph-supervisor to call this agent.

        Args:
            input_data (dict): State passed by the supervisor (e.g., {"messages": [...]})

        Returns:
            dict: Agent's structured response.
        """
        print(f"🧠 {self.name} received query")
        if "messages" not in input_data or not input_data["messages"]:
            raise ValueError(f"{self.name} received an empty message list.")
    
        valid_msgs = [msg for msg in input_data["messages"] if hasattr(msg, "content") and msg.content]
        if not valid_msgs:
            raise ValueError(f"{self.name} received message(s) with no content.")
        result = self.agent.invoke(input_data)

        # Retrieve all AIMessage-type messages that have content
        messages = result.get("messages", [])
        final_output = None

        for msg in reversed(messages):
            if isinstance(msg, AIMessage) and msg.content.strip():
                final_output = msg.content.strip()
                break

        if final_output is None:
            final_output = "[Agent did not return a valid message]"

        # Append clean AIMessage to be surfaced by supervisor
        messages.append(AIMessage(content=final_output, name="supervisor"))

        return {
            "messages": messages,
            "final_output": final_output
        }

    def run(self, query: str) -> str:
        """
        Convenience method for standalone testing/debugging.

        Args:
            query (str): User input to run directly through the agent.

        Returns:
            str: The agent textual response.
        """
        from langchain_core.messages import HumanMessage
        return self.agent.invoke({"messages": [HumanMessage(content=query)]})["messages"][-1].content
