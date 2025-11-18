from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.api.dependencies import get_current_user
from app.models.user import User
from app.schemas import (
    ChatMessage, ChatResponse, ChatHistoryResponse
)
from app.services.ollama_service import ollama_service
from app.services.database_service import db_service
from datetime import datetime

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("/start", response_model=dict)
async def start_chat(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Start a new chat session and get greeting message"""
    # Create new session
    session_id = db_service.get_session_id()
    
    # Get user context for personalization
    user_context = db_service.get_user_context(db, current_user.id)
    
    # Generate greeting message
    greeting = ollama_service.create_greeting_message(user_context)
    
    # Save greeting to history
    db_service.save_message(
        db=db,
        user_id=current_user.id,
        session_id=session_id,
        role="assistant",
        message=greeting
    )
    
    return {
        "session_id": session_id,
        "message": greeting,
        "timestamp": datetime.utcnow()
    }


@router.post("/message", response_model=ChatResponse)
async def send_message(
    message_data: ChatMessage,
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Send a message in a chat session"""
    # Save user message
    db_service.save_message(
        db=db,
        user_id=current_user.id,
        session_id=session_id,
        role="user",
        message=message_data.message
    )
    
    # Get chat history
    history = db_service.get_session_history(db, current_user.id, session_id)
    chat_history = [
        {"role": msg.role, "message": msg.message}
        for msg in history[:-1]  # Exclude the message we just saved
    ]
    
    # Get user context for personalization
    user_context_data = db_service.get_user_context(db, current_user.id)
    user_context_str = ollama_service.create_personalized_context(user_context_data)
    
    # Get response from Ollama
    response = await ollama_service.chat(
        message=message_data.message,
        chat_history=chat_history,
        user_context=user_context_str
    )
    
    # Save assistant response
    db_service.save_message(
        db=db,
        user_id=current_user.id,
        session_id=session_id,
        role="assistant",
        message=response
    )
    
    return ChatResponse(
        role="assistant",
        message=response,
        timestamp=datetime.utcnow()
    )


@router.get("/history/{session_id}", response_model=List[ChatHistoryResponse])
async def get_chat_history(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get chat history for a session"""
    history = db_service.get_session_history(db, current_user.id, session_id)
    return history


@router.get("/sessions", response_model=List[str])
async def get_sessions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all session IDs for current user"""
    sessions = db_service.get_user_sessions(db, current_user.id)
    return sessions
