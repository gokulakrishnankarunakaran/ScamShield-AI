"""UPI QR Code Parsing, Validation, and Layered Signal Extraction Service.

Team CYBERTRON.
Product Principle: "VERIFY BEFORE YOU TRUST."
Provides deterministic parsing of UPI QR payloads, normalized name comparison,
and structural VPA pattern analysis.
"""

import re
import urllib.parse
from typing import Any, Dict, Optional, Tuple

try:
    from rapidfuzz import fuzz  # type: ignore
    RAPIDFUZZ_AVAILABLE = True
except ImportError:
    RAPIDFUZZ_AVAILABLE = False


def _levenshtein_ratio(s1: str, s2: str) -> float:
    """Fallback Levenshtein similarity ratio between 0.0 and 1.0."""
    if s1 == s2:
        return 1.0
    if not s1 or not s2:
        return 0.0
    len1, len2 = len(s1), len(s2)
    dp = [[0] * (len2 + 1) for _ in range(len1 + 1)]
    for i in range(len1 + 1):
        dp[i][0] = i
    for j in range(len2 + 1):
        dp[0][j] = j
    for i in range(1, len1 + 1):
        for j in range(1, len2 + 1):
            cost = 0 if s1[i - 1] == s2[j - 1] else 1
            dp[i][j] = min(dp[i - 1][j] + 1, dp[i][j - 1] + 1, dp[i - 1][j - 1] + cost)
    distance = dp[len1][len2]
    max_len = max(len1, len2)
    return max(0.0, 1.0 - (distance / max_len))


def _token_sort_ratio_fallback(s1: str, s2: str) -> int:
    """Fallback Token Sort Ratio implementation matching RapidFuzz behavior (0-100)."""
    t1 = " ".join(sorted(s1.split()))
    t2 = " ".join(sorted(s2.split()))
    ratio = _levenshtein_ratio(t1, t2)
    return int(round(ratio * 100))


def normalize_name(text: Optional[str]) -> str:
    """Normalize merchant / recipient names by removing punctuation and extra whitespace."""
    if not text:
        return ""
    # Lowercase and replace non-alphanumeric chars with spaces
    cleaned = re.sub(r"[^a-zA-Z0-9\s]", " ", text.lower())
    # Collapse multiple whitespace characters into single space
    return " ".join(cleaned.split())


