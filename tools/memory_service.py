"""
Long-term Memory Bank Service for WorkNest / Sweden Housing Agent.
Handles user preferences and facts across sessions.
"""
import os
import json
from typing import Dict, Any, Optional

MEMORY_STORE_FILE = "/config/Desktop/BuildWithGemini/user_memories.json"

class MemoryBankService:
    def __init__(self, filepath: str = MEMORY_STORE_FILE):
        self.filepath = filepath
        self._ensure_store()

    def _ensure_store(self):
        if not os.path.exists(self.filepath):
            with open(self.filepath, "w") as f:
                json.dump({}, f)

    def get_memories(self, user_id: str = "default_user") -> Dict[str, Any]:
        try:
            with open(self.filepath, "r") as f:
                data = json.load(f)
                return data.get(user_id, {
                    "workplace": "Stockholm Central / City",
                    "max_commute_minutes": 35,
                    "net_income_sek": 38000,
                    "fixed_expenses_sek": 11000,
                    "family": "1 adult, 0 children",
                    "notes": ["Prefers quiet suburban rail corridor with low municipal tax"]
                })
        except Exception:
            return {}

    def save_memory(self, user_id: str, key: str, value: Any):
        try:
            with open(self.filepath, "r") as f:
                data = json.load(f)
        except Exception:
            data = {}
        if user_id not in data:
            data[user_id] = {}
        data[user_id][key] = value
        with open(self.filepath, "w") as f:
            json.dump(data, f, indent=2)

memory_bank = MemoryBankService()
