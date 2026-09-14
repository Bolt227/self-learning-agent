from typing import Any

from google import genai
from google.genai import types
from backend.config import GEMINI_API_KEY, MODEL_NAME
from backend.agent.state import AgentState

# Initialize a single shared Gemini client
client = genai.Client(api_key=GEMINI_API_KEY)


def run_agent(messages, memories=None, rag_chunks=None):
    """
    Calls Gemini to generate a response given a conversation history,
    optional long-term user memories, and optional RAG document chunks.

    Args:
        messages: List of message dicts with 'role' and 'content' keys.
                  Also accepts an AgentState dict.
        memories: Optional list of memory dicts from the memory store.
        rag_chunks: Optional list of RAG result dicts from the RAG pipeline.

    Returns:
        str: The generated response text from Gemini.
    """
    # Support being called with an AgentState dict
    if isinstance(messages, dict):
        state = messages
        memories = state.get("memories", [])
        messages = state.get("messages", [])

    # Build memory context block
    memory_context = ""
    if memories:
        memory_context = "\n\nRelevant user memories:\n"
        for memory in memories:
            memory_context += (
                f"- {memory.get('content', '')} "
                f"(type: {memory.get('type', '')}, "
                f"scope: {memory.get('scope', '')}, "
                f"importance: {memory.get('importance', 0)})\n"
            )

    # Build RAG document context block
    rag_context = ""
    if rag_chunks:
        rag_context = "\n\nRelevant document knowledge:\n"
        for chunk in rag_chunks:
            source = chunk.get("source", "unknown")
            text = chunk.get("text", "")
            rag_context += f"[Source: {source}]\n{text}\n\n"

    # Compose the system instruction
    system_instruction = f"""You are a helpful self-learning personal AI assistant.

Use the conversation history, relevant user memories, and any retrieved
document knowledge to answer the user's request accurately.

Only use memories when they are relevant to the current request.

If multiple memories exist, prefer the memory whose scope
matches the current request more specifically.

Do not invent personal information that is not present
in the conversation, memories, or retrieved documents.
{memory_context}
{rag_context}
"""

    # Convert message history into Gemini Content objects
    gemini_contents = []
    for msg in messages:
        role = msg.get("role", "user")
        content = msg.get("content", "")

        # Gemini uses 'model' instead of 'assistant'
        if role == "assistant":
            role = "model"

        gemini_contents.append(
            types.Content(
                role=role,
                parts=[types.Part(text=content)]
            )
        )

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=gemini_contents,
        config=types.GenerateContentConfig(
            system_instruction=system_instruction
        )
    )

    return response.text
