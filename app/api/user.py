from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.api.dependencies import get_current_user
from app.models.user import User
from app.schemas import (
    UserDetailsCreate, UserDetailsUpdate, UserDetailsResponse,
    PersonalFactCreate, PersonalFactUpdate, PersonalFactResponse
)
from app.services.database_service import db_service

router = APIRouter(prefix="/user", tags=["User Profile"])


# User Details endpoints
@router.get("/details", response_model=UserDetailsResponse)
async def get_user_details(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user details"""
    details = db_service.get_user_details(db, current_user.id)
    if not details:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User details not found"
        )
    return details


@router.post("/details", response_model=UserDetailsResponse, status_code=status.HTTP_201_CREATED)
async def create_user_details(
    details: UserDetailsCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create user details"""
    existing_details = db_service.get_user_details(db, current_user.id)
    if existing_details:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User details already exist"
        )
    
    return db_service.create_user_details(db, current_user.id, details)


@router.put("/details", response_model=UserDetailsResponse)
async def update_user_details(
    details: UserDetailsUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user details"""
    updated_details = db_service.update_user_details(db, current_user.id, details)
    if not updated_details:
        # Create if doesn't exist
        return db_service.create_user_details(
            db, current_user.id, UserDetailsCreate(**details.model_dump())
        )
    return updated_details


# Personal Facts endpoints
@router.get("/facts", response_model=List[PersonalFactResponse])
async def get_personal_facts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all personal facts for current user"""
    return db_service.get_personal_facts(db, current_user.id)


@router.post("/facts", response_model=PersonalFactResponse, status_code=status.HTTP_201_CREATED)
async def create_personal_fact(
    fact: PersonalFactCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a personal fact"""
    existing_fact = db_service.get_personal_fact(db, current_user.id, fact.fact_key)
    if existing_fact:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Fact with key '{fact.fact_key}' already exists"
        )
    
    return db_service.create_personal_fact(db, current_user.id, fact)


@router.put("/facts/{fact_key}", response_model=PersonalFactResponse)
async def update_personal_fact(
    fact_key: str,
    fact: PersonalFactUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a personal fact"""
    updated_fact = db_service.update_personal_fact(db, current_user.id, fact_key, fact)
    if not updated_fact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Fact with key '{fact_key}' not found"
        )
    return updated_fact


@router.delete("/facts/{fact_key}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_personal_fact(
    fact_key: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a personal fact"""
    success = db_service.delete_personal_fact(db, current_user.id, fact_key)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Fact with key '{fact_key}' not found"
        )
