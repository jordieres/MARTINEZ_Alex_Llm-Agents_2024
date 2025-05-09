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
    If confidence is low, escalate to HITL.
    """
    user_input = state["messages"][-1].content
    router = CustomAgentRouter()
    category, confidence = router.classify_text(user_input)

    if confidence < router.confidence_threshold:
        print(f"⚠️ Low confidence ({confidence:.2f}) - Escalating to HITL")
        return {"route": "hitl", "suggested_category": category}
    
    return {"route":category}

def hitl_decision(state: State) -> Dict[str, str]:
    """
    Human-in-the-Loop (HITL) allows a human to select the correct agent.
    The original user query is preserved and passed to the selected agent.
    """
    # Get the original user query from the conversation history
    original_query = state["messages"][0].content  # First user message in conversation
    suggested_category = state.get("suggested_category", "generic")

    print(f"⚠️ Uncertain classification: Suggested '{suggested_category}', but confidence was too low.")
    print(f"👤 Human input required for: {original_query}")
    
    # Ask human operator to manually select the correct category
    available_categories = ["weather", "database", "article title", "article content", "generic"]
    print(f"Available categories: {', '.join(available_categories)}")
    human_choice = input("Select the correct category: ").strip().lower()

    # Validate input
    if human_choice not in available_categories:
        print("⚠️ Invalid selection. Defaulting to 'generic'.")
        human_choice = "generic"

    return {
        "route": human_choice,
        "original_query": original_query,  # Preserve original query for the agent
    }

def route_decision(state: State) -> str:
    """
    Determines the next node based on classification result.
    Falls back to HITL if classification confidence was low.
    """
    if state["route"] == "hitl":
        return "hitl"  # Ensure it routes to HITL decision node

    valid_routes = {"weather", "database", "article title", "article content"}
    return state["route"] if state["route"] in valid_routes else "generic"

# Agent functions with memory integration
def weather_agent(state: State) -> Dict[str, str]:
    """
    Executes the WeatherAgent and ensures it receives the correct query.
    """
    # Always use original query if available
    user_input = state.get("original_query", state["messages"][-1].content)

    agent = WeatherAgent()
    response = agent.run(user_input)

    # Store in memory
    state["memory"].save_context({"user_input": user_input}, {"response": response})

    return {
        "messages": state["messages"] + [{"role": "assistant", "content": response}]
    }

def db_agent(state: State) -> Dict[str, str]:
    """
    Executes the DBAgent and ensures it receives the correct query.
    """
    # Always use original query if available
    user_input = state.get("original_query", state["messages"][-1].content)

    agent = DBAgent()
    response = agent.run(user_input)

    # Store in memory
    state["memory"].save_context({"user_input": user_input}, {"response": response})

    return {
        "messages": state["messages"] + [{"role": "assistant", "content": response}]
    }

def crossref_agent(state: State) -> Dict[str, str]:
    """
    Executes the Crossref Agent and ensures it receives the correct query.
    """
    # Always use original query if available
    user_input = state.get("original_query", state["messages"][-1].content)

    agent = CrossrefAgent()
    response = agent.run(user_input)

    # Store in memory
    state["memory"].save_context({"user_input": user_input}, {"response": response})

    return {
        "messages": state["messages"] + [{"role": "assistant", "content": response}]
    }

def elsevier_agent(state: State) -> Dict[str, str]:
    """
    Executes the Elsevier Agent and ensures it receives the correct query.
    """
    # Always use original query if available
    user_input = state.get("original_query", state["messages"][-1].content)

    agent = ElsevierAgent()
    response = agent.run(user_input)

    # Store in memory
    state["memory"].save_context({"user_input": user_input}, {"response": response})

    return {
        "messages": state["messages"] + [{"role": "assistant", "content": response}]
    }

# Define the LangGraph workflow
graph = StateGraph(State)

graph.add_node("classify", classify_query)
graph.add_node("hitl", hitl_decision)
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
    "hitl": "hitl",  # Ensures HITL is used for low confidence queries
    "generic": "generic"
})

# Ensure HITL routes directly to the selected agent instead of reclassifying
graph.add_conditional_edges("hitl", lambda state: state["route"], {
    "weather": "weather",
    "database": "database",
    "article title": "crossref",
    "article content": "elsevier",
    "generic": "generic"
})

graph.add_edge("hitl", "classify")  # Once the human decides, re-classify the query
graph.add_edge("weather", END)
graph.add_edge("database", END)
graph.add_edge("crossref", END)
graph.add_edge("elsevier", END)
graph.add_edge("generic", END)

compiled_graph = graph.compile()

def run_conversation(user_input: str):
    """
    Streams the graph execution step-by-step for a given user input.
    """
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

# Example usage
if __name__ == "__main__":
    while True:
        user_input = input("User: ")
        if user_input.lower() in ["quit", "exit", "q"]:
            print("Goodbye!")
            break
        run_conversation(user_input)