from Agents.BaseAgent import BaseAgent
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain.schema import HumanMessage, AIMessage, SystemMessage
from langchain.memory import ConversationBufferMemory
from Agents.WeatherAgent import WeatherAgent
from Agents.DBAgent import DBAgent
from Agents.CrossrefAgent import CrossrefAgent
from Agents.ElsevierAgent import ElsevierAgent
import transformers, warnings
from langchain_google_vertexai import ChatVertexAI
from langgraph_supervisor import create_supervisor
import vertexai
from Tools.CrossrefTool import crossref_tool
from Tools.WeatherTool import weather_tool
from Tools.ElsevierTool import elsevier_tool
from Tools.DBTool import influx_tool

# suppress excessive logs
transformers.logging.set_verbosity_error()
warnings.filterwarnings("ignore", category=DeprecationWarning)

# Initialize your specialized agents
weather_agent = WeatherAgent()
db_agent      = DBAgent()
cr_agent      = CrossrefAgent()
els_agent     = ElsevierAgent()

# Initialize Vertex AI & bind tools for the supervisor's underlying LLM
vertexai.init(project="summer-surface-443821-r9", location="europe-southwest1")
llm = ChatVertexAI(
    model_name="gemini-2.0-flash",
    temperature=0.28,
    max_output_tokens=1000,
    top_p=0.95,
    top_k=40
).bind_tools(
    [weather_tool, influx_tool, crossref_tool, elsevier_tool],
    tool_choice="auto"
)

# Create the supervisor
supervisor = create_supervisor(
    agents=[weather_agent, db_agent, cr_agent, els_agent],
    model=llm,
    prompt=(
        "You are a supervisor managing different tools for complex engineering queries.\n"
        "- Use `weather_agent` for weather tasks.\n"
        "- Use `db_agent` for database (sensor) queries.\n"
        "- Use `cr_agent` for searching article titles.\n"
        "- Use `els_agent` for fetching full article content.\n\n"
        "For explainability, narrate each decision and who you call.\n"
        "Once all tools have been consulted, return the final answer to the user."
    )
)

# Compile the LangGraph workflow
graph = supervisor.compile()

def run_conversation(user_input: str):
    """
    Runs one turn of the supervisor flow, then prints:
      1) A full trace of every message exchanged
      2) The `final_output` field if present (otherwise, last assistant content)
    """
    print("\n🔄 Starting Supervisor Flow")
    result = graph.invoke({
        "messages": [HumanMessage(content=user_input)]
    })

    # 1) Full message trace (for debugging / explainability)
    print("\n📜 Full message trace:")
    for msg in result["messages"]:
        # Use the message's class name as its 'role'
        msg_type = msg.__class__.__name__
        # Safely get its `.content`
        content = getattr(msg, "content", "")
        print(f"{msg_type}: {content}")

    # 2) Print `final_output` if provided by the agent
    final = result.get("final_output")
    if final:
        print("\n🧠 Final Output:")
        print(final)
    else:
        # Fallback: reprint the last assistant content
        last = result["messages"][-1]
        fallback = getattr(last, "content", str(last))
        print("\n⚠️ No `final_output` field, falling back to last assistant message:")
        print(fallback)

if __name__ == "__main__":
    while True:
        ui = input("\nUser: ")
        if ui.lower() in ["quit", "exit", "q"]:
            print("👋 Goodbye!")
            break
        run_conversation(ui)
