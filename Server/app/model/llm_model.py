from langchain_community.llms import Ollama
import random

# -------------------------------
# Initialize Phi-3 via Ollama
# -------------------------------
try:
    llm = Ollama(
        model="phi3:latest",                # ✅ EXACT name from `ollama list`
        base_url="http://localhost:11434",
        temperature=0.5,                    # Phi likes lower temperature
    )
    OLLAMA_AVAILABLE = True
except Exception as e:
    print(f"Ollama not available: {e}")
    OLLAMA_AVAILABLE = False


# -------------------------------
# Mock responses (fallback)
# -------------------------------
MOCK_RESPONSES = [
    "Ollama server is not running on localhost:11434. This is a default fallback reply.",
    "I'm currently in offline mode because the local Ollama server is not reachable.",
    "Fallback response: please start Ollama (port 11434) to get real AI answers.",
]


def generate_response(prompt: str) -> str:
    """
    Generate response using Phi3 locally.
    """
    try:
        if OLLAMA_AVAILABLE:
            return llm.invoke(prompt)

        # Ollama was not available at import time
        return random.choice(MOCK_RESPONSES)

    except Exception as e:
        # Most likely Ollama is not running or became unreachable.
        # Log once per call and return a friendly default message
        print(f"Ollama connection error, using fallback: {e}")
        return random.choice(MOCK_RESPONSES)
