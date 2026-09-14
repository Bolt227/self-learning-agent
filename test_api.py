import urllib.request
import json

payload = {
    "user_id": "demo_user",
    "messages": [
        {"role": "user", "content": "I mainly use Python for my projects and I love competitive programming."},
        {"role": "assistant", "content": "That is great! Python is a fantastic choice."},
        {"role": "user", "content": "What programming language do I prefer?"}
    ],
    "use_rag": False,
    "use_memory": True
}

data = json.dumps(payload).encode("utf-8")
req = urllib.request.Request(
    "http://localhost:8000/chat",
    data=data,
    headers={"Content-Type": "application/json"},
    method="POST"
)

with urllib.request.urlopen(req) as res:
    result = json.loads(res.read())

print("=== Chat Response ===")
print(f"Response:         {result['response']}")
print(f"Memories Used:    {result['memories_used']}")
print(f"Memory Extracted: {result['memory_extracted']}")
