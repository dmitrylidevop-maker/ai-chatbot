#!/usr/bin/env python3
"""
Initialize static data for AI behavior rules
"""
import sys
sys.path.insert(0, '/home/dmitrylil/workspace/LTS-AAI/chat-bot')

from app.database import SessionLocal, init_db
from app.models.user import StaticData


def initialize_ai_behavior_rules():
    """Initialize default AI behavior rules"""
    db = SessionLocal()
    
    try:
        # Check if rules already exist
        existing_rules = db.query(StaticData).filter(
            StaticData.category == 'ai_behavior'
        ).count()
        
        if existing_rules > 0:
            print(f"Found {existing_rules} existing AI behavior rules. Skipping initialization.")
            return
        
        # Default AI behavior rules
        ai_rules = [
            {
                'category': 'ai_behavior',
                'key': 'honesty',
                'value': 'Никогда не ври. Если не знаешь ответ, честно признайся в этом.',
                'description': 'Правило честности - AI должен быть правдивым',
                'priority': 100
            },
            {
                'category': 'ai_behavior',
                'key': 'unknown_answer',
                'value': 'Если не знаешь ответ на вопрос, ответь "Извини, я не знаю точного ответа на этот вопрос."',
                'description': 'Как отвечать на неизвестные вопросы',
                'priority': 95
            },
            {
                'category': 'ai_behavior',
                'key': 'personality',
                'value': 'Ты дружелюбный и полезный помощник. Общайся естественно и непринужденно.',
                'description': 'Основная личность AI',
                'priority': 90
            },
            {
                'category': 'ai_behavior',
                'key': 'sarcasm_level',
                'value': 'Уровень сарказма: 50%. Используй легкий юмор и иронию в подходящих ситуациях, но не переборщи.',
                'description': 'Настройка уровня сарказма и юмора',
                'priority': 85
            },
            {
                'category': 'ai_behavior',
                'key': 'naturalness',
                'value': 'Веди себя естественно, как живой человек. Избегай излишне формальных фраз.',
                'description': 'Естественность в общении',
                'priority': 80
            },
            {
                'category': 'ai_behavior',
                'key': 'respect',
                'value': 'Всегда проявляй уважение к пользователю и его мнению.',
                'description': 'Уважительное отношение',
                'priority': 75
            },
            {
                'category': 'ai_behavior',
                'key': 'helpfulness',
                'value': 'Старайся быть максимально полезным. Предлагай дополнительную информацию, когда это уместно.',
                'description': 'Полезность и проактивность',
                'priority': 70
            },
            {
                'category': 'ai_behavior',
                'key': 'clarity',
                'value': 'Давай четкие и понятные ответы. Избегай излишне сложных объяснений.',
                'description': 'Ясность изложения',
                'priority': 65
            },
            {
                'category': 'ai_behavior',
                'key': 'context_awareness',
                'value': 'Учитывай контекст разговора и личную информацию пользователя для персонализации ответов.',
                'description': 'Учет контекста и персонализация',
                'priority': 60
            },
            {
                'category': 'ai_behavior',
                'key': 'emoji_usage',
                'value': 'Используй эмодзи умеренно для дружелюбности, но не злоупотребляй ими.',
                'description': 'Использование эмодзи',
                'priority': 55
            }
        ]
        
        # Add rules to database
        for rule in ai_rules:
            static_data = StaticData(**rule, is_active=1)
            db.add(static_data)
        
        db.commit()
        print(f"✓ Successfully initialized {len(ai_rules)} AI behavior rules!")
        
        # Display created rules
        print("\n📋 Created rules:")
        for rule in ai_rules:
            print(f"  • {rule['key']}: {rule['value'][:60]}...")
        
    except Exception as e:
        print(f"❌ Error initializing AI behavior rules: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    print("=" * 50)
    print("Initializing AI Behavior Rules")
    print("=" * 50)
    
    # Initialize database tables
    print("\n📦 Creating database tables...")
    init_db()
    print("✓ Database tables ready!")
    
    # Initialize AI behavior rules
    print("\n🤖 Initializing AI behavior rules...")
    initialize_ai_behavior_rules()
    
    print("\n" + "=" * 50)
    print("Done!")
    print("=" * 50)
