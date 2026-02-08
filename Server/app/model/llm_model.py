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
    "Running in mock mode. Start Ollama to get real responses.",
    "Phi model is not reachable right now.",
    "Fallback mode active.",
]


def generate_response(prompt: str) -> str:
    """
    Generate response using Phi3 locally.
    """
    try:
        if OLLAMA_AVAILABLE:
            return llm.invoke(prompt)

        return random.choice(MOCK_RESPONSES)

    except Exception as e:
        print(f"Error: {e}")
        return random.choice(MOCK_RESPONSES)
