from typing import Any

from openai import OpenAI

from backend.config import OPENAI_API_KEY, MODEL_NAME
from backend.agent.state import AgentState


client = OpenAI(api_key=OPENAI_API_KEY)


def build_memory_context(memories: list[dict[str, Any]]) -> str:
    if not memories:
        return "No relevant memories found."

    lines = []

    for memory in memories:
        lines.append(
            f"- {memory.get('content', '')} "
            f"(type: {memory.get('type', '')}, "
            f"scope: {memory.get('scope', '')}, "
            f"importance: {memory.get('importance', 0)})"
        )

    return "\n".join(lines)


def run_agent(state: AgentState) -> AgentState:
    messages = state.get("messages", [])
    memories = state.get("memories", [])

    memory_context = build_memory_context(memories)

    instructions = f"""
You are a helpful self-learning personal AI assistant.

Use:
1. The current conversation.
2. Relevant long-term user memories.

Only use memories when they are relevant to the current request.

If multiple memories exist, prefer the memory whose scope
matches the current request more specifically.

Do not invent personal information.

Relevant user memories:
{memory_context}
"""

    response = client.responses.create(
        model=MODEL_NAME,
        instructions=instructions,
        input=messages
    )

    state["response"] = response.output_text

    return state