import os
import yaml

def load_config() -> dict:
    """Load the YAML configuration file."""
    base_path = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(base_path, "../../../.config.yaml")
    if not os.path.isfile(config_path):
        raise FileNotFoundError(f"Config file not found at: {config_path}")
    with open(config_path, "r") as f:
        return yaml.safe_load(f)
    
def get_config_value(key: str, default: str = None) -> str:
    """Get a config value from environment, falling back to YAML."""
    return os.environ.get(key) or load_config().get(key, default)
