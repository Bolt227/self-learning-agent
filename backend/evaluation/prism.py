import os
import time
import requests
from threading import Thread
from dotenv import load_dotenv

load_dotenv()

PRISMTRACE_HOST = os.getenv("PRISMTRACE_HOST")
PRISMTRACE_PROJECT_ID = os.getenv("PRISMTRACE_PROJECT_ID")
PRISMTRACE_API_KEY = os.getenv("PRISMTRACE_API_KEY")


def send_trace(
    input_message,
    output_message,
    latency_ms,
    session_id=None,
    user_id=None,
    metadata=None
):
    if not PRISMTRACE_HOST or not PRISMTRACE_PROJECT_ID or not PRISMTRACE_API_KEY:
        return

    payload = {
        "project_id": PRISMTRACE_PROJECT_ID,
        "model": "gpt-5.6-luna",
        "input_messages": [
            {
                "role": "user",
                "content": input_message
            }
        ],
        "output_message": output_message,
        "latency_ms": latency_ms,
        "session_id": session_id,
        "user_id": user_id,
        "agent_id": "self-learning-agent",
        "metadata": metadata or {}
    }

    def _send():
        try:
            requests.post(
                f"{PRISMTRACE_HOST}/api/traces",
                headers={
                    "X-PRISMtrace-Key": PRISMTRACE_API_KEY,
                    "Content-Type": "application/json"
                },
                json=payload,
                timeout=10
            )
        except Exception:
            pass

    Thread(target=_send, daemon=True).start()