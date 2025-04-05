# **Cooperative Agents with Large Language Models**

## **Overview**

This project aims to create an advanced AI-based system utilizing Large Language Models (LLMs) to solve complex industrial and organizational problems. The system is built on a modular architecture composed of multiple specialized agents, each equipped with unique tools to handle specific tasks. The project leverages the capabilities of LLMs for natural language processing, task decomposition, optimization, and more, creating a robust, scalable, and adaptable framework.

## **Project Structure**

The project is organized into several key directories and files:

### **1. `Agents/`**
The `Agents` directory contains the implementation of various specialized agents that form the core of the project. Each agent is designed to handle a particular type of task or problem, making the system modular and extendable.

- **`BaseAgent.py`**: The base class for all agents, defining common methods and attributes that are shared across different agent types.
- **`MemoryAgent.py`**: Implements an agent that maintains and uses memory to enhance decision-making processes over time.
- **`NLPAgent.py`**: Implements an agent specialized in natural language processing tasks like Named Entity Recognition (NER), sentiment analysis, and more.
- **`TaskDecompAgent.py`**: Handles the decomposition of complex tasks into manageable subtasks, which are then processed by other agents.

Each agent in this directory is initialized with custom prompt templates and can be integrated into the broader system via workflows that chain their outputs together.

### **2. `Tools/`**
The `Tools` directory includes various utilities and helper classes that are used by the agents to perform their tasks more efficiently.

- **`DecompTool.py`**: Contains logic to break down complex problems into simpler, manageable tasks. This tool is primarily used by the `TaskDecompAgent`.
- **`SummTool.py`**: Implements methods for summarizing text, including extractive and abstractive summarization techniques, which can be used by the `MemoryAgent` or other agents.
- **`Tools.py`**: A collection of general-purpose utilities that can be used across different agents, providing functions like text processing, data handling, etc.

These tools are designed to be reusable and are integrated into the agents to provide them with the specific capabilities needed for their tasks.