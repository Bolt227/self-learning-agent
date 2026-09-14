import json
import os

MEMORY_FILE = "data/memory.json"


def load_memories(user_id: str):
    if not os.path.exists(MEMORY_FILE):
        return []

    with open(MEMORY_FILE, "r") as file:
        data = json.load(file)

    return data.get(user_id, [])


def save_memory(user_id: str, memory: dict):
    os.makedirs(os.path.dirname(MEMORY_FILE) or ".", exist_ok=True)

    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as file:
            data = json.load(file)
    else:
        data = {}

    if user_id not in data:
        data[user_id] = []

    existing_memories = data[user_id]

    for existing in existing_memories:
        if (
            existing.get("content", "").strip().lower()
            == memory.get("content", "").strip().lower()
        ):
            return

    existing_memories.append(memory)

    with open(MEMORY_FILE, "w") as file:
        json.dump(data, file, indent=4)


def get_all_memories(user_id: str):
    return load_memories(user_id)