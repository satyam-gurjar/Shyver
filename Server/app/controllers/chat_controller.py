from fastapi import APIRouter, WebSocket, WebSocketDisconnect
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


@router.websocket("/ws")
async def websocket_chat(websocket: WebSocket):
    """WebSocket endpoint for real-time chat.

    Expects messages as JSON objects:
    {"session_id": "<id>", "message": "<text>"}

    Sends back JSON:
    {"response": "<assistant reply>"}
    """

    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_json()
            session_id = data.get("session_id")
            message = data.get("message")

            if not session_id or message is None:
                await websocket.send_json({
                    "error": "session_id and message are required"
                })
                continue

            response = process_chat(
                session_id=session_id,
                user_message=message,
            )

            await websocket.send_json({
                "response": response
            })
    except WebSocketDisconnect:
        # Client disconnected; just end the connection gracefully
        pass
