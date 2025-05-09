from langchain.agents import initialize_agent, AgentType
from langchain_google_vertexai import ChatVertexAI
from langchain.memory import ConversationBufferMemory
from Tools.DBTool import influx_tool
import vertexai


class DBAgent:
    """
    Agent for querying InfluxDB using LangChain's initialize_agent.
    Compatible with langgraph-supervisor expectations.
    """

    def __init__(self):
        system_instruction = """
        You are a database assistant for querying sensor data from a university lab environment.
        - All sensors belong to laboratories at Universidad Politécnica de Madrid.
        - If the user refers to "the lab" or "indoor data", assume it means the laboratory's sensor system.
        - If indoor data is missing, notify the user and suggest using fallback sources like outdoor data or weather API.
        - Sensor data includes temperature, humidity, light, motion, and vdd.
        - Time ranges can be relative (e.g., 7d) or absolute (e.g., 2024-11-01 to 2024-11-10).
        - If the user specifies outdoor data  is the weather agent work
        """
        
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

        # Tool-based agent setup
        self.agent_executor = initialize_agent(
            tools=[influx_tool],
            llm=llm,
            agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True,
            memory=ConversationBufferMemory(),
            agent_kwargs={"system_message": system_instruction}
        )

        self.name = "db_agent"

    def invoke(self, state):
        """
        Entry point for LangGraph supervisor. Accepts a state dict and returns the updated one.
        """
        # 🔍 Find the last user message (HumanMessage)
        user_messages = [m for m in state["messages"] if m.type == "human"]
        if not user_messages:
            query = "No human message found."
        else:
            query = user_messages[-1].content

        print(f"🧠 db_agent received query: {query}")

        try:
            response = self.agent_executor.run(query)
        except Exception as e:
            response = f"❌ Error in DBAgent: {str(e)}"

        return {
            "messages": state["messages"] + [{"type": "ai", "content": response}],
            "final_output": response,
        }
