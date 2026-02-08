# Import FastAPI framework
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import controller (router)
from app.controllers.chat_controller import router as chat_router

# Create FastAPI app instance
# This is the main backend application
app = FastAPI(title="Local LLaMA Chat MVC")

# Add CORS middleware to allow frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register chat routes (controllers)
app.include_router(chat_router)

# When you run:
# uvicorn app.main:app --reload
# this file starts the server