class QRService:
    """Service handling UPI QR parsing, Layer 1 Name Matching, and Layer 3 VPA Pattern Analysis."""

    MAX_PAYLOAD_LENGTH = 2048

    def __init__(self) -> None:
        pass

    def parse_upi_qr(self, raw_payload: str) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """Parse raw QR code payload using standard urllib.parse.

        Returns:
            (is_valid, parsed_dict, error_message)
        """
        if not raw_payload or not isinstance(raw_payload, str):
            return False, None, "QR payload is empty or invalid."

        payload = raw_payload.strip()

        if len(payload) > self.MAX_PAYLOAD_LENGTH:
            return False, None, f"QR payload exceeds maximum safe length ({self.MAX_PAYLOAD_LENGTH} characters)."

        # Validate URI Scheme
        if not payload.lower().startswith("upi://"):
            return False, None, "Unsupported QR scheme. Only UPI payment QR codes ('upi://pay') are supported."

        try:
            parsed_url = urllib.parse.urlparse(payload)
        except Exception as e:
            return False, None, f"Malformed QR URI structure: {str(e)}"

        # Query parameter extraction
        query_str = parsed_url.query
        if not query_str and "?" in payload:
            query_str = payload.split("?", 1)[1]

        params = urllib.parse.parse_qs(query_str, keep_blank_values=True)
        
        # Flatten dictionary
        flat_params: Dict[str, str] = {}
        for k, v in params.items():
            flat_params[k.lower()] = v[0] if v else ""

        # Extract pa (Virtual Payment Address / VPA) - MANDATORY
        vpa = flat_params.get("pa", "").strip()
        if not vpa:
            return False, None, "Invalid UPI QR: Mandatory payee address ('pa') parameter is missing."

        if "@" not in vpa:
            return False, None, f"Invalid UPI VPA format ('{vpa}'): Missing handle delimiter '@'."

        # Extract pn (Payee Name)
        payee_name = flat_params.get("pn", "").strip()
        if not payee_name:
            payee_name = None

        # Extract am (Amount)
        amount_raw = flat_params.get("am", "").strip()
        amount: Optional[float] = None
        if amount_raw:
            try:
                parsed_am = float(amount_raw)
                if parsed_am > 0:
                    amount = parsed_am
            except ValueError:
                amount = None

        # Extract mc (Merchant Code)
        mc = flat_params.get("mc", "").strip() or None

        # Extract tr (Transaction Reference)
        tr = flat_params.get("tr", "").strip() or None

        # Extract tn (Transaction Note)
        tn = flat_params.get("tn", "").strip() or None

        # Extract cu (Currency)
        cu = flat_params.get("cu", "INR").strip().upper() or "INR"

        result = {
            "vpa": vpa.lower(),
            "payee_name": payee_name,
            "amount": amount,
            "merchant_code": mc,
            "transaction_ref": tr,
            "transaction_note": tn,
            "currency": cu,
            "raw_params": flat_params,
        }

        return True, result, None

    def match_names(self, expected_name: Optional[str], payee_name: Optional[str]) -> Dict[str, Any]:
        """Layer 1: Compare expected name entered by user against decoded QR payee name.

        Uses RapidFuzz (or Levenshtein ratio fallback) with normalization.
        """
        if not expected_name or not expected_name.strip():
            return {
                "status": "not_provided",
                "score": 0,
                "normalized_expected": None,
                "normalized_payee": normalize_name(payee_name) if payee_name else None,
                "details": "User did not specify an expected recipient name.",
            }

        if not payee_name or not payee_name.strip():
            return {
                "status": "mismatch",
                "score": 0,
                "normalized_expected": normalize_name(expected_name),
                "normalized_payee": None,
                "details": "QR code does not contain a payee name ('pn') parameter.",
            }

        norm_expected = normalize_name(expected_name)
        norm_payee = normalize_name(payee_name)

        if norm_expected == norm_payee:
            score = 100
        elif RAPIDFUZZ_AVAILABLE:
            # Use Token Sort Ratio to handle word order variations (e.g. "Stores Sri Krishna" vs "Sri Krishna Stores")
            token_score = int(round(fuzz.token_sort_ratio(norm_expected, norm_payee)))
            ratio_score = int(round(fuzz.ratio(norm_expected, norm_payee)))
            score = max(token_score, ratio_score)
        else:
            token_score = _token_sort_ratio_fallback(norm_expected, norm_payee)
            ratio_score = int(round(_levenshtein_ratio(norm_expected, norm_payee) * 100))
            score = max(token_score, ratio_score)

        # Categorize match type
        if score >= 90:
            status = "exact" if score >= 98 else "strong_match"
        elif score >= 60:
            status = "possible_match"
        else:
            status = "mismatch"

        return {
            "status": status,
            "score": score,
            "normalized_expected": norm_expected,
            "normalized_payee": norm_payee,
            "details": f"Name similarity score: {score}% ({status}).",
        }

    def analyze_vpa_pattern(self, vpa: str, merchant_code: Optional[str] = None) -> Dict[str, Any]:
        """Layer 3: Lightweight heuristic analysis of VPA structure (weak signal only).

        Never marks a VPA fraudulent by itself; provides contextual signal.
        """
        if not vpa or "@" not in vpa:
            return {
                "status": "caution",
                "pattern_type": "invalid",
                "details": "Malformed or invalid VPA handle.",
            }

        handle, psp = vpa.split("@", 1)
        handle = handle.lower()
        psp = psp.lower()

        # Phone number handle (e.g. 9876543210@ybl, 919876543210@paytm)
        if re.match(r"^(?:\+?91)?[6-9]\d{9}$", handle):
            return {
                "status": "caution",
                "pattern_type": "phone_handle",
                "details": f"VPA uses an individual mobile phone number handle (@{psp}).",
            }

        # Personal bank handle patterns (e.g., john123@okhdfc, rahul.kumar88@okaxis)
        personal_psps = {"okhdfcbank", "okhdfc", "okaxis", "oksbi", "okicici", "apl"}
        if psp in personal_psps and re.search(r"\d{2,}$", handle):
            return {
                "status": "caution",
                "pattern_type": "personal_handle",
                "details": f"VPA structure matches an individual personal account pattern (@{psp}).",
            }

        # Dedicated merchant aggregator handle or merchant code present
        merchant_psps = {"paytmqr", "bharatpe", "phonepe", "icici", "hdfcbank", "axisbank"}
        if merchant_code or any(mp in psp or mp in handle for mp in merchant_psps):
            return {
                "status": "positive",
                "pattern_type": "merchant_handle",
                "details": f"VPA matches standard merchant payment gateway structure (@{psp}).",
            }

        return {
            "status": "neutral",
            "pattern_type": "standard",
            "details": f"Standard VPA handle (@{psp}).",
        }


_qr_service_instance: Optional[QRService] = None


def get_qr_service() -> QRService:
    """Return singleton QRService instance."""
    global _qr_service_instance
    if _qr_service_instance is None:
        _qr_service_instance = QRService()
    return _qr_service_instance
