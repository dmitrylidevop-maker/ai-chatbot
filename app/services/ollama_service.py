from typing import List, Dict, Any, Optional
import ollama
from app.config import get_settings
from app.services.base import BaseService
from app.database import SessionLocal

settings = get_settings()


class OllamaService(BaseService):
    """Service for interacting with Ollama LLM"""
    
    def __init__(self):
        self.model = settings.OLLAMA_MODEL
        self.base_url = settings.OLLAMA_BASE_URL
        self.client = None
        self._ai_rules_cache = None
    
    def _get_ai_behavior_rules(self) -> List[str]:
        """Get AI behavior rules from database (with caching)"""
        if self._ai_rules_cache is None:
            db = SessionLocal()
            try:
                from app.services.database_service import db_service
                self._ai_rules_cache = db_service.get_ai_behavior_rules(db)
            except Exception as e:
                print(f"Error loading AI rules: {e}")
                self._ai_rules_cache = []
            finally:
                db.close()
        
        return self._ai_rules_cache
    
    def reload_ai_rules(self):
        """Force reload AI behavior rules from database"""
        self._ai_rules_cache = None
        return self._get_ai_behavior_rules()
    
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
        """Create initial greeting message using LLM"""
        user_name = "друг"
        user_info = ""
        language = settings.DEFAULT_LANGUAGE

        print(f"language detected: {language}")
        
        if user_data.get('user_details'):
            details = user_data['user_details']
            if details.get('full_name'):
                user_name = details['full_name'].split()[0]  # First name only
                user_info += f"Имя: {details['full_name']}\n"
            if details.get('bio'):
                user_info += f"О пользователе: {details['bio']}\n"
        
        if user_data.get('personal_facts'):
            facts = user_data['personal_facts']
            if facts:
                # Check for language preference in facts
                for fact in facts:
                    if fact['fact_key'].lower() in ['язык', 'language', 'preferred_language']:
                        language = fact['fact_value']
                        break
                
                user_info += "Интересы: "
                user_info += ", ".join([f"{fact['fact_key']}: {fact['fact_value']}" for fact in facts[:3]])
                user_info += "\n"
        
        # Generate unique greeting using LLM
        try:
            prompt = f"""Создай короткое дружелюбное приветствие для пользователя.
Имя пользователя: {user_name}
Язык общения: {language}
{"Информация о пользователе:\n" + user_info if user_info else ""}

Требования:
- Приветствие должно быть уникальным и персональным
- Максимум 2-3 предложения
- Используй эмодзи для дружелюбности
- Спроси как дела или предложи помощь
- Пиши ОБЯЗАТЕЛЬНО на языке: {language}

Только текст приветствия без пояснений:"""
            
            response = ollama.chat(
                model=self.model,
                messages=[
                    {"role": "system", "content": f"Ты создаешь дружелюбные персональные приветствия на языке: {language}."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            greeting = response['message']['content'].strip()
            return greeting
            
        except Exception as e:
            print(f"Error generating greeting: {e}")
            # Fallback to simple greeting
            return f"Привет, {user_name}! 👋 Как твои дела? Чем могу помочь сегодня?"
    
    async def chat(
        self,
        message: str,
        chat_history: List[Dict[str, str]],
        user_context: Optional[str] = None
    ) -> str:
        """Send a message to Ollama and get response"""
        try:
            # Detect message language
            message_language = self._detect_language(message)
            
            # Get AI behavior rules
            ai_rules = self._get_ai_behavior_rules()
            
            messages = []
            
            # Build system message
            system_parts = []
            
            # Add AI behavior rules
            if ai_rules:
                system_parts.append("ПРАВИЛА ПОВЕДЕНИЯ:")
                for i, rule in enumerate(ai_rules, 1):
                    system_parts.append(f"{i}. {rule}")
                system_parts.append("")  # Empty line
            
            # Add user context if available
            if user_context:
                system_parts.append("ИНФОРМАЦИЯ О ПОЛЬЗОВАТЕЛЕ:")
                system_parts.append(user_context)
                system_parts.append("")  # Empty line
            
            # Add language instruction
            system_parts.append(f"ВАЖНО: Пользователь пишет на языке: {message_language}. Отвечай ОБЯЗАТЕЛЬНО на том же языке, на котором задан вопрос.")
            
            if user_context:
                system_parts.append("\nИспользуй информацию о пользователе для персонализации разговора. Будь естественным и дружелюбным.")
            else:
                system_parts.append("\nОбщайся естественно и помогай пользователю.")
            
            system_message = "\n".join(system_parts)
            messages.append({"role": "system", "content": system_message})
            
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
    
    def _detect_language(self, text: str) -> str:
        """Detect language of the text (simple heuristic)"""
        # Check for Hebrew characters
        if any('\u0590' <= char <= '\u05FF' for char in text):
            return "иврит"
        # Check for Cyrillic characters (Russian, Ukrainian, etc.)
        elif any('\u0400' <= char <= '\u04FF' for char in text):
            return "русский"
        # Check for common English words
        elif any(word in text.lower() for word in ['the', 'is', 'are', 'what', 'how', 'hello', 'hi']):
            return "английский"
        # Check for common Spanish words
        elif any(word in text.lower() for word in ['el', 'la', 'es', 'hola', 'que', 'como']):
            return "испанский"
        # Check for common German words
        elif any(word in text.lower() for word in ['der', 'die', 'das', 'ist', 'sind', 'hallo']):
            return "немецкий"
        # Check for common French words
        elif any(word in text.lower() for word in ['le', 'la', 'est', 'sont', 'bonjour', 'salut']):
            return "французский"
        else:
            # Default to configured language
            return settings.DEFAULT_LANGUAGE


# Singleton instance
ollama_service = OllamaService()
