from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
import bcrypt
from sqlalchemy.orm import Session
from app.config import get_settings
from app.models.user import User
from app.schemas import TokenData
from app.services.base import BaseService

settings = get_settings()


class AuthService(BaseService):
    """Authentication and authorization service"""
    
    def __init__(self):
        self.secret_key = settings.JWT_SECRET_KEY
        self.algorithm = settings.JWT_ALGORITHM
        self.access_token_expire_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES
    
    async def initialize(self) -> bool:
        """Initialize auth service"""
        return True
    
    async def health_check(self) -> bool:
        """Check auth service health"""
        return True
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        password_bytes = plain_password.encode('utf-8')
        hashed_bytes = hashed_password.encode('utf-8')
        return bcrypt.checkpw(password_bytes, hashed_bytes)
    
    def get_password_hash(self, password: str) -> str:
        """Hash a password"""
        password_bytes = password.encode('utf-8')
        hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
        return hashed.decode('utf-8')
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def verify_token(self, token: str) -> Optional[TokenData]:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            user_id: str = payload.get("sub")
            username: str = payload.get("username")
            if user_id is None:
                return None
            return TokenData(user_id=user_id, username=username)
        except JWTError:
            return None
    
    def authenticate_user(self, db: Session, username: str, password: str) -> Optional[User]:
        """Authenticate a user"""
        user = db.query(User).filter(User.username == username).first()
        if not user:
            return None
        if not self.verify_password(password, user.password_hash):
            return None
        return user
    
    def create_user(self, db: Session, username: str, password: str) -> User:
        """Create a new user"""
        hashed_password = self.get_password_hash(password)
        user = User(username=username, password_hash=hashed_password)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user


# Singleton instance
auth_service = AuthService()
