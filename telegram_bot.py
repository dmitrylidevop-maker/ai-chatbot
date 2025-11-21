#!/usr/bin/env python3
"""
Telegram Bot Entry Point
Run this script to start the Telegram bot
"""
import asyncio
import sys
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode

# Add project root to path
sys.path.insert(0, '/home/dmitrylil/workspace/LTS-AAI/chat-bot')

from app.config import get_settings
from app.telegram.handlers import router
from app.database import init_db
from app.services.ollama_service import ollama_service

settings = get_settings()


async def main():
    """Main function to run the bot"""
    print("=" * 50)
    print("🤖 Starting Telegram Bot")
    print("=" * 50)
    
    # Initialize database
    print("\n📦 Initializing database...")
    init_db()
    print("✓ Database initialized!")
    
    # Check Ollama service
    print("\n🔍 Checking Ollama service...")
    if await ollama_service.health_check():
        print("✓ Ollama service is running!")
        if await ollama_service.initialize():
            print(f"✓ Ollama model {settings.OLLAMA_MODEL} is ready!")
        else:
            print(f"❌ Ollama model {settings.OLLAMA_MODEL} not found!")
            print(f"Please run: ollama pull {settings.OLLAMA_MODEL}")
            return
    else:
        print("❌ Ollama service is not running!")
        print("Please start Ollama service first.")
        return
    
    # Initialize bot and dispatcher
    print(f"\n🚀 Starting bot with token: {settings.TELEGRAM_BOT_TOKEN[:10]}...")
    bot = Bot(token=settings.TELEGRAM_BOT_TOKEN, parse_mode=ParseMode.HTML)
    
    dp = Dispatcher()
    dp.include_router(router)
    
    # Start polling
    print("\n✓ Bot is running! Press Ctrl+C to stop.")
    print("=" * 50)
    
    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    except KeyboardInterrupt:
        print("\n\n🛑 Stopping bot...")
    finally:
        await bot.session.close()
        print("✓ Bot stopped successfully!")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
