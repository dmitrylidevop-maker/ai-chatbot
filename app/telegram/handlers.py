from aiogram import Router, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from app.services.telegram_service import telegram_service
from app.telegram.states import RegistrationStates

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    """Handle /start command"""
    telegram_id = message.from_user.id
    username = message.from_user.username
    full_name = message.from_user.full_name
    
    # Check if user already exists
    is_new_user = await telegram_service.is_new_user(telegram_id)
    
    if is_new_user:
        # Start registration process for new user
        await state.update_data(telegram_id=telegram_id, username=username, full_name=full_name)
        
        welcome_text = f"""
👋 Привет{', ' + full_name if full_name else ''}! Добро пожаловать!

Я твой персональный AI-ассистент. Чтобы лучше тебя узнать и персонализировать общение, ответь, пожалуйста, на несколько вопросов.

📝 Вопрос 1/5

Как тебя зовут? (Или напиши "пропустить" чтобы использовать {full_name or "имя из профиля"})
"""
        await message.answer(welcome_text)
        await state.set_state(RegistrationStates.waiting_for_name)
    else:
        # Existing user - just greet
        await telegram_service.start_chat_session(telegram_id)
        greeting = await telegram_service.get_greeting(telegram_id)
        await message.answer(greeting)


@router.message(Command("newsession"))
async def cmd_new_session(message: Message):
    """Start a new chat session"""
    telegram_id = message.from_user.id
    
    # End current session and start new one
    await telegram_service.end_session(telegram_id)
    session_id = await telegram_service.start_chat_session(telegram_id)
    
    if session_id:
        await message.answer("🔄 Начата новая сессия! Предыдущая история сохранена.")
    else:
        await message.answer("❌ Ошибка при создании новой сессии. Попробуйте /start")


@router.message(Command("profile"))
async def cmd_profile(message: Message):
    """Show user profile"""
    telegram_id = message.from_user.id
    
    user_info = await telegram_service.get_user_info(telegram_id)
    
    if not user_info:
        await message.answer("❌ Не удалось получить информацию о профиле. Попробуйте /start")
        return
    
    profile_text = "👤 Ваш профиль:\n\n"
    
    if user_info.get('user_details'):
        details = user_info['user_details']
        if details.get('full_name'):
            profile_text += f"Имя: {details['full_name']}\n"
        if details.get('bio'):
            profile_text += f"О себе: {details['bio']}\n"
    
    if user_info.get('personal_facts'):
        facts = user_info['personal_facts']
        if facts:
            profile_text += "\n📝 Личная информация:\n"
            for fact in facts:
                if fact['fact_key'] != 'telegram_id':  # Skip internal field
                    profile_text += f"• {fact['fact_key']}: {fact['fact_value']}\n"
    
    if user_info.get('preferred_language'):
        profile_text += f"\n🌐 Язык: {user_info['preferred_language']}"
    
    await message.answer(profile_text)


@router.message(Command("help"))
async def cmd_help(message: Message):
    """Show help message"""
    help_text = """
🤖 Доступные команды:

/start - Начать общение с ботом
/newsession - Начать новую сессию чата
/profile - Посмотреть ваш профиль
/help - Показать эту справку

💬 Просто отправьте мне сообщение, и я отвечу!

Я персонализирую разговор на основе вашей информации и автоматически определяю язык вашего сообщения.
"""
    await message.answer(help_text)


# Registration handlers
@router.message(RegistrationStates.waiting_for_name)
async def process_name(message: Message, state: FSMContext):
    """Process user's name"""
    user_name = message.text.strip()
    
    data = await state.get_data()
    
    if user_name.lower() != "пропустить":
        await state.update_data(user_name=user_name)
    else:
        # Use Telegram full_name
        await state.update_data(user_name=data.get('full_name', ''))
    
    # Ask for age
    await message.answer(
        "📝 Вопрос 2/5\n\n"
        "Сколько тебе лет? (Или напиши \"пропустить\")"
    )
    await state.set_state(RegistrationStates.waiting_for_age)


@router.message(RegistrationStates.waiting_for_age)
async def process_age(message: Message, state: FSMContext):
    """Process user's age"""
    age = message.text.strip()
    
    if age.lower() != "пропустить":
        await state.update_data(age=age)
    
    # Ask for interests
    await message.answer(
        "📝 Вопрос 3/5\n\n"
        "Какие у тебя интересы или хобби? (Например: программирование, путешествия, музыка)\n"
        "Или напиши \"пропустить\""
    )
    await state.set_state(RegistrationStates.waiting_for_interests)


