from fastapi import APIRouter
from app.model.schemas import ChatRequest
from app.services.chat_service import process_chat

# Create router
router = APIRouter()

@router.post("/chat")
def chat_endpoint(request: ChatRequest):
    """
    This is the API endpoint.
    Frontend sends data here.
    """

    # Call service layer
    response = process_chat(
        session_id=request.session_id,
        user_message=request.message
    )

    # Return response as JSON
    return {
        "response": response
    }
