import os
import sys
from typing import List

# Allow importing from backend when running this file directly
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.config import GEMINI_API_KEY
from google import genai

# Initialize the Gemini client using the API key from config.py
client = genai.Client(api_key=GEMINI_API_KEY)

# Define the default embedding model for Gemini
DEFAULT_EMBEDDING_MODEL = "models/gemini-embedding-2"


def get_embedding(text: str, model: str = DEFAULT_EMBEDDING_MODEL) -> List[float]:
    """
    Generates an embedding vector for a single string using Google's Gemini API.

    Args:
        text (str): The text to convert into an embedding.
        model (str): The Gemini embedding model to use.

    Returns:
        List[float]: The generated embedding vector.

    Raises:
        ValueError: If the input text is empty or purely whitespace.
    """
    if not text or not text.strip():
        raise ValueError("Cannot generate embedding for empty or whitespace-only text.")

    response = client.models.embed_content(
        model=model,
        contents=text
    )
    return response.embeddings[0].values


def get_embeddings(texts: List[str], model: str = DEFAULT_EMBEDDING_MODEL) -> List[List[float]]:
    """
    Generates embedding vectors for a list of strings in a single batch request.

    Args:
        texts (List[str]): A list of text strings to embed.
        model (str): The Gemini embedding model to use.

    Returns:
        List[List[float]]: A list of generated embedding vectors, in the same order as the input.

    Raises:
        ValueError: If the input list is empty.
    """
    if not texts:
        raise ValueError("Cannot generate embeddings for an empty list.")

    return [get_embedding(text, model) for text in texts]


if __name__ == "__main__":
    print("Testing Gemini Embedding Module...")
    test_text = "I enjoy competitive programming using Python."
    
    try:
        # Check if the API key is actually present before attempting the API call
        if not GEMINI_API_KEY:
            print("FAILURE: GEMINI_API_KEY is not configured in .env / config.py")
            sys.exit(1)
            
        print(f"Input text: '{test_text}'")
        
        # Test single embedding function
        vector = get_embedding(test_text)
        
        print("SUCCESS: Embedding generated correctly.")
        print(f"Vector dimension: {len(vector)}")
        print(f"First 5 values: {vector[:5]}")
        
    except Exception as e:
        print(f"FAILURE: An unexpected error occurred: {e}")
