.. Agentic AI: An Exploratory And Functional Approach documentation master file, created by
   sphinx-quickstart on Thu May 15 18:18:37 2025.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Agentic AI: An Exploratory And Functional Approach documentation
================================================================

This documentation presents the design, architecture, and implementation details of a modular agent-based system developed for the final degree project (TFG). The system combines large language models with external tools for intelligent decision-making in scientific and environmental contexts.

.. toctree::
   :maxdepth: 2
   :caption: Getting Started

   overview
   configuration


.. toctree::
   :maxdepth: 2
   :caption: Modules

   tfg.Agents
   tfg.Tools
   tfg.System
   tfg.evaluation
   tfg.utils
   tfg


Project Structure
=================

The system is structured into the following modules:

- **Agents**: Specialized LLM-based agents for handling specific tasks.
- **Tools**: Interfaces for external APIs and databases.
- **System**: LangGraph pipeline for coordinating agentic reasoning.
- **Evaluation**: Scripts for automatic performance testing.
- **Utils**: Configuration and helper utilities.


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`