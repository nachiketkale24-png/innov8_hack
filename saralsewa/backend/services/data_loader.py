import json
import os
from typing import List, Dict, Any

_SCHEMES_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "schemes.json")


def load_schemes() -> List[Dict[str, Any]]:
    """Load government schemes from local JSON file."""
    with open(_SCHEMES_PATH, "r", encoding="utf-8") as f:
        schemes = json.load(f)
    return schemes