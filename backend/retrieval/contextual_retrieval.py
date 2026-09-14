from backend.memory.memory_store import load_memories


STOP_WORDS = {
    "a",
    "an",
    "the",
    "is",
    "am",
    "are",
    "was",
    "were",
    "what",
    "why",
    "how",
    "when",
    "where",
    "who",
    "i",
    "me",
    "my",
    "you",
    "your",
    "for",
    "to",
    "of",
    "in",
    "on",
    "and",
    "or",
    "with",
    "give",
    "tell",
    "explain",
    "write",
    "please",
    "can",
    "could",
    "would",
    "should"
}


CONTEXT_MAP = {

    "competitive programming": [
        "codeforces",
        "leetcode",
        "codechef",
        "hackerrank",
        "competitive programming",
        "contest",
        "algorithm",
        "problem solving",
        "coding problem",
        "competitive"
    ],

    "python": [
        "python",
        "python script",
        "python code",
        "pandas",
        "numpy",
        "django",
        "flask",
        "script",
        "rename files",
        "file handling",
        "automation"
    ],

    "java": [
        "java",
        "java code",
        "spring",
        "spring boot"
    ],

    "machine learning": [
        "machine learning",
        "ml",
        "deep learning",
        "neural network",
        "model",
        "training",
        "dataset",
        "ai"
    ],

    "backend development": [
    "backend",
    "backend development",
    "rest api",
    "api",
    "web api",
    "fastapi",
    "server",
    "server side"
],

    "career and projects": [
        "project",
        "career",
        "goal",
        "profile",
        "work on"
    ],

    "general": []

}


def keyword_matches(text: str, keyword: str):
    text = text.lower()
    keyword = keyword.lower()

    if " " in keyword:
        return keyword in text

    words = set(
        word.strip(".,!?;:'\"()[]{}")
        for word in text.split()
    )

    return keyword in words


def detect_context(query: str):
    detected_contexts = []

    for context, keywords in CONTEXT_MAP.items():

        for keyword in keywords:

            if keyword_matches(query, keyword):
                detected_contexts.append(context)
                break

    return detected_contexts


def meaningful_words(text: str):
    words = set(text.lower().split())

    cleaned_words = set()

    for word in words:
        word = word.strip(".,!?;:'\"()[]{}")

        if word and word not in STOP_WORDS:
            cleaned_words.add(word)

    return cleaned_words


def search_memories_contextually(user_id: str, query: str):

    memories = load_memories(user_id)

    if not memories:
        return []

    detected_contexts = detect_context(query)

    query_words = meaningful_words(query)

    scored_memories = []

    for memory in memories:

        content = memory.get("content", "").lower()
        scope = memory.get("scope", "").lower()
        importance = float(memory.get("importance", 0))

        content_words = meaningful_words(content)
        scope_words = meaningful_words(scope)

        content_overlap = len(query_words & content_words)
        scope_overlap = len(query_words & scope_words)

        score = 0.0

        score += content_overlap * 2.0
        score += scope_overlap * 3.0

        for context in detected_contexts:

            context_keywords = CONTEXT_MAP.get(context, [])

            content_match = any(
                keyword_matches(content, keyword)
                for keyword in context_keywords
            )

            scope_match = any(
                keyword_matches(scope, keyword)
                for keyword in context_keywords
            )

            if content_match:
                score += 10.0

            if scope_match:
                score += 15.0

        score += importance * 0.5

        if score >= 3.0:
            scored_memories.append((score, memory))

    scored_memories.sort(
        key=lambda x: x[0],
        reverse=True
    )

    return [
        memory
        for score, memory in scored_memories[:5]
    ]
