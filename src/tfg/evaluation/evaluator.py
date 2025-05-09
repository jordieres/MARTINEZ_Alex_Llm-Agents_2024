"""
Evaluator module for analyzing system responses per scenario.

This module is used during batch evaluation of LLM agent outputs.
It provides simple heuristic metrics like word count, response length,
and reference detection from the assistant's last message.
"""

def evaluate_response(result, original_prompt):
    """
    Evaluates the quality of the system's response with detailed metrics.

    Args:
        result (dict): The full result returned by the LangGraph.
        original_prompt (str): The original scenario prompt.

    Returns:
        dict: Dictionary containing multiple evaluation metrics.
    """
    # Extract all assistant messages
    all_content = "\n".join(
        getattr(m, "content", "") for m in result["messages"]
        if hasattr(m, "content")
    ).lower()

    # Get last AI message
    last_ai = next(
        (m.content for m in reversed(result["messages"]) if m.__class__.__name__ == "AIMessage"),
        ""
    )

    # Track which agents are used and their order
    agent_aliases = {
        "weather_agent": ["weather_agent"],
        "db_agent": ["db_agent"],
        "crossref_agent": ["crossref_agent", "cr_agent"],
        "elsevier_agent": ["elsevier_agent", "els_agent"],
        "calculator_agent": ["calculator_agent"],
    }

    used_agents = []
    for agent, aliases in agent_aliases.items():
        for alias in aliases:
            if alias in all_content and agent not in used_agents:
                used_agents.append(agent)
                break

    # Prepare metrics
    metrics = {
        "length_chars": len(last_ai),
        "responds_to_prompt": "yes" if any(kw in last_ai.lower() for kw in ["temperature", "data", "estimate", "value", "result", "information"]) else "no",
        "contains_numerical_value": any(char.isdigit() for char in last_ai),
        "agent_count": len(used_agents),
        "agent_sequence": ", ".join(used_agents),
    }

    # Individual agent usage
    for agent in agent_aliases:
        metrics[f"uses_{agent}"] = agent in used_agents

    return metrics
