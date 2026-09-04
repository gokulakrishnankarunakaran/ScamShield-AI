"""Structured Reputation Lookup Service for ScamShield AI.

Principle:
"VERIFY BEFORE YOU TRUST."
Provides deterministic evidence-based verification of payment Virtual Payment Addresses (VPAs).
Does not guess or hallucinate verdicts; relies strictly on authoritative data layer intelligence.
"""

import logging
from typing import Any, Dict, Optional
from ..database.mock_data import get_merchant_by_vpa

logger = logging.getLogger(__name__)


class ReputationService:
    """Deterministic payment identity reputation service."""

    def __init__(self) -> None:
        pass

    def lookup_vpa(self, vpa: str) -> Dict[str, Any]:
        """Perform deterministic reputation lookup for a given VPA.

        Returns a dictionary containing:
        - vpa: Normalized VPA string
        - status: 'verified' | 'reported_scam' | 'unknown'
        - risk_level: 'LOW' | 'HIGH' | 'CRITICAL' | 'MEDIUM'
        - is_known: bool
        - merchant: Merchant details if found, else None
        - evidence_source: Origin of determination
        - message: Clear deterministic summary
        """
        if not vpa or not isinstance(vpa, str) or "@" not in vpa:
            return {
                "vpa": vpa or "",
                "status": "unknown",
                "risk_level": "MEDIUM",
                "is_known": False,
                "merchant": None,
                "evidence_source": "ScamShield Deterministic Registry",
                "message": "Invalid or malformed VPA format.",
            }

        clean_vpa = vpa.strip().lower()
        merchant = get_merchant_by_vpa(clean_vpa)

        if merchant:
            status = merchant.get("status", "unknown")
            risk_level = merchant.get("risk_level", "LOW" if status == "verified" else "CRITICAL")
            
            if status == "verified":
                message = f"Verified Merchant: '{merchant.get('merchant_name')}' is registered and verified in good standing."
            elif status == "reported_scam":
                reported_cnt = merchant.get("reported_count", 1)
                message = (
                    f"CRITICAL WARNING: VPA '{clean_vpa}' is flagged as a REPORTED SCAM with "
                    f"{reported_cnt} active fraud incidents recorded in the registry."
                )
            else:
                message = f"Merchant profile exists with status: {status}."

            return {
                "vpa": clean_vpa,
                "status": status,
                "risk_level": risk_level,
                "is_known": True,
                "merchant": merchant,
                "evidence_source": "ScamShield Deterministic Registry",
                "message": message,
            }

        # VPA is not present in our database
        return {
            "vpa": clean_vpa,
            "status": "unknown",
            "risk_level": "MEDIUM",
            "is_known": False,
            "merchant": None,
            "evidence_source": "ScamShield Deterministic Registry",
            "message": f"Unknown VPA '{clean_vpa}'. No verified merchant record or fraud report on file.",
        }


_reputation_service_instance: Optional[ReputationService] = None


def get_reputation_service() -> ReputationService:
    """Return singleton ReputationService instance."""
    global _reputation_service_instance
    if _reputation_service_instance is None:
        _reputation_service_instance = ReputationService()
    return _reputation_service_instance

