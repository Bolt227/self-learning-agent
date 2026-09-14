from backend.agent.agent import run_agent
from backend.memory.memory_extractor import extract_memory

print("=== Test 1: Memory Extractor ===")
msg = "I love competitive programming and I mainly use Python for my projects."
result = extract_memory(msg)
print(f"Input:           {msg}")
print(f"Should Remember: {result['should_remember']}")
print(f"Content:         {result['content']}")
print(f"Type:            {result['type']}")
print(f"Scope:           {result['scope']}")
print(f"Importance:      {result['importance']}")

print()
print("=== Test 2: Agent Response with Memory ===")
messages = [{"role": "user", "content": "What programming language do I prefer?"}]
memories = [{"content": "User mainly uses Python for their projects."}]
response = run_agent(messages, memories=memories)
print(f"Response: {response}")
