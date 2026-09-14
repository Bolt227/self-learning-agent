import json

from openai import OpenAI

from backend.config import OPENAI_API_KEY, MODEL_NAME

client = OpenAI(api_key=OPENAI_API_KEY)


def extract_memory(user_message: str):
    response = client.responses.create(
        model=MODEL_NAME,
        instructions="""
You are a memory extraction system for a personal AI assistant.

Analyze the user's message and identify information that is useful
for future conversations.

Remember:
- preferences
- interests
- goals
- skills
- habits
- stable personal context

Do not remember:
- greetings
- temporary requests
- questions
- general facts
- information that is not about the user

Return ONLY valid JSON using exactly this structure:

{
    "should_remember": true,
    "content": "User prefers Java for competitive programming.",
    "type": "preference",
    "scope": "competitive programming",
    "importance": 0.9
}

The "type" must be one of:
"preference", "interest", "goal", "skill", "habit", "personal_context"

"importance" must be a number between 0 and 1.

If nothing should be remembered, return:

{
    "should_remember": false,
    "content": "",
    "type": "",
    "scope": "",
    "importance": 0
}
""",
        input=user_message
    )

    text = response.output_text.strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {
            "should_remember": False,
            "content": "",
            "type": "",
            "scope": "",
            "importance": 0
        }
