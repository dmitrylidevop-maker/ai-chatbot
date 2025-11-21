from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime
import uuid
from app.models.user import User, UserDetails, PersonalFact, ChatHistory
from app.schemas import (
    UserDetailsCreate, UserDetailsUpdate,
    PersonalFactCreate, PersonalFactUpdate
)
from app.services.base import BaseService


class DatabaseService(BaseService):
    """Service for database operations"""
    
    async def initialize(self) -> bool:
        """Initialize database service"""
        return True
    
    async def health_check(self) -> bool:
        """Check database health"""
        return True
    
    # User Details operations
    def get_user_details(self, db: Session, user_id: str) -> Optional[UserDetails]:
        """Get user details"""
        return db.query(UserDetails).filter(UserDetails.user_id == user_id).first()
    
    def create_user_details(
        self,
        db: Session,
        user_id: str,
        details: UserDetailsCreate
    ) -> UserDetails:
        """Create user details"""
        db_details = UserDetails(user_id=user_id, **details.model_dump())
        db.add(db_details)
        db.commit()
        db.refresh(db_details)
        return db_details
    
    def update_user_details(
        self,
        db: Session,
        user_id: str,
        details: UserDetailsUpdate
    ) -> Optional[UserDetails]:
        """Update user details"""
        db_details = self.get_user_details(db, user_id)
        if not db_details:
            return None
        
        for key, value in details.model_dump(exclude_unset=True).items():
            setattr(db_details, key, value)
        
        db.commit()
        db.refresh(db_details)
        return db_details
    
    # Personal Facts operations
    def get_personal_facts(self, db: Session, user_id: str) -> List[PersonalFact]:
        """Get all personal facts for a user"""
        return db.query(PersonalFact).filter(PersonalFact.user_id == user_id).all()
    
    def get_personal_fact(
        self,
        db: Session,
        user_id: str,
        fact_key: str
    ) -> Optional[PersonalFact]:
        """Get a specific personal fact"""
        return db.query(PersonalFact).filter(
            PersonalFact.user_id == user_id,
            PersonalFact.fact_key == fact_key
        ).first()
    
    def create_personal_fact(
        self,
        db: Session,
        user_id: str,
        fact: PersonalFactCreate
    ) -> PersonalFact:
        """Create a personal fact"""
        db_fact = PersonalFact(user_id=user_id, **fact.model_dump())
        db.add(db_fact)
        db.commit()
        db.refresh(db_fact)
        return db_fact
    
    def update_personal_fact(
        self,
        db: Session,
        user_id: str,
        fact_key: str,
        fact: PersonalFactUpdate
    ) -> Optional[PersonalFact]:
        """Update a personal fact"""
        db_fact = self.get_personal_fact(db, user_id, fact_key)
        if not db_fact:
            return None
        
        db_fact.fact_value = fact.fact_value
        db.commit()
        db.refresh(db_fact)
        return db_fact
    
    def delete_personal_fact(
        self,
        db: Session,
        user_id: str,
        fact_key: str
    ) -> bool:
        """Delete a personal fact"""
        db_fact = self.get_personal_fact(db, user_id, fact_key)
        if not db_fact:
            return False
        
        db.delete(db_fact)
        db.commit()
        return True
    
    # Chat History operations
    def get_session_id(self) -> str:
        """Generate a new session ID"""
        return str(uuid.uuid4())
    
    def save_message(
        self,
        db: Session,
        user_id: str,
        session_id: str,
        role: str,
        message: str
    ) -> ChatHistory:
        """Save a chat message"""
        db_message = ChatHistory(
            user_id=user_id,
            session_id=session_id,
            role=role,
            message=message
        )
        db.add(db_message)
        db.commit()
        db.refresh(db_message)
        return db_message
    
    def get_session_history(
        self,
        db: Session,
        user_id: str,
        session_id: str,
        limit: int = 50
    ) -> List[ChatHistory]:
        """Get chat history for a session"""
        return db.query(ChatHistory).filter(
            ChatHistory.user_id == user_id,
            ChatHistory.session_id == session_id
        ).order_by(ChatHistory.created_at.asc()).limit(limit).all()
    
    def get_user_sessions(
        self,
        db: Session,
        user_id: str
    ) -> List[str]:
        """Get all session IDs for a user"""
        sessions = db.query(ChatHistory.session_id).filter(
            ChatHistory.user_id == user_id
        ).distinct().all()
        return [s[0] for s in sessions]
    
    def get_user_context(self, db: Session, user_id: str) -> Dict[str, Any]:
        """Get full user context for personalization"""
        context = {}
        
        # Get user details
        user_details = self.get_user_details(db, user_id)
        if user_details:
            context['user_details'] = {
                'full_name': user_details.full_name,
                'email': user_details.email,
                'phone': user_details.phone,
                'bio': user_details.bio
            }
        
        # Get personal facts
        personal_facts = self.get_personal_facts(db, user_id)
        context['personal_facts'] = [
            {
                'fact_key': fact.fact_key,
                'fact_value': fact.fact_value
            }
            for fact in personal_facts
        ]
        
        # Extract preferred language if exists
        from app.config import get_settings
        settings = get_settings()
        context['preferred_language'] = settings.DEFAULT_LANGUAGE
        for fact in personal_facts:
            if fact.fact_key.lower() in ['язык', 'language', 'preferred_language']:
                context['preferred_language'] = fact.fact_value
                break
        
        return context


# Singleton instance
db_service = DatabaseService()
