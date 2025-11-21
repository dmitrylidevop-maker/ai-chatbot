from typing import Dict, Any, Optional
from app.services.base import BaseService
from app.services.database_service import db_service
from app.services.ollama_service import ollama_service
from app.config import get_settings
from app.database import SessionLocal

settings = get_settings()


class TelegramService(BaseService):
    """Service for managing Telegram bot interactions with database and LLM"""
    
    def __init__(self):
        self.user_sessions: Dict[int, str] = {}  # telegram_id -> session_id mapping
    
    async def initialize(self) -> bool:
        """Initialize Telegram service"""
        try:
            return True
        except Exception as e:
            print(f"Error initializing Telegram service: {e}")
            return False
    
    async def health_check(self) -> bool:
        """Check if Telegram service is healthy"""
        return True
    
    async def is_new_user(self, telegram_id: int) -> bool:
        """Check if user is new (not registered yet)"""
        db = SessionLocal()
        try:
            user = db_service.get_user_by_telegram_id(db, telegram_id)
            return user is None
        except Exception as e:
            print(f"Error checking if user is new: {e}")
            return True
        finally:
            db.close()
    
    async def register_new_user(
        self,
        telegram_id: int,
        username: str = None,
        full_name: str = None,
        age: str = None,
        interests: str = None,
        language: str = None,
        bio: str = None
    ) -> Optional[str]:
        """Register new user with personalization data"""
        db = SessionLocal()
        try:
            # Create new user
            user_data = {
                "username": username or f"tg_{telegram_id}",
                "password": f"telegram_{telegram_id}"  # Auto-generated password
            }
            
            new_user = db_service.create_user(db, user_data)
            
            if not new_user:
                return None
            
            # Store telegram_id in personal facts
            from app.schemas import PersonalFactCreate, UserDetailsCreate
            
            db_service.create_personal_fact(
                db,
                new_user.id,
                PersonalFactCreate(fact_key="telegram_id", fact_value=str(telegram_id))
            )
            
            # Create user details with name and bio
            details_data = {}
            if full_name:
                details_data['full_name'] = full_name
            if bio:
                details_data['bio'] = bio
            
            if details_data:
                db_service.create_user_details(
                    db,
                    new_user.id,
                    UserDetailsCreate(**details_data)
                )
            
            # Add personal facts
            if age:
                db_service.create_personal_fact(
                    db,
                    new_user.id,
                    PersonalFactCreate(fact_key="возраст", fact_value=age)
                )
            
            if interests:
                db_service.create_personal_fact(
                    db,
                    new_user.id,
                    PersonalFactCreate(fact_key="интересы", fact_value=interests)
                )
            
            if language:
                db_service.create_personal_fact(
                    db,
                    new_user.id,
                    PersonalFactCreate(fact_key="предпочитаемый_язык", fact_value=language)
                )
            
            return new_user.id
            
        except Exception as e:
            print(f"Error registering new user: {e}")
            db.rollback()
            return None
        finally:
            db.close()
    
    async def get_or_create_user(self, telegram_id: int, username: str = None, full_name: str = None) -> Optional[str]:
        """Get existing user by telegram_id or create new one"""
        db = SessionLocal()
        try:
            # Try to find user by telegram_id in personal_facts
            user = db_service.get_user_by_telegram_id(db, telegram_id)
            
            if user:
                return user.id
            
            # Create new user
            user_data = {
                "username": username or f"tg_{telegram_id}",
                "password": f"telegram_{telegram_id}"  # Auto-generated password
            }
            
            new_user = db_service.create_user(db, user_data)
            
            if new_user:
                # Store telegram_id in personal facts
                from app.schemas import PersonalFactCreate
                db_service.create_personal_fact(
                    db,
                    new_user.id,
                    PersonalFactCreate(fact_key="telegram_id", fact_value=str(telegram_id))
                )
                
                # Store username and full_name if provided
                if full_name:
                    from app.schemas import UserDetailsCreate
                    db_service.create_user_details(
                        db,
                        new_user.id,
                        UserDetailsCreate(full_name=full_name)
                    )
                
                return new_user.id
            
            return None
            
        except Exception as e:
            print(f"Error getting/creating user: {e}")
            return None
        finally:
            db.close()
    
    async def start_chat_session(self, telegram_id: int) -> Optional[str]:
        """Start new chat session for telegram user"""
        db = SessionLocal()
        try:
            user_id = await self.get_or_create_user(telegram_id)
            if not user_id:
                return None
            
            # Create new session
            session = db_service.create_chat_session(db, user_id)
            if session:
                self.user_sessions[telegram_id] = session.session_id
                return session.session_id
            
            return None
            
        except Exception as e:
            print(f"Error starting chat session: {e}")
            return None
        finally:
            db.close()
    
    async def get_session_id(self, telegram_id: int) -> Optional[str]:
        """Get active session ID for telegram user"""
        return self.user_sessions.get(telegram_id)
    
    async def get_greeting(self, telegram_id: int) -> str:
        """Get personalized greeting for user"""
        db = SessionLocal()
        try:
            user_id = await self.get_or_create_user(telegram_id)
            if not user_id:
                return "Привет! Я твой AI-ассистент. Чем могу помочь?"
            
            # Get user data for personalization
            user_data = db_service.get_user_with_details(db, user_id)
            
            # Generate greeting using LLM
            greeting = ollama_service.create_greeting_message(user_data)
            
            return greeting
            
        except Exception as e:
            print(f"Error generating greeting: {e}")
            return "Привет! Я твой AI-ассистент. Чем могу помочь?"
        finally:
            db.close()
    
    async def process_message(self, telegram_id: int, message: str) -> str:
        """Process user message and get AI response"""
        db = SessionLocal()
        try:
            # Get or create user
            user_id = await self.get_or_create_user(telegram_id)
            if not user_id:
                return "Произошла ошибка при обработке сообщения. Попробуйте /start"
            
            # Get or create session
            session_id = self.user_sessions.get(telegram_id)
            if not session_id:
                session_id = await self.start_chat_session(telegram_id)
                if not session_id:
                    return "Произошла ошибка при создании сессии. Попробуйте /start"
            
            # Get chat history
            history = db_service.get_chat_history(db, session_id)
            
            # Get user context for personalization
            user_data = db_service.get_user_with_details(db, user_id)
            context = ollama_service.create_personalized_context(user_data)
            
            # Get AI response
            response = await ollama_service.chat(message, history, context)
            
            # Save messages to database
            db_service.save_chat_message(db, session_id, "user", message)
            db_service.save_chat_message(db, session_id, "assistant", response)
            
            return response
            
        except Exception as e:
            print(f"Error processing message: {e}")
            return f"Извините, произошла ошибка: {str(e)}"
        finally:
            db.close()
    
    async def end_session(self, telegram_id: int) -> bool:
        """End chat session for telegram user"""
        try:
            if telegram_id in self.user_sessions:
                del self.user_sessions[telegram_id]
            return True
        except Exception as e:
            print(f"Error ending session: {e}")
            return False
    
    async def get_user_info(self, telegram_id: int) -> Optional[Dict[str, Any]]:
        """Get user information"""
        db = SessionLocal()
        try:
            user_id = await self.get_or_create_user(telegram_id)
            if not user_id:
                return None
            
            user_data = db_service.get_user_with_details(db, user_id)
            return user_data
            
        except Exception as e:
            print(f"Error getting user info: {e}")
            return None
        finally:
            db.close()


# Singleton instance
telegram_service = TelegramService()
