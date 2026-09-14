import os
import requests
from dotenv import load_dotenv

from backend.config import MODEL_NAME

load_dotenv()

PRISMTRACE_HOST = os.getenv(
    "PRISMTRACE_HOST",
    "https://prism.blockconvey.com"
)
PRISMTRACE_PROJECT_ID = os.getenv("PRISMTRACE_PROJECT_ID")
PRISMTRACE_API_KEY = os.getenv("PRISMTRACE_API_KEY")


def send_trace(
    input_message,
    output_message,
    latency_ms,
    session_id=None,
    user_id=None,
    metadata=None,
):
    if not PRISMTRACE_PROJECT_ID or not PRISMTRACE_API_KEY:
        print("PRISM: missing project ID or API key")
        return None

    payload = {
        "project_id": PRISMTRACE_PROJECT_ID,
        "model": MODEL_NAME,
        "input_messages": [
            {
                "role": "user",
                "content": input_message,
            }
        ],
        "output_message": output_message,
        "latency_ms": int(latency_ms),
        "session_id": session_id,
        "user_identifier": user_id,
        "agent_id": "self-learning-agent",
        "agent_name": "Self-Learning Personal AI Agent",
        "metadata": metadata or {},
    }

    try:
        response = requests.post(
            f"{PRISMTRACE_HOST.rstrip('/')}/api/traces",
            headers={
                "X-PRISMtrace-Key": PRISMTRACE_API_KEY,
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=10,
        )

        if not response.ok:
            print(
                f"PRISM trace failed: "
                f"{response.status_code} {response.text}"
            )
            return None

        result = response.json()

        print(
            f"PRISM trace recorded: "
            f"{result.get('id', 'unknown')}"
        )

        return result

    except requests.RequestException as e:
        print(f"PRISM connection error: {e}")
        return None
