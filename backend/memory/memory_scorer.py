from datetime import datetime, timezone


def recency_score(memory: dict) -> float:
    timestamp = memory.get("last_used_at") or memory.get("updated_at")

    if not timestamp:
        return 0.0

    try:
        last_time = datetime.fromisoformat(timestamp)
        now = datetime.now(timezone.utc)

        age_days = max(
            0.0,
            (now - last_time).total_seconds() / 86400
        )

        return 1.0 / (1.0 + age_days)

    except (ValueError, TypeError):
        return 0.0


def score_memory(
    memory: dict,
    query: str,
    contextual_score: float = 0.0
) -> float:

    importance = float(
        memory.get("importance", 0.0)
    )

    confidence = float(
        memory.get(
            "confidence",
            importance
        )
    )

    recency = recency_score(memory)

    score = contextual_score

    score += importance * 0.5
    score += confidence * 0.3
    score += recency * 0.2

    return score


def resolve_memory_conflicts(
    memories: list[dict]
) -> list[dict]:

    if not memories:
        return []

    resolved = {}

    for memory in memories:
        memory_type = memory.get("type", "")
        scope = memory.get("scope", "").lower()

        key = (memory_type, scope)

        if key not in resolved:
            resolved[key] = memory
            continue

        existing = resolved[key]

        if float(
            memory.get("importance", 0)
        ) > float(
            existing.get("importance", 0)
        ):
            resolved[key] = memory

    return list(resolved.values())