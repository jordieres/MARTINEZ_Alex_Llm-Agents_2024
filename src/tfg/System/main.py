import sys 
import os
# Add the root path of your modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from langchain.schema import HumanMessage, BaseMessage
from Agents.WeatherAgent import WeatherAgent
from Agents.DBAgent import DBAgent
from Agents.CrossrefAgent import CrossrefAgent
from Agents.ElsevierAgent import ElsevierAgent
from Agents.CalcAgent import CalculatorAgent
import transformers, warnings
from langchain_google_vertexai import ChatVertexAI
from langgraph_supervisor import create_supervisor
import vertexai
from Tools.CrossrefTool import crossref_tool
from Tools.WeatherTool import weather_tool
from Tools.ElsevierTool import elsevier_tool
from Tools.DBTool import influx_tool
from Tools.CalcTool import calculator_tool
from typing import List

# suppress excessive logs
transformers.logging.set_verbosity_error()
warnings.filterwarnings("ignore", category=DeprecationWarning)

from graphviz import Source

def export_graph_png(output_path="langgraph_diagram.png"):
    """
    Generates a PNG diagram of the compiled LangGraph supervisor flow.
    """
    graph = create_system().get_graph()
    dot_source = graph.draw_png()  # Get DOT format
    s = Source(dot_source)
    s.render(output_path, format="png", cleanup=True)
    print(f"✅ LangGraph diagram exported as: {output_path}")

def print_graph_ascii():
    graph = create_system().get_graph()
    graph.print_ascii()

def print_graph_mermaid():
    graph = create_system().get_graph()
    print(graph.draw_mermaid())


# ✅ Encapsulate system creation to allow per-execution isolation
def create_system():
    # Initialize your specialized agents
    weather_agent = WeatherAgent()
    db_agent      = DBAgent()
    crossref_agent      = CrossrefAgent()
    elsevier_agent     = ElsevierAgent()
    calculator_agent = CalculatorAgent()

    # Initialize Vertex AI & bind tools for the supervisor's underlying LLM
    vertexai.init(project="summer-surface-443821-r9", location="europe-southwest1")
    llm = ChatVertexAI(
        model_name="gemini-2.0-flash",
        temperature=0.28,
        max_output_tokens=1000,
        top_p=0.95,
        top_k=40
    ).bind_tools(
        [weather_tool, influx_tool, crossref_tool, elsevier_tool, calculator_tool],
        tool_choice="auto"
    )

    # Create the supervisor
    supervisor = create_supervisor(
        agents=[weather_agent, db_agent, crossref_agent, elsevier_agent, calculator_agent],
        model=llm,
        prompt=(
            "You are a supervisor managing different tools for complex engineering queries.\n"
            "- Use `weather_agent` to get **outdoor temperature**, historical or not, using approximate or simulated data if needed.\n"
            "- Use `db_agent` to access **indoor sensor data** from the lab (e.g., humidity, temperature, light).\n"
            "- Use `calculator_agent` to compute statistics like mean, max, min over multiple values.\n"
            "- Use `cr_agent` to search article titles and `els_agent` to retrieve article content.\n\n"
            "- Use `calculator_agent` for performing numeric operations like mean, max, or min.\n\n"
            "General context:\n"
            "- The system handles queries for an environmental sensor network deployed at Universidad Politécnica de Madrid.\n"
            "- The term 'lab' refers to laboratory spaces monitored by these sensors.\n"
            "- Assume standard working hours (9am-5pm) if occupancy data is missing.\n"
            "- Use Madrid as the default external weather location.\n\n"
            "You may call multiple tools or repeat tool calls if needed.\n"
            "If you need a daily breakdown or to compute an average over multiple days, query each day using an agent and then aggregate.\n"
            "Always narrate your reasoning before and after each tool call.\n"
            "Do not assume missing data – if a sensor query fails, try a fallback or notify the user.\n"
            "Only return a final answer when all data is gathered and processed."
        )
    )

    # Compile the LangGraph workflow
    return supervisor.compile()

def run_conversation(user_input: str, return_full: bool = False):
    """
    Runs one turn of the supervisor flow, then prints:
      1) A full trace of every message exchanged
      2) The `final_output` field if present (otherwise, last assistant content)
    
    ✅ Modified: each run uses a fresh memory and new system
    """
    print("\n🔄 Starting Supervisor Flow")

    graph = create_system()
    memory: List[BaseMessage] = [HumanMessage(content=user_input)]

    # Run the graph with fresh memory
    result = graph.invoke({
        "messages": memory
    })

    if return_full:
        return result

    # 1) Full message trace (for debugging / explainability)
    print("\n📜 Full message trace:")
    for msg in result["messages"]:
        msg_type = msg.__class__.__name__
        content = getattr(msg, "content", "")
        print(f"{msg_type}: {content}")

    # 2) Print `final_output` if provided by the agent
    final = result.get("final_output")
    if final:
        print("\n🧠 Final Output:")
        print(final)
    else:
        last = result["messages"][-1]
        fallback = getattr(last, "content", str(last))
        print("\n Response:")
        print(fallback)

if __name__ == "__main__":
    if "--graph" in sys.argv:
        print_graph_ascii()
        sys.exit()
    elif "--mermaid" in sys.argv:
        print_graph_mermaid()
        sys.exit()
    elif "--png" in sys.argv:
        export_graph_png()
        sys.exit()
    while True:
        ui = input("\nUser: ")
        if ui.lower() in ["quit", "exit", "q"]:
            print("👋 Goodbye!")
            break
        run_conversation(ui)