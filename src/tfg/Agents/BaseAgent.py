from langchain.agents import Tool
from langgraph.prebuilt import create_react_agent
from langchain_google_vertexai import ChatVertexAI
from typing import Dict, List
import vertexai


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
    def __init__(
        self,
        tools: List[Tool],
        name: str,
        system_instructions: str = "",
        model_name: str = "gemini-2.0-flash",
        model_kwargs: Dict = None,
    ):
        # Vertex AI project/location setup (hardcoded for this use case)
        project = "summer-surface-443821-r9"
        location = "europe-southwest1"

        # Initialize Vertex AI context
        vertexai.init(project=project, location=location)

        # Default model config (can be overridden by user)
        self.model_kwargs = model_kwargs or {
            "temperature": 0.28,
            "max_output_tokens": 1000,
            "top_p": 0.95,
            "top_k": 40,
        }

        # Create the VertexAI chat model
        llm = ChatVertexAI(model_name=model_name, **self.model_kwargs)

        # Create the LangGraph-compatible React-style agent
        self.name = name  # Needed by langgraph-supervisor for routing
        self.agent = create_react_agent(
            model=llm,
            tools=tools,
            name=name,
            prompt=system_instructions
        )

    def invoke(self, state: dict) -> dict:
        """
        Supervisor-compatible entry point for executing the agent.
        Receives a LangGraph state dict and returns updated messages.

        Args:
            state (dict): LangGraph state containing 'messages'.

        Returns:
            dict: Updated state with appended assistant message.
        """
        from langchain_core.messages import HumanMessage

        user_message = state["messages"][-1].content
        print(f"🧠 {self.name} received: {user_message}")

        try:
            response = self.agent.invoke({"messages": [HumanMessage(content=user_message)]})
            content = response["messages"][-1].content
        except Exception as e:
            content = f"❌ Error in {self.name}: {str(e)}"

        updated_messages = state["messages"] + [{"type": "ai", "content": content}]
        return {"messages": updated_messages}


    def run(self, query: str) -> str:
        """
        Convenience method for standalone testing/debugging.

        Args:
            query (str): User input to run directly through the agent.

        Returns:
            str: The agent’s textual response.
        """
        from langchain_core.messages import HumanMessage
        return self.agent.invoke({"messages": [HumanMessage(content=query)]})["messages"][-1].content
