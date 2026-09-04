"""Multi-Signal Risk Assessment and Verdict Engine for ScamShield AI.

Team CYBERTRON.
Product Principle: "VERIFY BEFORE YOU TRUST."
Centralizes all risk scoring, deterministic evidence evaluation, and verdict generation.
Authoritative deterministic identity evidence ALWAYS takes precedence over weak heuristics.
"""

import logging
from typing import Any, Dict, List, Optional

from .reputation_service import ReputationService, get_reputation_service
from .vector_service import VectorService, get_vector_service
from .qr_service import QRService, get_qr_service

logger = logging.getLogger(__name__)


class RiskEngine:
    """Deterministic Multi-Layer Risk Engine for QR and Payment Identity Verification."""

    # Risk Thresholds
    GREEN_THRESHOLD = 20
    RED_THRESHOLD = 60

    def __init__(
        self,
        reputation_service: Optional[ReputationService] = None,
        vector_service: Optional[VectorService] = None,
        qr_service: Optional[QRService] = None,
    ) -> None:
        self.reputation_service = reputation_service or get_reputation_service()
        self.vector_service = vector_service or get_vector_service()
        self.qr_service = qr_service or get_qr_service()

    def evaluate_qr_payment(
        self,
        parsed_upi: Dict[str, Any],
        expected_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Evaluate decoded UPI QR payment across all independent verification layers.

        Returns comprehensive assessment matching the standard ScamShield response format.
        """
        vpa = parsed_upi.get("vpa", "")
        payee_name = parsed_upi.get("payee_name")
        merchant_code = parsed_upi.get("merchant_code")

        reasons: List[str] = []
        checks_data: Dict[str, Any] = {}

        # -------------------------------------------------------------
        # LAYER 2: Authoritative VPA Reputation Lookup
        # -------------------------------------------------------------
        rep_result = self.reputation_service.lookup_vpa(vpa)
        rep_status = rep_result.get("status", "unknown")
        rep_merchant = rep_result.get("merchant")

        checks_data["vpa_reputation"] = {
            "status": rep_status,
            "risk_level": rep_result.get("risk_level"),
            "reported_count": rep_merchant.get("reported_count", 0) if rep_merchant else 0,
            "trusted_since": rep_merchant.get("trusted_since") if rep_merchant else None,
            "category": rep_merchant.get("category") if rep_merchant else None,
        }

        # -------------------------------------------------------------
        # HARD RED SHORT-CIRCUIT: Known Scam VPA
        # -------------------------------------------------------------
        if rep_status == "reported_scam":
            reported_cnt = rep_merchant.get("reported_count", 1) if rep_merchant else 1
            category = rep_merchant.get("category", "Fraudulent Entity") if rep_merchant else "Fraudulent Entity"
            reasons.append(
                f"CRITICAL FRAUD ALERT: VPA '{vpa}' is flagged as a KNOWN SCAM ({category}) with "
                f"{reported_cnt} active incident reports in the registry."
            )
            if expected_name and payee_name:
                reasons.append(f"QR Payee: '{payee_name}' | Expected: '{expected_name}'.")

            return {
                "verdict": "RED",
                "risk_score": 98,
                "confidence": "high",
                "payee": {
                    "name": payee_name,
                    "vpa": vpa,
                    "amount": parsed_upi.get("amount"),
                    "merchant_code": merchant_code,
                    "transaction_ref": parsed_upi.get("transaction_ref"),
                    "transaction_note": parsed_upi.get("transaction_note"),
                    "currency": parsed_upi.get("currency", "INR"),
                },
                "expected_recipient": expected_name,
                "checks": {
                    "name_match": {"status": "mismatch" if expected_name else "not_provided", "score": 0},
                    "vpa_reputation": checks_data["vpa_reputation"],
                    "vpa_pattern": {"status": "caution", "pattern_type": "scam_registered"},
                    "semantic_match": {"status": "skipped", "score": 0},
                },
                "reasons": reasons,
                "recommendation": "DO NOT PAY. This payment destination is confirmed fraudulent.",
                "explanation": (
                    f"ScamShield blocked this transaction. The recipient identifier ({vpa}) matches "
                    f"an active fraud registry entry ({category})."
                ),
            }

        # -------------------------------------------------------------
        # LAYER 1: Name Matching (Expected vs QR Decoded)
        # -------------------------------------------------------------
        name_match = self.qr_service.match_names(expected_name, payee_name)
        checks_data["name_match"] = {
            "status": name_match["status"],
            "score": name_match["score"],
            "normalized_expected": name_match.get("normalized_expected"),
            "normalized_payee": name_match.get("normalized_payee"),
        }

        # -------------------------------------------------------------
        # LAYER 3: VPA Pattern Analysis
        # -------------------------------------------------------------
        pattern_check = self.qr_service.analyze_vpa_pattern(vpa, merchant_code)
        checks_data["vpa_pattern"] = {
            "status": pattern_check["status"],
            "pattern_type": pattern_check["pattern_type"],
            "details": pattern_check["details"],
        }

        # -------------------------------------------------------------
        # SEMANTIC / VECTOR MATCHING (Disambiguation for Typos/OCR)
        # -------------------------------------------------------------
        semantic_status = "skipped"
        semantic_score = 0
        matched_merchant_name = None
        matched_merchant_vpa = None

        if expected_name and name_match["status"] in ("possible_match", "mismatch"):
            # Check 1: Direct semantic/phonetic similarity between expected_name and decoded QR payee_name
            if payee_name:
                sim = self.vector_service.calculate_similarity(expected_name, payee_name)
                semantic_score = int(round(sim * 100))
                if sim >= 0.80:
                    semantic_status = "match"
                    matched_merchant_name = payee_name
                    matched_merchant_vpa = vpa
                elif sim >= 0.60:
                    semantic_status = "possible_match"
                    matched_merchant_name = payee_name
                    matched_merchant_vpa = vpa
                else:
                    semantic_status = "not_match"

            # Check 2: If the QR VPA belongs to a known registered merchant, check if registered name matches
            if semantic_status in ("skipped", "not_match") and rep_merchant:
                reg_name = rep_merchant.get("merchant_name", "")
                reg_sim = self.vector_service.calculate_similarity(expected_name, reg_name)
                if reg_sim >= 0.80:
                    semantic_status = "match"
                    semantic_score = int(round(reg_sim * 100))
                    matched_merchant_name = reg_name
                    matched_merchant_vpa = vpa

        checks_data["semantic_match"] = {
            "status": semantic_status,
            "score": semantic_score,
            "matched_merchant": matched_merchant_name,
            "matched_vpa": matched_merchant_vpa,
        }

        # -------------------------------------------------------------
        # SCORING ALGORITHM
        # -------------------------------------------------------------
        # Base baseline score for any standard unverified transaction
        score = 25
        confidence = "medium"

        # 1. Evaluate Name Match
        if name_match["status"] == "exact":
            score -= 25
            reasons.append(f"Name Match: Payee name '{payee_name}' exactly matches your expected recipient.")
            confidence = "high"
        elif name_match["status"] == "strong_match":
            score -= 15
            reasons.append(f"Name Match: Payee name '{payee_name}' closely matches '{expected_name}'.")
            confidence = "high"
        elif name_match["status"] == "possible_match":
            if semantic_status in ("match", "possible_match"):
                score -= 10
                reasons.append(
                    f"Semantic Resolution: '{payee_name}' is identified as a phonetic/spelling variation of '{expected_name}'."
                )
                confidence = "high"
            else:
                score += 15
                reasons.append(
                    f"Partial Match: Payee name '{payee_name}' only partially matches expected '{expected_name}'."
                )
        elif name_match["status"] == "mismatch":
            if semantic_status == "match":
                score -= 5
                reasons.append(
                    f"Semantic Match: Detected alias/registered entity '{matched_merchant_name}' matching '{expected_name}'."
                )
            else:
                score += 55
                reasons.append(
                    f"IDENTITY MISMATCH: QR payee name is '{payee_name or 'Unspecified'}', but you entered '{expected_name}'."
                )
                confidence = "high"
        elif name_match["status"] == "not_provided":
            if payee_name:
                reasons.append(f"QR Payee: '{payee_name}'. (No expected recipient name was specified for cross-check).")
            else:
                score += 15
                reasons.append("QR code does not contain a verified payee name.")

        # 2. Evaluate Reputation
        if rep_status == "verified":
            score -= 35
            merchant_name = rep_merchant.get("merchant_name") if rep_merchant else "Registered Merchant"
            reasons.append(f"Verified Merchant: VPA '{vpa}' belongs to registered merchant '{merchant_name}' in good standing.")
            confidence = "high"
        elif rep_status == "unknown":
            # Neutral signal: VPA is not in our verified registry
            if name_match["status"] == "not_provided":
                reasons.append(f"VPA '{vpa}' is not in the pre-verified business registry.")

        # 3. Evaluate VPA Pattern Heuristic (Weak signal)
        if pattern_check["status"] == "caution":
            if expected_name and rep_status != "verified":
                score += 15
                reasons.append(
                    f"Pattern Caution: VPA '{vpa}' appears to be a personal/individual handle rather than an official business account."
                )
        elif pattern_check["status"] == "positive":
            score -= 5

        # Clamp score between 0 and 100
        risk_score = max(0, min(100, score))

        # -------------------------------------------------------------
        # VERDICT & RECOMMENDATIONS
        # -------------------------------------------------------------
        if risk_score < self.GREEN_THRESHOLD:
            verdict = "GREEN"
            recommendation = "Identity confirmed. Recipient matches your intended receiver and is safe to pay."
        elif risk_score < self.RED_THRESHOLD:
            verdict = "YELLOW"
            recommendation = "Caution advised. Confirm the payee name on the cashier/payment screen before entering your UPI PIN."
        else:
            verdict = "RED"
            recommendation = "Do NOT proceed with payment until the recipient identity is verified."

        return {
            "verdict": verdict,
            "risk_score": risk_score,
            "confidence": confidence,
            "payee": {
                "name": payee_name,
                "vpa": vpa,
                "amount": parsed_upi.get("amount"),
                "merchant_code": merchant_code,
                "transaction_ref": parsed_upi.get("transaction_ref"),
                "transaction_note": parsed_upi.get("transaction_note"),
                "currency": parsed_upi.get("currency", "INR"),
            },
            "expected_recipient": expected_name,
            "checks": checks_data,
            "reasons": reasons,
            "recommendation": recommendation,
            "explanation": " ".join(reasons),
        }


_risk_engine_instance: Optional[RiskEngine] = None


def get_risk_engine() -> RiskEngine:
    """Return singleton RiskEngine instance."""
    global _risk_engine_instance
    if _risk_engine_instance is None:
        _risk_engine_instance = RiskEngine()
    return _risk_engine_instance
