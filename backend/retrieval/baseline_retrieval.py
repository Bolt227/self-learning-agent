from backend.memory.memory_store import load_memories


def search_memories_baseline(user_id: str, query: str):

    memories = load_memories(user_id)

    if not memories:
        return []

    query_words = set(query.lower().split())

    scored_memories = []

    for memory in memories:

        content = memory.get("content", "").lower()

        content_words = set(content.split())

        overlap = len(query_words & content_words)

        if overlap > 0:
            scored_memories.append((overlap, memory))

    scored_memories.sort(
        key=lambda x: x[0],
        reverse=True
    )

    return [
        memory
        for score, memory in scored_memories[:5]
    ]