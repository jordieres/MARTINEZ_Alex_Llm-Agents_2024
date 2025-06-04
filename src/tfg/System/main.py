import sys
import os
import transformers
import warnings
from graphviz import Source
from typing import List

# Add the root path of your modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from langchain.schema import HumanMessage, BaseMessage
from langchain_google_vertexai import ChatVertexAI
from tfg.Agents.WeatherAgent import WeatherAgent
from tfg.Agents.DBAgent import DBAgent
from tfg.Agents.CrossrefAgent import CrossrefAgent
from tfg.Agents.ElsevierAgent import ElsevierAgent
from tfg.Agents.CalcAgent import CalculatorAgent
from tfg.Agents.VerifierAgent import VerifierAgent
from tfg.Tools.CrossrefTool import crossref_tool
from tfg.Tools.WeatherTool import weather_tool
from tfg.Tools.ElsevierTool import elsevier_tool
from tfg.Tools.DBTool import influx_tool
from tfg.Tools.CalcTool import calculator_tool
from tfg.utils.config import get_config_value
from langgraph_supervisor import create_supervisor

# Suppress warnings and logs
transformers.logging.set_verbosity_error()
warnings.filterwarnings("ignore", category=DeprecationWarning)

def create_system():
    # Initialize specialized agents
    weather_agent = WeatherAgent()
    db_agent = DBAgent()
    crossref_agent = CrossrefAgent()
    elsevier_agent = ElsevierAgent()
    calculator_agent = CalculatorAgent()
    verifier_agent = VerifierAgent()

    # Initialize LLM with bound tools
    project = get_config_value("project", "default-project")
    location = get_config_value("location", "default-location")
    from vertexai import init
    init(project=project, location=location)

    llm = ChatVertexAI(
        model_name="gemini-2.0-flash",
        temperature=0.28,
        max_output_tokens=1500,
        top_p=0.95,
        top_k=40
    ).bind_tools(
        [weather_tool, influx_tool, crossref_tool, elsevier_tool, calculator_tool],
        tool_choice="auto"
    )

    # Create supervisor with updated prompt
    supervisor = create_supervisor(
        agents=[weather_agent, db_agent, crossref_agent, elsevier_agent, calculator_agent, verifier_agent],
        model=llm,
        prompt=(
            "You are a supervisor managing multiple tools and expert agents to solve technical queries.\n\n"
            "Available agents:\n"
            "- weather_agent: for outdoor temperature queries.\n"
            "- db_agent: for indoor sensor data (temperature, humidity, etc).\n"
            "- calculator_agent: for computing statistics (mean, max, etc).\n"
            "- crossref_agent: for searching scientific article titles.\n"
            "- elsevier_agent: for retrieving article contents.\n"
            "- verifier_agent: for validating the final answer's confidence.\n\n"
            "General context:\n"
            "- The lab environment is located at Universidad Politécnica de Madrid.\n"
            "- If no occupancy info is available, assume standard working hours (9am–5pm).\n"
            "- Always use 'Madrid' as the default external weather location.\n\n"
            "Behavioral guidelines:\n"
            "- Narrate your reasoning before each step.\n"
            "- Chain multiple agents if needed.\n"
            "- Always end the reasoning process by calling verifier_agent to validate the response.\n"
            "- If the verifier returns a low confidence (e.g., below 0.75), revise your plan and retry the query before producing a final answer.\n"
            "- Only return a final_output after a high-confidence verification step has succeeded.\n"
            "- Do not assume sensor data is present; handle failures gracefully and attempt fallbacks.\n"
            "- Always end the reasoning process by calling verifier_agent to validate the response.\n"
            "- If the verifier returns a low confidence (e.g., below 0.5) and an unsatisfactory veredict, revise your plan and retry the query before producing a final answer.\n"
            "- Only return a final_output after a high-confidence verification step has succeeded.\n"

        )
    )

    return supervisor.compile()

def run_conversation(user_input: str, return_full: bool = False):
    print("\nStarting Supervisor Flow")
    graph = create_system()
    memory: List[BaseMessage] = [HumanMessage(content=user_input)]

    result = graph.invoke({"messages": memory})

    if return_full:
        return result

    print("\nFull message trace:")
    for msg in result["messages"]:
        msg_type = msg.__class__.__name__
        if msg_type == "ToolMessage":
            payload = getattr(msg, "tool_response", None) or getattr(msg, "content", "")
            print(f"{msg_type}: Tool response: {payload}")
        else:
            content = getattr(msg, "content", "")
            print(f"{msg_type}: {content}")

    final = result.get("final_output")
    if final:
        print("\nFinal Output:")
        print(final)
    else:
        last = result["messages"][-1]
        fallback = getattr(last, "content", str(last))
        print("\nResponse:")
        print(fallback)

def export_graph_png(output_path="langgraph_diagram.png"):
    graph = create_system().get_graph()
    dot_source = graph.draw_png()
    s = Source(dot_source)
    s.render(output_path, format="png", cleanup=True)
    print(f"✅ LangGraph diagram exported as: {output_path}")

def print_graph_ascii():
    graph = create_system().get_graph()
    graph.print_ascii()

def print_graph_mermaid():
    graph = create_system().get_graph()
    print(graph.draw_mermaid())

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
