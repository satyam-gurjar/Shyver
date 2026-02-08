from pydantic import BaseModel

# This defines what data the API expects from frontend
class ChatRequest(BaseModel):
    # session_id helps track conversation
    session_id: str

    # user message text
    message: str
