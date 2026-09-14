from typing import Any, TypedDict


class AgentState(TypedDict, total=False):
    user_id: str
    session_id: str
    message: str

    messages: list[dict[str, Any]]

    memories: list[dict[str, Any]]
    retrieved_documents: list[dict[str, Any]]

    tool_calls: list[dict[str, Any]]
    tool_results: list[dict[str, Any]]

    response: str

    context_type: str
    needs_memory: bool
    needs_rag: bool
    needs_tool: bool

    error: str