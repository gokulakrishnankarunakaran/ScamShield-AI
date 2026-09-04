"""QR Shield API contract schemas for Phase 2 Verification Engine."""

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


class QRCheckRequest(BaseModel):
    """Request payload for QR code verification."""
    qr_data: str = Field(..., description="Raw QR code decoded string, e.g. upi://pay?pa=...")
    expected_name: Optional[str] = Field(default=None, description="Expected recipient/merchant name entered by user")

    def __init__(self, **data: Any) -> None:
        # Support raw_payload as an alias for qr_data for compatibility
        if "raw_payload" in data and "qr_data" not in data:
            data["qr_data"] = data["raw_payload"]
        super().__init__(**data)


class PayeeDetails(BaseModel):
    """Decoded Payee and payment parameters from UPI QR."""
    name: Optional[str] = None
    vpa: Optional[str] = None
    amount: Optional[float] = None
    merchant_code: Optional[str] = None
    transaction_ref: Optional[str] = None
    transaction_note: Optional[str] = None
    currency: str = "INR"


class NameMatchCheck(BaseModel):
    """Layer 1: Expected name vs QR payee name string comparison."""
    status: str = "not_provided"  # exact | strong_match | possible_match | mismatch | not_provided
    score: int = 0
    normalized_expected: Optional[str] = None
    normalized_payee: Optional[str] = None


class VPAReputationCheck(BaseModel):
    """Layer 2: Authoritative VPA registry reputation lookup."""
    status: str = "unknown"  # verified | reported_scam | unknown
    risk_level: Optional[str] = None
    reported_count: int = 0
    trusted_since: Optional[str] = None
    category: Optional[str] = None


class VPAPatternCheck(BaseModel):
    """Layer 3: Heuristic analysis of VPA structure (weak signal only)."""
    status: str = "neutral"  # positive | neutral | caution
    pattern_type: str = "standard"  # personal_handle | phone_handle | business_handle | merchant_handle | standard
    details: Optional[str] = None


class SemanticMatchCheck(BaseModel):
    """Semantic vector search match (used when string match is ambiguous)."""
    status: str = "skipped"  # match | possible_match | not_match | skipped
    score: int = 0
    matched_merchant: Optional[str] = None
    matched_vpa: Optional[str] = None


class QRVerificationChecks(BaseModel):
    """Container for all independent verification layer outputs."""
    name_match: NameMatchCheck = Field(default_factory=NameMatchCheck)
    vpa_reputation: VPAReputationCheck = Field(default_factory=VPAReputationCheck)
    vpa_pattern: VPAPatternCheck = Field(default_factory=VPAPatternCheck)
    semantic_match: SemanticMatchCheck = Field(default_factory=SemanticMatchCheck)


class QRCheckResponse(BaseModel):
    """Comprehensive response returned from QR Shield Verification Engine."""
    verdict: str  # GREEN | YELLOW | RED | INVALID_QR
    risk_score: int  # 0 to 100
    confidence: str  # high | medium | low
    payee: PayeeDetails
    expected_recipient: Optional[str] = None
    checks: QRVerificationChecks
    reasons: List[str] = Field(default_factory=list)
    recommendation: str
    explanation: Optional[str] = None
    raw_payload: Optional[str] = None
    is_valid_upi: bool = True
    error_message: Optional[str] = None
