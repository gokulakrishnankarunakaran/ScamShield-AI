from enum import Enum
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


class MerchantStatusEnum(str, Enum):
    """Reputation status of a payment identity."""
    VERIFIED = "verified"
    REPORTED_SCAM = "reported_scam"
    UNKNOWN = "unknown"


class RiskLevelEnum(str, Enum):
    """Calculated risk tier for payment identity."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class MerchantSchema(BaseModel):
    """Schema representing a merchant entity in the system."""
    id: str
    merchant_name: str
    normalized_name: str
    vpa: str
    status: MerchantStatusEnum
    category: Optional[str] = None
    risk_level: Optional[RiskLevelEnum] = None
    reported_count: int = 0
    trusted_since: Optional[str] = None
    notes: Optional[str] = None
    embedding_metadata: Optional[Dict[str, Any]] = None


class ReputationLookupResponse(BaseModel):
    """Schema for deterministic reputation lookup."""
    vpa: str
    status: MerchantStatusEnum
    risk_level: RiskLevelEnum
    is_known: bool
    merchant: Optional[MerchantSchema] = None
    evidence_source: str = "ScamShield Deterministic Registry"
    message: str


class VectorSearchQuery(BaseModel):
    """Request payload for semantic merchant search."""
    query_name: str = Field(..., min_length=2, description="Merchant display name to search")
    top_k: int = Field(default=3, ge=1, le=10, description="Max candidate matches")
    min_similarity: float = Field(default=0.4, ge=0.0, le=1.0, description="Minimum similarity threshold")


class VectorSearchResult(BaseModel):
    """Individual candidate match returned from vector search."""
    merchant_id: str
    merchant_name: str
    normalized_name: str
    vpa: str
    status: MerchantStatusEnum
    similarity_score: float
    confidence_tier: str
    match_type: str
