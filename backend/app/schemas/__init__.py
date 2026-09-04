"""Pydantic schemas package for ScamShield AI API contracts."""

from .health import HealthResponse, ComponentStatus
from .merchant import (
    MerchantSchema,
    MerchantStatusEnum,
    VectorSearchQuery,
    VectorSearchResult,
)
from .qr import QRCheckRequest, QRCheckResponse
from .screenshot import ScreenshotCheckRequest, ScreenshotCheckResponse

__all__ = [
    "HealthResponse",
    "ComponentStatus",
    "MerchantSchema",
    "MerchantStatusEnum",
    "VectorSearchQuery",
    "VectorSearchResult",
    "QRCheckRequest",
    "QRCheckResponse",
    "ScreenshotCheckRequest",
    "ScreenshotCheckResponse",
]

