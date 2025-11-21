from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.services.database_service import db_service
from app.services.ollama_service import ollama_service
from app.models.user import StaticData
from pydantic import BaseModel

router = APIRouter(prefix="/static-data", tags=["static-data"])


class StaticDataCreate(BaseModel):
    category: str
    key: str
    value: str
    description: str = None
    priority: int = 0


class StaticDataUpdate(BaseModel):
    value: str = None
    is_active: int = None
    priority: int = None


class StaticDataResponse(BaseModel):
    id: int
    category: str
    key: str
    value: str
    description: str = None
    is_active: int
    priority: int
    
    class Config:
        from_attributes = True


@router.get("/ai-behavior", response_model=List[str])
async def get_ai_behavior_rules(db: Session = Depends(get_db)):
    """Get all active AI behavior rules"""
    return db_service.get_ai_behavior_rules(db)


@router.get("/{category}", response_model=List[StaticDataResponse])
async def get_static_data_by_category(category: str, db: Session = Depends(get_db)):
    """Get all static data by category"""
    return db_service.get_static_data(db, category)


@router.post("/", response_model=StaticDataResponse)
async def create_static_data(data: StaticDataCreate, db: Session = Depends(get_db)):
    """Create new static data rule"""
    rule = db_service.add_static_data(
        db,
        category=data.category,
        key=data.key,
        value=data.value,
        description=data.description,
        priority=data.priority
    )
    
    # Reload AI rules cache if it's an AI behavior rule
    if data.category == 'ai_behavior':
        ollama_service.reload_ai_rules()
    
    return rule


@router.patch("/{rule_id}", response_model=StaticDataResponse)
async def update_static_data(
    rule_id: int,
    data: StaticDataUpdate,
    db: Session = Depends(get_db)
):
    """Update existing static data rule"""
    rule = db_service.update_static_data(
        db,
        rule_id=rule_id,
        value=data.value,
        is_active=data.is_active,
        priority=data.priority
    )
    
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    
    # Reload AI rules cache if it's an AI behavior rule
    if rule.category == 'ai_behavior':
        ollama_service.reload_ai_rules()
    
    return rule


@router.post("/reload-ai-rules")
async def reload_ai_rules():
    """Force reload AI behavior rules from database"""
    rules = ollama_service.reload_ai_rules()
    return {
        "message": "AI rules reloaded successfully",
        "rules_count": len(rules)
    }
