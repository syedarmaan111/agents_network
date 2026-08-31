from .auth import router as auth_router
from .chat import router as chat_router
from .database import router as database_router
from .health import router as health_router

__all__ = [
    "auth_router",
    "chat_router",
    "database_router",
    "health_router",
]
