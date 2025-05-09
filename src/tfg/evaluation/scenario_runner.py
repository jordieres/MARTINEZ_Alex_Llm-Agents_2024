import os
import sys
import io
from contextlib import redirect_stdout

# Add the root path of your modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from System.main import run_conversation
from evaluator import evaluate_response 

BASE_DIR = os.path.dirname(__file__)
SCENARIO_FILE = os.path.join(os.path.dirname(__file__), "scenarios", "complex_scenarios.txt")
LOG_DIR = "logs"
METRIC_DIR = "metrics"

os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(METRIC_DIR, exist_ok=True)


def parse_scenarios(file_path):
    """Parses the scenarios file and returns a list of dicts with metadata and prompt"""
    scenarios = []
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Split scenarios using double newlines
    raw_scenarios = content.strip().split("\n\n")
    for block in raw_scenarios:
        lines = block.strip().split("\n")
        scenario = {
            "id": None,
            "difficulty": "unknown",
            "type": "unspecified",
            "requires": [],
            "prompt": "",
        }
        prompt_lines = []
        for line in lines:
            if line.startswith("# scenario_"):
                scenario["id"] = line.strip().replace("# ", "")
            elif line.startswith("# difficulty:"):
                scenario["difficulty"] = line.split(":", 1)[1].strip()
            elif line.startswith("# type:"):
                scenario["type"] = line.split(":", 1)[1].strip()
            elif line.startswith("# requires:"):
                scenario["requires"] = [r.strip() for r in line.split(":", 1)[1].split(",")]
            elif not line.startswith("#"):
                prompt_lines.append(line)
        scenario["prompt"] = " ".join(prompt_lines).strip()
        if scenario["id"] and scenario["prompt"]:
            scenarios.append(scenario)
    return scenarios


def run_and_log(scenario):
    """Runs the conversation and logs the output and metrics"""
    print(f"\n▶️ Running {scenario['id']} [{scenario['difficulty']}]")

    # Redirect stdout to capture printed messages (Thought, Action, etc.)
    stdout_buffer = io.StringIO()
    with redirect_stdout(stdout_buffer):
        result = run_conversation(scenario["prompt"], return_full=True)
    debug_output = stdout_buffer.getvalue()

    # Save log file
    log_path = os.path.join(LOG_DIR, f"{scenario['id']}.log")
    with open(log_path, "w", encoding="utf-8") as f:
        f.write("=== PROMPT ===\n")
        f.write(scenario["prompt"] + "\n\n")

        f.write("=== DEBUG OUTPUT ===\n")
        f.write(debug_output + "\n")

        f.write("=== MESSAGES ===\n")
        for msg in result["messages"]:
            msg_type = msg.__class__.__name__
            content = getattr(msg, "content", "")
            f.write(f"{msg_type}: {content}\n")

        assistant_response = next(
            (m.content for m in reversed(result["messages"]) if m.__class__.__name__ == "AIMessage"),
            "NO ASSISTANT RESPONSE"
        )
        f.write("\n=== FINAL RESPONSE (from last AIMessage) ===\n")
        f.write(assistant_response + "\n")

    # Evaluate metrics
    metrics = evaluate_response(result, scenario["prompt"])
    metric_path = os.path.join(METRIC_DIR, f"{scenario['id']}_metrics.txt")
    with open(metric_path, "w", encoding="utf-8") as f:
        for k, v in metrics.items():
            f.write(f"{k}: {v}\n")

    print(f"✅ Done: Logs → {log_path}, Metrics → {metric_path}")



def run_all():
    """Main loop: parse scenarios and run each"""
    print("Path:", SCENARIO_FILE)
    scenarios = parse_scenarios(SCENARIO_FILE)
    for scenario in scenarios:
        run_and_log(scenario)


if __name__ == "__main__":
    run_all()
