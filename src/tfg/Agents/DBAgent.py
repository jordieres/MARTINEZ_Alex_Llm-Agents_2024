from langchain.agents import initialize_agent, AgentType
from langchain_google_vertexai import ChatVertexAI
from langchain.memory import ConversationBufferMemory
from Tools.DBTool import influx_tool
import vertexai

class DBAgent:
    """
    Agent for querying InfluxDB using LangChain's initialize_agent.
    """

    def __init__(self):
        # Vertex AI initialization
        vertexai.init(project="summer-surface-443821-r9", location="europe-southwest1")

        # LLM setup
        llm = ChatVertexAI(
            model_name="gemini-2.0-flash",
            temperature=0.28,
            max_output_tokens=1000,
            top_p=0.95,
            top_k=40,
        )

        # System prompt / instruction for the agent
        self.agent_executor = initialize_agent(
            tools=[influx_tool],
            llm=llm,
            agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True,
            memory=ConversationBufferMemory()
        )
        
        self.name = "Database Agent"

    def invoke(self, state):
        """
        Entry point for LangGraph supervisor. Accepts a state dict and returns the updated one.

        Args:
            state (dict): LangGraph state containing 'messages'.

        Returns:
            dict: Updated state with assistant message added.
        """
        # Extract the last user message
        user_message = state["messages"][-1].content
        print(f"🧠 DBAgent received: {user_message}")

        # Run the agent with the query
        try:
            result = self.agent_executor.run(user_message)
        except Exception as e:
            result = f"❌ Error in DBAgent: {str(e)}"

        # Add the assistant response to the message list
        updated_messages = state["messages"] + [{"type": "ai", "content": result}]
        return {"messages": updated_messages}

