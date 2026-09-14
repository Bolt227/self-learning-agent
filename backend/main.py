import time
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional

from backend.agent.agent import run_agent
from backend.memory.memory_extractor import extract_memory
from backend.memory.memory_store import save_memory, load_memories
from backend.retrieval.semantic_search import combined_rerank_search
from backend.rag.rag_pipeline import RAGPipeline

# Import PRISM tracing if available
try:
    from backend.evaluation.prism import send_trace
    PRISM_ENABLED = True
except ImportError:
    PRISM_ENABLED = False

app = FastAPI(
    title="Self-Learning Personal AI Agent",
    description="An agent that learns from conversations and retrieves document knowledge via RAG.",
    version="2.0.0"
)

# Initialize the RAG pipeline once at startup
rag = RAGPipeline()

# In-memory session store
sessions = {}


# ─── Request / Response Models ────────────────────────────────────────────────

class Message(BaseModel):
    role: str   # "user" or "assistant"
    content: str

class ChatRequest(BaseModel):
    user_id: str = "demo_user"
    session_id: str = "default"
    messages: Optional[List[Message]] = None
    message: Optional[str] = None   # Simple single-message mode
    use_rag: Optional[bool] = True
    use_memory: Optional[bool] = True

class ChatResponse(BaseModel):
    response: str
    memories_used: List[str] = []
    rag_chunks_used: List[str] = []
    memory_extracted: Optional[dict] = None

class IngestRequest(BaseModel):
    file_path: str

class IngestResponse(BaseModel):
    success: bool
    message: str


# ─── Routes ──────────────────────────────────────────────────────────────────

@app.get("/")
def root():
    return {"status": "online", "service": "self-learning-agent", "version": "2.0.0"}


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    """
    Main chat endpoint.

    Pipeline:
    1. Extract memory from the latest user message
    2. Save any new memory
    3. Retrieve relevant memories (semantic + contextual reranking)
    4. Retrieve relevant RAG document chunks
    5. Run the Gemini agent with full context
    6. Emit PRISM trace (if enabled)
    7. Return the response
    """
    # Support both simple message mode and full messages list mode
    if request.message:
        if request.session_id not in sessions:
            sessions[request.session_id] = []
        sessions[request.session_id].append({"role": "user", "content": request.message})
        messages = sessions[request.session_id]
        latest_user_msg = request.message
    elif request.messages:
        messages = [{"role": m.role, "content": m.content} for m in request.messages]
        latest_user_msg = next(
            (m["content"] for m in reversed(messages) if m["role"] == "user"), ""
        )
    else:
        raise HTTPException(status_code=400, detail="Provide either 'message' or 'messages'.")

    start_time = time.perf_counter()

    # 1. Extract and save memory
    extracted = None
    if request.use_memory and latest_user_msg:
        try:
            extracted = extract_memory(latest_user_msg)
            if extracted.get("should_remember"):
                save_memory(request.user_id, extracted)
        except Exception:
            extracted = None

    # 2. Retrieve relevant memories (semantic + contextual reranking)
    memories = []
    memories_used = []
    if request.use_memory and latest_user_msg:
        try:
            ranked = combined_rerank_search(request.user_id, latest_user_msg, top_k=5)
            memories = [r["memory"] for r in ranked]
            memories_used = [m.get("content", "") for m in memories]
        except Exception:
            memories = []

    # 3. Retrieve relevant RAG document chunks
    rag_chunks = []
    rag_chunks_used = []
    if request.use_rag and latest_user_msg:
        try:
            rag_results = rag.query(latest_user_msg, top_k=3)
            rag_chunks = rag_results
            rag_chunks_used = [r.get("text", "")[:120] + "..." for r in rag_results]
        except Exception:
            rag_chunks = []

    # 4. Run Gemini agent
    try:
        response = run_agent(messages, memories=memories, rag_chunks=rag_chunks)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent error: {str(e)}")

    latency_ms = int((time.perf_counter() - start_time) * 1000)

    # 5. PRISM tracing (if available)
    if PRISM_ENABLED:
        try:
            send_trace(
                input_message=latest_user_msg,
                output_message=response,
                latency_ms=latency_ms,
                session_id=request.session_id,
                user_id=request.user_id,
                metadata={
                    "agent_version": "gemini-rag-v2",
                    "memory_enabled": request.use_memory,
                    "rag_enabled": request.use_rag,
                    "retrieval": "semantic+contextual"
                }
            )
        except Exception:
            pass  # PRISM tracing is non-critical

    # Update session history
    if request.message:
        sessions[request.session_id].append({"role": "assistant", "content": response})

    return ChatResponse(
        response=response,
        memories_used=memories_used,
        rag_chunks_used=rag_chunks_used,
        memory_extracted=extracted
    )


@app.post("/ingest", response_model=IngestResponse)
def ingest_document(request: IngestRequest):
    """Ingest a document into the RAG vector store."""
    if not os.path.exists(request.file_path):
        raise HTTPException(status_code=404, detail=f"File not found: {request.file_path}")

    success = rag.ingest_document(request.file_path)
    if success:
        return IngestResponse(success=True, message="Document ingested successfully.")
    else:
        return IngestResponse(success=False, message="Failed to ingest document.")


@app.get("/memories/{user_id}")
def get_memories(user_id: str):
    """Returns all stored memories for a given user."""
    memories = load_memories(user_id)
    return {"user_id": user_id, "count": len(memories), "memories": memories}
