from backend.memory.memory_store import load_memories


def search_memories(user_id: str, query: str):
    memories = load_memories(user_id)

    if not memories:
        return []

    query_words = set(query.lower().split())

    scored_memories = []

    for memory in memories:
        text = memory.get("content", "").lower()

        score = sum(
            1 for word in query_words
            if word in text
        )

        if score > 0:
            scored_memories.append((score, memory))

    scored_memories.sort(
        key=lambda x: x[0],
        reverse=True
    )

    return [memory for score, memory in scored_memories[:5]]
