from backend.agent.state import AgentState
from backend.agent.agent import run_agent
from backend.retrieval.contextual_retrieval import search_memories_contextually


def retrieve_memory(state: AgentState) -> AgentState:
    user_id = state["user_id"]
    message = state["message"]

    memories = search_memories_contextually(
        user_id,
        message
    )

    state["memories"] = memories

    return state


def decide_next_action(state: AgentState) -> AgentState:
    message = state["message"].lower()

    state["needs_memory"] = True
    state["needs_rag"] = False
    state["needs_tool"] = False

    return state


def run_workflow(state: AgentState) -> AgentState:
    state = decide_next_action(state)

    if state.get("needs_memory"):
        state = retrieve_memory(state)

    state = run_agent(state)

    return state