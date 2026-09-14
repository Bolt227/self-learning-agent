import json
from google import genai
from google.genai import types
from backend.config import GEMINI_API_KEY, MODEL_NAME

# Reuse the same Gemini client
client = genai.Client(api_key=GEMINI_API_KEY)

EXTRACTION_PROMPT = """You are a memory extraction system for a personal AI assistant.

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
"""

_FALLBACK = {
    "should_remember": False,
    "content": "",
    "type": "",
    "scope": "",
    "importance": 0
}


def extract_memory(user_message: str) -> dict:
    """
    Sends a user message to Gemini and extracts any long-term memory
    worth saving about the user.

    Args:
        user_message (str): The raw message from the user.

    Returns:
        dict: A memory dict with should_remember, content, type, scope, importance.
    """
    if not user_message or not user_message.strip():
        return _FALLBACK

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=user_message,
        config=types.GenerateContentConfig(
            system_instruction=EXTRACTION_PROMPT
        )
    )

    text = response.text.strip()

    # Strip markdown code fences if Gemini wraps the JSON in them
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
        text = text.strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return _FALLBACK
