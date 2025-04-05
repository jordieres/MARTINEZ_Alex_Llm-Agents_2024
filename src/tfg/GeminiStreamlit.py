from langchain import hub
from langchain.agents import Tool, create_react_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.utilities import GoogleSerperAPIWrapper
import os
from typing import TypedDict, Annotated, Union
from langchain_core.agents import AgentAction, AgentFinish
from langchain_core.messages import BaseMessage
import operator
from typing import TypedDict, Annotated
from langchain_core.agents import AgentFinish
from langgraph.prebuilt.tool_executor import ToolExecutor
from langgraph.prebuilt import ToolInvocation
from langgraph.graph import END, StateGraph
from langchain_core.agents import AgentActionMessageLog
import streamlit as st


# Set up Streamlit page
st.set_page_config(page_title="Gemini Agent", layout="wide")

# Initialize the API key and tool
os.environ["SERPER_API_KEY"] = ""
search = GoogleSerperAPIWrapper()

# Define functions for tools
def toggle_case(word):
    return ''.join([char.upper() if char.islower() else char.lower() for char in word])

def sort_string(string):
    return ''.join(sorted(string))

# Define tools
tools = [
    Tool(name="Search", func=search.run, description="Use for current events queries."),
    Tool(name="Toggle_Case", func=lambda word: toggle_case(word), description="Convert letter cases."),
    Tool(name="Sort_String", func=lambda string: sort_string(string), description="Sort a string alphabetically."),
]

# Initialize LLM
llm = ChatGoogleGenerativeAI(model="gemini-pro", google_api_key="", convert_system_message_to_human=True, verbose=True)
prompt = hub.pull("hwchase17/react")
agent_runnable = create_react_agent(llm, tools, prompt)

# Define agent state class
class AgentState(TypedDict):
    input: str
    chat_history: list
    agent_outcome: Union[AgentAction, AgentFinish, None]
    return_direct: bool
    intermediate_steps: Annotated[list[tuple[AgentAction, str]], operator.add]

# Tool Executor
tool_executor = ToolExecutor(tools)

# Define agent run and tool execution functions
def run_agent(state):
    agent_outcome = agent_runnable.invoke(state)
    return {"agent_outcome": agent_outcome}

def execute_tools(state):
    last_message = state['agent_outcome']
    tool_name = last_message.tool
    arguments = last_message.tool_input if tool_name else {}
    if "return_direct" in arguments:
        del arguments["return_direct"]
    action = ToolInvocation(tool=tool_name, tool_input=arguments)
    response = tool_executor.invoke(action)
    return {"intermediate_steps": [(state['agent_outcome'], response)]}

def should_continue(state):
    last_message = state['agent_outcome']
    if "Action" not in last_message.log:
        return "end"
    return "continue" if not state.get("return_direct", False) else "final"

# Define graph for workflow
workflow = StateGraph(AgentState)
workflow.add_node("agent", run_agent)
workflow.add_node("action", execute_tools)
workflow.add_node("final", execute_tools)
workflow.set_entry_point("agent")
workflow.add_conditional_edges("agent", should_continue, {"continue": "action", "final": "final", "end": END})
workflow.add_edge("action", "agent")
workflow.add_edge("final", END)
app = workflow.compile()

# Main function to run the agent in Streamlit
def main():
    st.title("LangGraph Agent + Gemini Pro + Custom Tool + Streamlit")
    input_text = st.text_area("Enter your text:")

    if st.button("Run Agent"):
        inputs = {"input": input_text, "chat_history": [], "return_direct": False}
        results = []
        for s in app.stream(inputs):
            result = list(s.values())[0]
            results.append(result)
            st.write(result)

# Run the main function
if __name__ == "__main__":
    main()
