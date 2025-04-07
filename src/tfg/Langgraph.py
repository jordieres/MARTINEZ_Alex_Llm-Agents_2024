from langgraph.graph import StateGraph, START, END
from typing import Dict, Annotated
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages
from langchain.memory import ConversationBufferMemory
from CustomAgentRouter import CustomAgentRouter
from Agents.WeatherAgent import WeatherAgent
from Agents.DBAgent import DBAgent
from Agents.CrossrefAgent import CrossrefAgent
from Agents.ElsevierAgent import ElsevierAgent
import transformers
from langchain.schema import HumanMessage
transformers.logging.set_verbosity_error()
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

# Define the state structure with memory
class State(TypedDict):
    messages: Annotated[list, add_messages]
    route: str
    memory: ConversationBufferMemory

def classify_query(state: State) -> Dict[str, str]:
    """
    Uses CustomAgentRouter to classify user input and determine the correct agent.
    """
    user_input = state["messages"][-1].content
    router = CustomAgentRouter()
    category, _ = router.classify_text(user_input)
    return {"route": category}

def route_decision(state: State) -> str:
    """
    Determines the next node based on classification result.
    """
    valid_routes = {"weather", "database", "article title", "article content"}
    return state["route"] if state["route"] in valid_routes else "generic"

# Agent functions with memory integration
def weather_agent(state: State) -> Dict[str, str]:
    user_input = state["messages"][-1].content
    agent = WeatherAgent()
    response = agent.run(user_input)
    state["memory"].save_context({"user_input": user_input}, {"response": response})
    return {"messages": state["messages"] + [{"role": "assistant", "content": response}]}

def db_agent(state: State) -> Dict[str, str]:
    user_input = state["messages"][-1].content
    agent = DBAgent()
    response = agent.run(user_input)
    state["memory"].save_context({"user_input": user_input}, {"response": response})
    return {"messages": state["messages"] + [{"role": "assistant", "content": response}]}

def crossref_agent(state: State) -> Dict[str, str]:
    user_input = state["messages"][-1].content
    agent = CrossrefAgent()
    response = agent.run(user_input)
    state["memory"].save_context({"user_input": user_input}, {"response": response})
    return {"messages": state["messages"] + [{"role": "assistant", "content": response}]}

def elsevier_agent(state: State) -> Dict[str, str]:
    user_input = state["messages"][-1].content
    agent = ElsevierAgent()
    response = agent.run(user_input)
    state["memory"].save_context({"user_input": user_input}, {"response": response})
    return {"messages": state["messages"] + [{"role": "assistant", "content": response}]}

# Define the LangGraph workflow
graph = StateGraph(State)

graph.add_node("classify", classify_query)
graph.add_node("weather", weather_agent)
graph.add_node("database", db_agent)
graph.add_node("crossref", crossref_agent)
graph.add_node("elsevier", elsevier_agent)
graph.add_node("generic", lambda state: {"messages": state["messages"] + [{"role": "assistant", "content": "I'm not sure how to help with that."}]})

graph.add_edge(START, "classify")
graph.add_conditional_edges("classify", route_decision, {
    "weather": "weather",
    "database": "database",
    "article title": "crossref",
    "article content": "elsevier",
    "generic": "generic"
})

graph.add_edge("weather", END)
graph.add_edge("database", END)
graph.add_edge("crossref", END)
graph.add_edge("elsevier", END)
graph.add_edge("generic", END)

compiled_graph = graph.compile()

def run_conversation(user_input: str):
    state = {
        "messages": [{"role": "user", "content": user_input}],
        "memory": ConversationBufferMemory()
    }
    for event in compiled_graph.stream(state):
        for value in event.values():
            if "messages" in value:
                print("Assistant:", value["messages"][-1]["content"])
            else:
                print("Assistant: (No response received)")

if __name__ == "__main__":
    while True:
        user_input = input("User: ")
        if user_input.lower() in ["quit", "exit", "q"]:
            print("Goodbye!")
            break
        run_conversation(user_input)
