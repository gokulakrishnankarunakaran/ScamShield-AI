"""QR Shield Verification API Router.

Team CYBERTRON.
Product Principle: "VERIFY BEFORE YOU TRUST."
Provides deterministic UPI QR code validation, multi-layer identity verification,
and contextual scam risk explanation.
"""

import logging
from typing import Any, Dict, Optional

try:
    from fastapi import APIRouter, HTTPException, status
except ImportError:
    class APIRouter:  # type: ignore
        def __init__(self, *args: Any, **kwargs: Any) -> None: pass
        def get(self, *args: Any, **kwargs: Any) -> Any: return lambda f: f
        def post(self, *args: Any, **kwargs: Any) -> Any: return lambda f: f

from ..schemas.qr import (
    QRCheckRequest,
    QRCheckResponse,
    PayeeDetails,
    QRVerificationChecks,
    NameMatchCheck,
    VPAReputationCheck,
    VPAPatternCheck,
    SemanticMatchCheck,
)
from ..services.qr_service import get_qr_service
from ..services.risk_engine import get_risk_engine
from ..services.gemini_service import get_gemini_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/check-qr", tags=["QR Shield"])


@router.post(
    "",
    response_model=QRCheckResponse,
    summary="Verify Payment QR Code",
    description=(
        "Performs real-time, deterministic identity verification on UPI QR payloads.\n\n"
        "**Verification Layers:**\n"
        "1. **Layer 1 (Expected Name Match):** Cross-checks user's intended merchant against decoded QR payee.\n"
        "2. **Layer 2 (VPA Reputation):** Checks authoritative registry for verified status or known fraud reports.\n"
        "3. **Layer 3 (VPA Pattern Heuristics):** Analyzes handle structure for personal vs commercial patterns.\n"
        "4. **Semantic Matching:** Disambiguates OCR typos and minor phonetic spelling differences."
    ),
)
def check_qr(request: QRCheckRequest) -> QRCheckResponse:
    """Verify a UPI QR payload against expected recipient and authoritative registry."""
    qr_service = get_qr_service()
    risk_engine = get_risk_engine()
    gemini_service = get_gemini_service()

    raw_qr = request.qr_data if hasattr(request, "qr_data") else getattr(request, "raw_payload", "")
    expected_name = getattr(request, "expected_name", None)

    # 1. Parse and Validate UPI QR
    is_valid, parsed_upi, error_msg = qr_service.parse_upi_qr(raw_qr)

    if not is_valid or not parsed_upi:
        logger.info(f"Invalid QR check rejected: {error_msg}")
        return QRCheckResponse(
            verdict="INVALID_QR",
            risk_score=100,
            confidence="high",
            payee=PayeeDetails(),
            expected_recipient=expected_name,
            checks=QRVerificationChecks(
                name_match=NameMatchCheck(status="not_provided", score=0),
                vpa_reputation=VPAReputationCheck(status="unknown"),
                vpa_pattern=VPAPatternCheck(status="caution", pattern_type="invalid"),
                semantic_match=SemanticMatchCheck(status="skipped", score=0),
            ),
            reasons=[error_msg or "The scanned QR code is not a valid UPI payment barcode."],
            recommendation="Do not scan or pay. Use an official payment QR code issued by the merchant.",
            explanation=f"QR parsing failed: {error_msg}",
            raw_payload=raw_qr,
            is_valid_upi=False,
            error_message=error_msg,
        )

    # 2. Run Deterministic Multi-Layer Risk Engine
    eval_result = risk_engine.evaluate_qr_payment(parsed_upi, expected_name)

    # 3. Generate Contextual AI Explanation (Non-Authoritative)
    explanation = gemini_service.generate_explanation(eval_result)

    # 4. Construct Structured Response
    checks = eval_result.get("checks", {})
    name_check = checks.get("name_match", {})
    rep_check = checks.get("vpa_reputation", {})
    pattern_check = checks.get("vpa_pattern", {})
    semantic_check = checks.get("semantic_match", {})

    return QRCheckResponse(
        verdict=eval_result["verdict"],
        risk_score=eval_result["risk_score"],
        confidence=eval_result["confidence"],
        payee=PayeeDetails(
            name=eval_result["payee"].get("name"),
            vpa=eval_result["payee"].get("vpa"),
            amount=eval_result["payee"].get("amount"),
            merchant_code=eval_result["payee"].get("merchant_code"),
            transaction_ref=eval_result["payee"].get("transaction_ref"),
            transaction_note=eval_result["payee"].get("transaction_note"),
            currency=eval_result["payee"].get("currency", "INR"),
        ),
        expected_recipient=expected_name,
        checks=QRVerificationChecks(
            name_match=NameMatchCheck(
                status=name_check.get("status", "not_provided"),
                score=name_check.get("score", 0),
                normalized_expected=name_check.get("normalized_expected"),
                normalized_payee=name_check.get("normalized_payee"),
            ),
            vpa_reputation=VPAReputationCheck(
                status=rep_check.get("status", "unknown"),
                risk_level=rep_check.get("risk_level"),
                reported_count=rep_check.get("reported_count", 0),
                trusted_since=rep_check.get("trusted_since"),
                category=rep_check.get("category"),
            ),
            vpa_pattern=VPAPatternCheck(
                status=pattern_check.get("status", "neutral"),
                pattern_type=pattern_check.get("pattern_type", "standard"),
                details=pattern_check.get("details"),
            ),
            semantic_match=SemanticMatchCheck(
                status=semantic_check.get("status", "skipped"),
                score=semantic_check.get("score", 0),
                matched_merchant=semantic_check.get("matched_merchant"),
                matched_vpa=semantic_check.get("matched_vpa"),
            ),
        ),
        reasons=eval_result.get("reasons", []),
        recommendation=eval_result.get("recommendation", ""),
        explanation=explanation,
        raw_payload=raw_qr,
        is_valid_upi=True,
        error_message=None,
    )
