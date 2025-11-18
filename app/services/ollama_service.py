from typing import List, Dict, Any, Optional
import ollama
from app.config import get_settings
from app.services.base import BaseService

settings = get_settings()


class OllamaService(BaseService):
    """Service for interacting with Ollama LLM"""
    
    def __init__(self):
        self.model = settings.OLLAMA_MODEL
        self.base_url = settings.OLLAMA_BASE_URL
        self.client = None
    
    async def initialize(self) -> bool:
        """Initialize Ollama service"""
        try:
            # Check if model exists
            models = ollama.list()
            model_exists = any(m['name'] == self.model for m in models.get('models', []))
            
            if not model_exists:
                print(f"Model {self.model} not found. It needs to be pulled first.")
                return False
            
            return True
        except Exception as e:
            print(f"Error initializing Ollama: {e}")
            return False
    
    async def health_check(self) -> bool:
        """Check if Ollama is running"""
        try:
            ollama.list()
            return True
        except Exception:
            return False
    
    def create_personalized_context(self, user_data: Dict[str, Any]) -> str:
        """Create personalized context from user data"""
        context_parts = []
        
        # Add user details
        if user_data.get('user_details'):
            details = user_data['user_details']
            if details.get('full_name'):
                context_parts.append(f"Имя пользователя: {details['full_name']}")
            if details.get('bio'):
                context_parts.append(f"О пользователе: {details['bio']}")
        
        # Add personal facts
        if user_data.get('personal_facts'):
            facts = user_data['personal_facts']
            if facts:
                context_parts.append("\nЛичная информация о пользователе:")
                for fact in facts:
                    context_parts.append(f"- {fact['fact_key']}: {fact['fact_value']}")
        
        if context_parts:
            return "\n".join(context_parts)
        return ""
    
    def create_greeting_message(self, user_data: Dict[str, Any]) -> str:
        """Create initial greeting message"""
        user_name = "друг"
        
        if user_data.get('user_details'):
            details = user_data['user_details']
            if details.get('full_name'):
                user_name = details['full_name'].split()[0]  # First name only
        
        greeting = f"Привет, {user_name}! 👋 Как твои дела? Чем могу помочь сегодня?"
        return greeting
    
    async def chat(
        self,
        message: str,
        chat_history: List[Dict[str, str]],
        user_context: Optional[str] = None
    ) -> str:
        """Send a message to Ollama and get response"""
        try:
            messages = []
            
            # Add system message with user context if available
            if user_context:
                system_message = f"""Ты дружелюбный помощник. Вот информация о пользователе, с которым ты общаешься:

{user_context}

Используй эту информацию для персонализации разговора. Будь естественным и дружелюбным."""
                messages.append({"role": "system", "content": system_message})
            else:
                messages.append({
                    "role": "system",
                    "content": "Ты дружелюбный и полезный AI-ассистент. Общайся естественно и помогай пользователю."
                })
            
            # Add chat history
            for msg in chat_history:
                messages.append({"role": msg["role"], "content": msg["message"]})
            
            # Add current message
            messages.append({"role": "user", "content": message})
            
            # Get response from Ollama
            response = ollama.chat(
                model=self.model,
                messages=messages
            )
            
            return response['message']['content']
        
        except Exception as e:
            print(f"Error in Ollama chat: {e}")
            return f"Извините, произошла ошибка при обработке вашего сообщения: {str(e)}"


# Singleton instance
ollama_service = OllamaService()
