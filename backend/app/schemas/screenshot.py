from typing import Any, Dict, List, Optional
try:
    from pydantic import BaseModel, Field
except ImportError:
    class BaseModel:  # type: ignore
        def __init__(self, **kwargs: Any) -> None:
            for k, v in kwargs.items():
                setattr(self, k, v)
        def model_dump(self) -> Dict[str, Any]:
            return self.__dict__
    def Field(*args: Any, **kwargs: Any) -> Any:  # type: ignore
        return kwargs.get("default", None)
from .merchant import MerchantStatusEnum, RiskLevelEnum, MerchantSchema


class ScreenshotCheckRequest(BaseModel):
    """Request payload for screenshot verification."""
    image_base64: Optional[str] = Field(default=None, description="Base64-encoded screenshot image")
    ocr_extracted_text: Optional[str] = Field(default=None, description="Pre-extracted OCR text if processed client-side")
    source_app: Optional[str] = Field(default="unknown", description="Source app hint: whatsapp | sms | gpay | paytm | phonepe")


class ExtractedEntities(BaseModel):
    """Extracted payment and entity fields from screenshot OCR/vision."""
    detected_vpa: Optional[str] = None
    detected_name: Optional[str] = None
    detected_amount: Optional[str] = None
    urgency_phrases_found: List[str] = Field(default_factory=list)
    threat_signals: List[str] = Field(default_factory=list)


class ScreenshotCheckResponse(BaseModel):
    """Response returned from Screenshot Verifier."""
    status: str = "pending_implementation_phase_2"
    is_suspicious: Optional[bool] = None
    risk_level: Optional[RiskLevelEnum] = None
    reputation_status: Optional[MerchantStatusEnum] = None
    extracted_entities: Optional[ExtractedEntities] = None
    identified_merchant: Optional[MerchantSchema] = None
    semantic_match: Optional[Dict[str, Any]] = None
    fraud_indicators: List[str] = Field(default_factory=list)
    explanation: Optional[str] = None
