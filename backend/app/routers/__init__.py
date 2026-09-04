"""Routers package for ScamShield AI API endpoints."""

from .health import router as health_router
from .qr import router as qr_router
from .screenshot import router as screenshot_router
from .demo import router as demo_router

__all__ = [
    "health_router",
    "qr_router",
    "screenshot_router",
    "demo_router",
]