@router.message(RegistrationStates.waiting_for_interests)
async def process_interests(message: Message, state: FSMContext):
    """Process user's interests"""
    interests = message.text.strip()
    
    if interests.lower() != "пропустить":
        await state.update_data(interests=interests)
    
    # Ask for preferred language with keyboard
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🇷🇺 Русский"), KeyboardButton(text="🇺🇸 English")],
            [KeyboardButton(text="🇮🇱 עברית"), KeyboardButton(text="🇪🇸 Español")],
            [KeyboardButton(text="🇩🇪 Deutsch"), KeyboardButton(text="🇫🇷 Français")],
            [KeyboardButton(text="⏭️ Пропустить")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    
    await message.answer(
        "📝 Вопрос 4/5\n\n"
        "На каком языке ты предпочитаешь общаться?",
        reply_markup=keyboard
    )
    await state.set_state(RegistrationStates.waiting_for_language)


@router.message(RegistrationStates.waiting_for_language)
async def process_language(message: Message, state: FSMContext):
    """Process user's preferred language"""
    language_text = message.text.strip()
    
    # Map emoji + language to language name
    language_map = {
        "🇷🇺 Русский": "русский",
        "🇺🇸 English": "английский",
        "🇮🇱 עברית": "иврит",
        "🇪🇸 Español": "испанский",
        "🇩🇪 Deutsch": "немецкий",
        "🇫🇷 Français": "французский"
    }
    
    if language_text in language_map:
        await state.update_data(language=language_map[language_text])
    elif language_text.lower() != "⏭️ пропустить" and language_text.lower() != "пропустить":
        await state.update_data(language=language_text)
    
    # Ask for bio
    await message.answer(
        "📝 Вопрос 5/5\n\n"
        "Расскажи немного о себе (несколько предложений):\n"
        "Или напиши \"пропустить\"",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(RegistrationStates.waiting_for_bio)


@router.message(RegistrationStates.waiting_for_bio)
async def process_bio(message: Message, state: FSMContext):
    """Process user's bio and complete registration"""
    bio = message.text.strip()
    
    if bio.lower() != "пропустить":
        await state.update_data(bio=bio)
    
    # Get all collected data
    data = await state.get_data()
    
    # Show processing message
    await message.answer("⏳ Создаю твой профиль...")
    
    # Register user with all information
    user_id = await telegram_service.register_new_user(
        telegram_id=data['telegram_id'],
        username=data['username'],
        full_name=data.get('user_name', data.get('full_name', '')),
        age=data.get('age'),
        interests=data.get('interests'),
        language=data.get('language'),
        bio=data.get('bio')
    )
    
    if user_id:
        # Start chat session
        await telegram_service.start_chat_session(data['telegram_id'])
        
        # Get personalized greeting
        greeting = await telegram_service.get_greeting(data['telegram_id'])
        
        await message.answer(
            "✅ Регистрация завершена!\n\n"
            f"{greeting}\n\n"
            "Теперь можешь задать мне любой вопрос! 💬"
        )
    else:
        await message.answer(
            "❌ Произошла ошибка при создании профиля. Попробуй /start снова."
        )
    
    # Clear state
    await state.clear()


@router.message(F.text)
async def handle_message(message: Message, state: FSMContext):
    """Handle regular text messages"""
    # Check if user is in registration process
    current_state = await state.get_state()
    if current_state is not None:
        # User is in registration, don't handle message here
        return
    
    telegram_id = message.from_user.id
    user_message = message.text
    
    # Check if user has active session
    session_id = await telegram_service.get_session_id(telegram_id)
    if not session_id:
        # Check if user exists
        is_new = await telegram_service.is_new_user(telegram_id)
        if is_new:
            await message.answer(
                "Привет! Похоже, ты здесь впервые. "
                "Отправь /start чтобы зарегистрироваться и начать общение! 👋"
            )
            return
        
        # Auto-start session for existing user
        await telegram_service.get_or_create_user(
            telegram_id,
            message.from_user.username,
            message.from_user.full_name
        )
        await telegram_service.start_chat_session(telegram_id)
    
    # Show typing indicator
    await message.bot.send_chat_action(chat_id=message.chat.id, action="typing")
    
    # Process message and get response
    response = await telegram_service.process_message(telegram_id, user_message)
    
    # Send response
    await message.answer(response)


@router.message()
async def handle_other(message: Message):
    """Handle other message types"""
    await message.answer(
        "Извините, я понимаю только текстовые сообщения. "
        "Отправьте /help для получения справки."
    )
