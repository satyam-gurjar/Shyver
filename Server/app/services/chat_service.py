from app.model.chat_memory import get_chat_history, save_message
from app.model.llm_model import generate_response

def process_chat(session_id: str, user_message: str) -> str:
    """
    This function connects memory + LLM.
    Controller calls THIS, not model directly.
    """

    # Get previous messages
    history = get_chat_history(session_id)

    # Build prompt with history
    prompt = ""
    for msg in history:
        prompt += f"{msg['role']}: {msg['content']}\n"

    # Add new user message
    prompt += f"user: {user_message}\nassistant:"

    # Generate response from LLaMA
    assistant_reply = generate_response(prompt)

    # Save both user and assistant messages
    save_message(session_id, "user", user_message)
    save_message(session_id, "assistant", assistant_reply)

    return assistant_reply
