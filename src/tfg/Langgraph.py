from langgraph.graph import StateGraph, START, END
from typing import Dict, Annotated
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages
from langchain.memory import ConversationBufferMemory
from Agents.WeatherAgent import WeatherAgent
from Agents.DBAgent import DBAgent
from Agents.CrossrefAgent import CrossrefAgent
from Agents.ElsevierAgent import ElsevierAgent
from Agents.PlannerAgent import PlannerAgent  # New planner agent
import transformers
import warnings

transformers.logging.set_verbosity_error()
warnings.filterwarnings("ignore", category=DeprecationWarning)

# Updated state structure to include explanations
class State(TypedDict):
    messages: Annotated[list, add_messages]
    steps: Annotated[list, add_messages]  # List of step results
    explanation: list[str]                # Trace log for reasoning
    memory: ConversationBufferMemory

# Step runner to execute each planned step using appropriate agent
def step_executor(state: State) -> Dict:
    last_step = state["steps"][-1] if state["steps"] else {}
    user_input = last_step.get("content", "")
    route = last_step.get("route", "")
    explanation = state.get("explanation", [])

    agent_map = {
        "weather": WeatherAgent,
        "database": DBAgent,
        "article title": CrossrefAgent,
        "article content": ElsevierAgent,
    }

    if route in agent_map:
        agent = agent_map[route]()
        response = agent.run(user_input)
        state["memory"].save_context({"user_input": user_input}, {"response": response})
        explanation.append(f"✅ Step '{user_input}' executed with agent '{route}'.")
        return {
            "steps": state["steps"] + [{"role": "assistant", "content": response}],
            "explanation": explanation
        }
    else:
        explanation.append(f"❓ No agent matched for: '{user_input}'")
        return {
            "steps": state["steps"] + [{"role": "assistant", "content": "I'm not sure how to help with that."}],
            "explanation": explanation
        }

# Planner agent to decide flow
planner = PlannerAgent()

def planning_node(state: State) -> Dict:
    user_prompt = state["messages"][-1].content
    plan, trace = planner.plan(user_prompt)
    return {
        "steps": plan,
        "explanation": trace
    }

# Define the LangGraph workflow
graph = StateGraph(State)
graph.add_node("plan", planning_node)
graph.add_node("execute_step", step_executor)

# Transitions
graph.add_edge(START, "plan")
# Iterative execution for each step in the plan
graph.add_conditional_edges("execute_step", lambda s: END if len(s["steps"]) >= len(s["explanation"]) else "execute_step")
graph.add_edge("plan", "execute_step")

compiled_graph = graph.compile()

# Run function
def run_conversation(user_input: str):
    state = {
        "messages": [{"role": "user", "content": user_input}],
        "steps": [],
        "explanation": [],
        "memory": ConversationBufferMemory()
    }
    for event in compiled_graph.stream(state):
        for value in event.values():
            if "steps" in value:
                print("Assistant:", value["steps"][-1].content)
            if "explanation" in value:
                print("\n[Reasoning Trace]")
                for line in value["explanation"]:
                    print("-", line)

if __name__ == "__main__":
    while True:
        user_input = input("User: ")
        if user_input.lower() in ["quit", "exit", "q"]:
            print("Goodbye!")
            break
        run_conversation(user_input)