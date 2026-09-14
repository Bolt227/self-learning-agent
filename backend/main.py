from fastapi import FastAPI
from pydantic import BaseModel

from backend.agent.orchestrator import run_workflow
from backend.memory.memory_extractor import extract_memory
from backend.memory.memory_manager import MemoryManager


app = FastAPI(title="Self-Learning Agent")

sessions = {}
memory_manager = MemoryManager()


class ChatRequest(BaseModel):
    user_id: str = "demo_user"
    session_id: str
    message: str


class ChatResponse(BaseModel):
    response: str


@app.get("/")
def root():
    return {
        "status": "online",
        "service": "self-learning-agent"
    }


@app.get("/memories/{user_id}")
def get_memories(user_id: str):
    return {
        "user_id": user_id,
        "memories": memory_manager.get_l2(user_id)
    }


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):

    if request.session_id not in sessions:
        sessions[request.session_id] = []

    session_messages = sessions[request.session_id]

    session_messages.append({
        "role": "user",
        "content": request.message
    })

    memory_result = extract_memory(request.message)

    if memory_result.get("should_remember"):

        memory_manager.add_l2(
            request.user_id,
            {
                "content": memory_result["content"],
                "type": memory_result["type"],
                "scope": memory_result["scope"],
                "importance": memory_result["importance"],
                "source": request.message
            }
        )

    state = {
        "user_id": request.user_id,
        "session_id": request.session_id,
        "message": request.message,
        "messages": memory_manager.get_l1(session_messages)
    }

    state = run_workflow(state)

    response = state["response"]

    session_messages.append({
        "role": "assistant",
        "content": response
    })

    return ChatResponse(response=response)