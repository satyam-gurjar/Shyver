# Simple in-memory storage
# Key = session_id
# Value = list of messages
chat_sessions = {}

def get_chat_history(session_id: str):
    """
    Returns previous messages for a session.
    If session does not exist, return empty list.
    """
    return chat_sessions.get(session_id, [])

def save_message(session_id: str, role: str, content: str):
    """
    Save a message to memory.
    role = 'user' or 'assistant'
    content = message text
    """

    # Create session if not exists
    if session_id not in chat_sessions:
        chat_sessions[session_id] = []

    # Append new message
    chat_sessions[session_id].append({
        "role": role,
        "content": content
    })
