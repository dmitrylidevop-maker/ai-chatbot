from abc import ABC, abstractmethod
from typing import Optional, Dict, Any


class BaseService(ABC):
    """Base class for all services to ensure extensibility"""
    
    @abstractmethod
    async def initialize(self) -> bool:
        """Initialize the service"""
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """Check if service is healthy"""
        pass
