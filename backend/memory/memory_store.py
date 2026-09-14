import json
import os
from datetime import datetime, timezone


MEMORY_FILE = "data/memory.json"


def current_timestamp():
    return datetime.now(timezone.utc).isoformat()


def load_memories(user_id: str):
    if not os.path.exists(MEMORY_FILE):
        return []

    with open(MEMORY_FILE, "r") as file:
        data = json.load(file)

    return data.get(user_id, [])


def save_memory(user_id: str, memory: dict):
    os.makedirs(
        os.path.dirname(MEMORY_FILE) or ".",
        exist_ok=True
    )

    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as file:
            data = json.load(file)
    else:
        data = {}

    if user_id not in data:
        data[user_id] = []

    existing_memories = data[user_id]

    now = current_timestamp()

    memory["created_at"] = memory.get("created_at", now)
    memory["updated_at"] = now
    memory["confidence"] = memory.get(
        "confidence",
        memory.get("importance", 0.0)
    )

    for index, existing in enumerate(existing_memories):

        same_content = (
            existing.get("content", "").strip().lower()
            == memory.get("content", "").strip().lower()
        )

        same_type_scope = (
            existing.get("type", "") == memory.get("type", "")
            and existing.get("scope", "").strip().lower()
            == memory.get("scope", "").strip().lower()
        )

        if same_content:
            existing["updated_at"] = now
            existing["last_used_at"] = existing.get(
                "last_used_at",
                None
            )
            existing_memories[index] = existing
            break

        if same_type_scope:
            memory["created_at"] = existing.get(
                "created_at",
                now
            )

            memory["last_used_at"] = existing.get(
                "last_used_at",
                None
            )

            existing_memories[index] = memory
            break

    else:
        memory["last_used_at"] = None
        existing_memories.append(memory)

    with open(MEMORY_FILE, "w") as file:
        json.dump(data, file, indent=4)


def get_all_memories(user_id: str):
    return load_memories(user_id)

def mark_memory_used(user_id: str, memory_content: str):
    if not os.path.exists(MEMORY_FILE):
        return

    with open(MEMORY_FILE, "r") as file:
        data = json.load(file)

    memories = data.get(user_id, [])

    for memory in memories:
        if (
            memory.get("content", "").strip().lower()
            == memory_content.strip().lower()
        ):
            memory["last_used_at"] = current_timestamp()
            break

    with open(MEMORY_FILE, "w") as file:
        json.dump(data, file, indent=4)