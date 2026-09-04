"""Google Gemini AI Contextual Explanation Service Interface.

Team CYBERTRON.
Product Principle: "VERIFY BEFORE YOU TRUST."
CRITICAL RULE:
Deterministic evidence is authoritative.
Gemini explains evidence; Gemini NEVER determines or overrides verdicts or scores.
"""

import logging
from typing import Any, Dict, Optional
from ..config import get_settings

logger = logging.getLogger(__name__)


class GeminiService:
    """Contextual Explanation Generator backed by Google Gemini AI (Phase 2 Interface)."""

    def __init__(self) -> None:
        self.settings = get_settings()
        self._is_active: bool = False
        self._initialize_gemini()

    def _initialize_gemini(self) -> None:
        """Inspect and initialize Gemini client if configured."""
        if self.settings.is_gemini_configured:
            try:
                # In Phase 2, verify SDK availability
                logger.info("Gemini API key configured. AI explanation service ready.")
                self._is_active = True
            except Exception as e:
                logger.warning(f"Failed to initialize Gemini client: {e}")
                self._is_active = False
        else:
            logger.info("Gemini API key not configured. Using deterministic explanation templates.")
            self._is_active = False

    @property
    def is_available(self) -> bool:
        """Return True if Gemini LLM engine is online and configured."""
        return self._is_active

    def generate_explanation(self, verification_result: Dict[str, Any]) -> str:
        """Generate a concise, human-readable contextual explanation of the verification evidence.

        CRITICAL INTEGRITY CONSTRAINTS:
        - NEVER modifies the verdict or risk score.
        - Translates deterministic evidence into plain-language warnings.
        """
        verdict = verification_result.get("verdict", "YELLOW")
        reasons = verification_result.get("reasons", [])
        payee = verification_result.get("payee", {})
        payee_name = payee.get("name") or "Unspecified Payee"
        vpa = payee.get("vpa") or "unknown VPA"
        expected = verification_result.get("expected_recipient")

        # If Gemini is configured and active in future, call LLM to summarize
        # Otherwise, synthesize a deterministic narrative from the verified evidence:
        if verdict == "RED":
            if any("KNOWN SCAM" in r or "CRITICAL FRAUD" in r for r in reasons):
                return (
                    f"CRITICAL WARNING: The QR code points to '{vpa}', which is flagged as a reported scam "
                    f"in the fraud database. Proceeding with this payment will likely result in permanent financial loss."
                )
            elif expected and expected != payee_name:
                return (
                    f"IDENTITY ALERT: You indicated you intended to pay '{expected}', but this QR code directs funds to "
                    f"'{payee_name}' ({vpa}). These identities do not match. Do not scan or pay."
                )
            else:
                return (
                    f"HIGH RISK DETECTED: This payment destination ({vpa}) exhibits multiple high-risk fraud signals. "
                    f"Payment has been blocked by ScamShield."
                )

        elif verdict == "GREEN":
            if expected:
                return (
                    f"VERIFICATION SUCCESSFUL: The QR payee '{payee_name}' matches your intended recipient '{expected}', "
                    f"and the payment address ({vpa}) is verified in good standing."
                )
            else:
                return f"VERIFIED RECIPIENT: VPA '{vpa}' belongs to registered merchant '{payee_name}'."

        else:  # YELLOW
            if expected:
                return (
                    f"ATTENTION: Payee '{payee_name}' only partially resembles '{expected}'. "
                    f"Please confirm the merchant name at the billing counter before completing the transaction."
                )
            else:
                return (
                    f"UNVERIFIED RECIPIENT: VPA '{vpa}' is not in the verified business registry. "
                    f"Please verify the cashier name before paying."
                )


_gemini_service_instance: Optional[GeminiService] = None


def get_gemini_service() -> GeminiService:
    """Return singleton GeminiService instance."""
    global _gemini_service_instance
    if _gemini_service_instance is None:
        _gemini_service_instance = GeminiService()
    return _gemini_service_instance
