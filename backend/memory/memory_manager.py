from backend.memory.memory_store import load_memories, save_memory


class MemoryManager:

    def get_l1(self, session_messages, limit=10):
        return session_messages[-limit:]

    def get_l2(self, user_id):
        return load_memories(user_id)

    def add_l2(self, user_id, memory):
        if not memory.get("content"):
            return

        save_memory(user_id, memory)

    def get_memory_context(self, user_id, session_messages):
        return {
            "l1": self.get_l1(session_messages),
            "l2": self.get_l2(user_id)
        }
