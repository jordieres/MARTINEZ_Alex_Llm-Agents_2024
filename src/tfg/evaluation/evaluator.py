"""
Evaluator module for analyzing system responses per scenario.

This module is used during batch evaluation of LLM agent outputs.
It provides simple heuristic metrics like word count, response length,
and reference detection from the assistant's last message.
"""

def evaluate_response(result: dict, prompt: str) -> dict:
    """
    Evaluates a system result and returns a dictionary of metrics.

    Parameters:
        result (dict): The full result object returned by `run_conversation()`.
        prompt (str): The original input prompt used in the scenario.

    Returns:
        dict: Dictionary with evaluation metrics.
    """
    messages = result.get("messages", [])

    # Find last assistant message
    ai_messages = [m for m in messages if m.__class__.__name__ == "AIMessage"]
    final_response = ai_messages[-1].content if ai_messages else ""

    metrics = {
        "prompt_length_words": len(prompt.split()),
        "output_length_words": len(final_response.split()),
        "num_messages": len(messages),
        "mentioned_references": "reference" in final_response.lower() or "doi" in final_response.lower(),
        "mentions_external_temperature": "exterior temperature" in final_response.lower() or "outside temperature" in final_response.lower(),
        "mentions_internal_temperature": "interior temperature" in final_response.lower() or "indoor temperature" in final_response.lower(),
    }

    return metrics
