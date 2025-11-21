from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.database import init_db
from app.api import auth, chat, user, static_data
from app.services.ollama_service import ollama_service

settings = get_settings()

app = FastAPI(
    title="AI Chat Bot API",
    description="AI Chat Bot with Ollama and personalization",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(chat.router)
app.include_router(user.router)
app.include_router(static_data.router)


@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    print("Initializing database...")
    try:
        init_db()
        print("Database initialized!")
    except Exception as e:
        print(f"ERROR: Failed to initialize database: {e}")
        print("Please make sure PostgreSQL is running and configured correctly in .env-tmp")
        print("You can start PostgreSQL with: sudo systemctl start postgresql")
        raise
    
    print("Checking Ollama service...")
    ollama_healthy = await ollama_service.health_check()
    if not ollama_healthy:
        print("WARNING: Ollama service is not available!")
    else:
        print("Ollama service is running!")
        ollama_initialized = await ollama_service.initialize()
        if ollama_initialized:
            print(f"Ollama model {settings.OLLAMA_MODEL} is ready!")
        else:
            print(f"WARNING: Model {settings.OLLAMA_MODEL} not found. Please pull it first.")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "AI Chat Bot API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    ollama_status = await ollama_service.health_check()
    
    return {
        "status": "healthy",
        "database": "connected",
        "ollama": "connected" if ollama_status else "disconnected"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG
    )
