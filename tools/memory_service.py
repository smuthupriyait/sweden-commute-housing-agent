"""
Long-term Memory Bank Service for WorkNest / Sweden Housing Agent.
Handles user preferences, saved filters, and facts across sessions.
Provides CRUD support (Get, Save, Update, Clear).
"""
import os
import json
from typing import Dict, Any, Optional

MEMORY_STORE_FILE = "/config/Desktop/BuildWithGemini/user_memories.json"

DEFAULT_PROFILE = {
    "workplace": "Stockholm Central / City",
    "max_commute_minutes": 35,
    "net_income_sek": 38000,
    "fixed_expenses_sek": 11000,
    "family": "1 adult, 0 children",
    "min_rooms": 1.5,
    "max_rent_sek": 12500,
    "preferred_neighborhoods": ["Arenastaden", "Råsunda", "Huvudsta"],
    "notes": [
        "Prefers quiet suburban rail corridor with low municipal tax",
        "Prefers apartments near commuter train lines in Solna"
    ]
}

class MemoryBankService:
    def __init__(self, filepath: str = MEMORY_STORE_FILE):
        self.filepath = filepath
        self._ensure_store()

    def _ensure_store(self):
        if not os.path.exists(self.filepath):
            with open(self.filepath, "w") as f:
                json.dump({"default_user": DEFAULT_PROFILE}, f, indent=2)

    def get_memories(self, user_id: str = "default_user") -> Dict[str, Any]:
        try:
            with open(self.filepath, "r") as f:
                data = json.load(f)
                user_data = data.get(user_id, {})
                # Merge with default profile keys so no KeyErrors occur
                merged = dict(DEFAULT_PROFILE)
                merged.update(user_data)
                return merged
        except Exception:
            return dict(DEFAULT_PROFILE)

    def save_memory(self, user_id: str, key: str, value: Any):
        try:
            with open(self.filepath, "r") as f:
                data = json.load(f)
        except Exception:
            data = {}
        if user_id not in data:
            data[user_id] = dict(DEFAULT_PROFILE)
        data[user_id][key] = value
        with open(self.filepath, "w") as f:
            json.dump(data, f, indent=2)

    def update_all_memories(self, user_id: str, new_profile: Dict[str, Any]):
        try:
            with open(self.filepath, "r") as f:
                data = json.load(f)
        except Exception:
            data = {}
        data[user_id] = new_profile
        with open(self.filepath, "w") as f:
            json.dump(data, f, indent=2)

    def clear_memories(self, user_id: str = "default_user"):
        try:
            with open(self.filepath, "r") as f:
                data = json.load(f)
        except Exception:
            data = {}
        data[user_id] = {
            "workplace": "Stockholm Central / City",
            "max_commute_minutes": 35,
            "net_income_sek": 38000,
            "fixed_expenses_sek": 11000,
            "family": "1 adult, 0 children",
            "notes": []
        }
        with open(self.filepath, "w") as f:
            json.dump(data, f, indent=2)

memory_bank = MemoryBankService()
