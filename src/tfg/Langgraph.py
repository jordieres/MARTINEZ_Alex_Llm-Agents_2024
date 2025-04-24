from Agents.BaseAgent import BaseAgent
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain.schema import HumanMessage
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


weather_agent = WeatherAgent()
db_agent = DBAgent()
cr_agent = CrossrefAgent()
els_agent = ElsevierAgent()

vertexai.init(project="summer-surface-443821-r9", location="europe-southwest1")
llm = ChatVertexAI(model_name="gemini-2.0-flash", temperature=0.28, max_output_tokens=1000, top_p=0.95, top_k=40).bind_tools([weather_tool, influx_tool, crossref_tool, elsevier_tool], tool_choice="auto")

supervisor = create_supervisor(
    agents=[weather_agent, db_agent, cr_agent, els_agent],
    model=llm,
    prompt=(
        "You are a supervisor managing different tools for complex questions about engineering "
        "For weather related tasks use weather_agent "
        "For database related tasks use db_agent "
        "For article content related tasks use els_agent"
        "For article finding tasks use cr_agent"
        "Keep updating on what you are doing and who are you asking for explainability purpose"
        "Give the user the last answer after consulting the needed agents"
    )
)

# Compile supervisor flow
graph = supervisor.compile()

# Execute conversation

def run_conversation(user_input: str):
    print("\n🔄 Starting Supervisor Flow")
    result = graph.invoke({
        "messages": [HumanMessage(content=user_input)]
    })

    # Extract the last assistant message and print the actual response
    final_message = result["messages"][-1]
    if hasattr(final_message, 'content'):
        print("Assistant:", final_message.content)
    else:
        print("Assistant:", final_message)

if __name__ == "__main__":
    while True:
        ui = input("User: ")
        if ui.lower() in ["quit", "exit", "q"]:
            print("👋 Goodbye!")
            break
        run_conversation(ui)