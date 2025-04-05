from openai import OpenAI
import json
import streamlit as st
import logging

# Configure the OpenAI API
api_key = "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"
client = OpenAI(api_key=api_key)

# Initialize logging
logging.basicConfig(level=logging.INFO)

# Define functions for calculations
def add_numbers(a, b):
    return {"result": a + b}

def subtract_numbers(a, b):
    return {"result": a - b}

# Define tools for GPT function calling
tools = [
    {
        "type": "function",
        "function": {
            "name": "add_numbers",
            "description": "Add two numbers together",
            "parameters": {
                "type": "object",
                "properties": {
                    "a": {"type": "number", "description": "First number"},
                    "b": {"type": "number", "description": "Second number"},
                },
                "required": ["a", "b"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "subtract_numbers",
            "description": "Subtract one number from another",
            "parameters": {
                "type": "object",
                "properties": {
                    "a": {"type": "number", "description": "First number"},
                    "b": {"type": "number", "description": "Second number"},
                },
                "required": ["a", "b"],
            },
        },
    },
]
functions = [
    {
        "name": "get_current_weather",
        "description": "Get the current weather in a given location",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "The city and state, e.g. San Francisco, CA"
                },
                "unit": {
                    "type": "string",
                    "enum": ["celsius", "fahrenheit"]
                }
            },
            "required": ["location"]
        }
    }
]

# Handle function calls
def handle_function_call(function_name, arguments):
    if function_name == "add_numbers":
        return add_numbers(arguments.get('a'), arguments.get('b'))
    elif function_name == "subtract_numbers":
        return subtract_numbers(arguments.get("a"), arguments.get("b"))
    else:
        raise ValueError(f"Unknown function: {function_name}")

# GPT-4 function to call and handle the response
def call_gpt():
    response = client.chat.completions.create(
        model="gpt-4-0613",
        messages=st.session_state.messages,  # Use the session's message history
        functions=functions
    )
    print(response)
    message = response.choices[0].message
    if "function_call" in message:
        tool_call = message.function_call
        arguments = json.loads(tool_call.arguments)
        result = handle_function_call(tool_call.name, arguments)
        return f"Function called: {tool_call.name}, Result: {result['result']}"
    else:
        return message.content

# Main Streamlit interface
def main():
    st.title("Math Problem Solver Chatbot")

    # Initialize session state for messages
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "system", "content": "You are a helpful assistant."}  # Invisible system message
        ]

    # Display input for API key
    if api_key:
        user_input = st.chat_input("Enter a math problem (addition or subtraction):")

        if user_input:
            # Add user input to session state for conversation
            st.session_state.messages.append({"role": "user", "content": user_input})

            # Call GPT-4 with the user's input and handle the response
            try:
                response = call_gpt()
                st.session_state.messages.append({"role": "assistant", "content": response})

            except Exception as e:
                st.error(f"Error: {str(e)}")
                logging.error(f"Error during GPT-4 API call: {str(e)}")

        # Loop to display only the user and assistant messages (skip system message)
        for message in st.session_state.messages[1:]:  # Skip the system message
            if message["role"] == "user":
                with st.chat_message("user"):
                    st.markdown(message["content"])
            elif message["role"] == "assistant":
                with st.chat_message("assistant"):
                    st.markdown(message["content"])

    else:
        st.write("Please enter your OpenAI API key to proceed.")

if __name__ == "__main__":
    main()
