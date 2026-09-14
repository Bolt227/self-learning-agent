from openai import OpenAI

from backend.config import OPENAI_API_KEY, MODEL_NAME


client = OpenAI(api_key=OPENAI_API_KEY)


def run_agent(messages, memories=None):

    memory_context = ""

    if memories:
        memory_context = "\n\nRelevant user memories:\n"

        for memory in memories:
            memory_context += f"- {memory.get('content', '')}\n"

    response = client.responses.create(
        model=MODEL_NAME,
        instructions=f"""
You are a helpful personal AI assistant.

Use the conversation history and relevant user memories
to answer the user's request.

Relevant user memories:
{memory_context}

Use memories only when they are relevant to the current request.

Do not invent personal information that is not present
in the conversation or memories.
""",
        input=messages
    )

    return response.output_text