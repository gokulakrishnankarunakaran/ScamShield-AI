"""Synthetic Demo Data Store for ScamShield AI.

DISCLAIMER:
==============================================================================
DEMO DATA — NOT REAL FRAUD INTELLIGENCE.
ALL MERCHANTS, VPAS, AND ENTITIES HERE ARE FICTIONAL DEMO ARTIFACTS
DESIGNED STRICTLY FOR HACKATHON SYSTEM VERIFICATION AND BENCHMARKING.
DO NOT USE REAL INDIVIDUALS' OR ENTITIES' UPI IDS.
==============================================================================
"""

import copy
import re
from typing import Dict, List, Optional, Any


def normalize_merchant_name(name: str) -> str:
    """Normalize merchant names by lowercasing, stripping special characters, and trimming extra spaces."""
    cleaned = re.sub(r"[^a-zA-Z0-9\s]", " ", name.lower())
    return " ".join(cleaned.split())


# Initial baseline synthetic dataset
MERCHANTS_DEMO_DATA: List[Dict[str, Any]] = [
    # -------------------------------------------------------------
    # 1. VERIFIED MERCHANTS (Legitimate registered business profiles)
    # -------------------------------------------------------------
    {
        "id": "merch_001",
        "merchant_name": "Sri Krishna Stores",
        "normalized_name": normalize_merchant_name("Sri Krishna Stores"),
        "vpa": "srikrishna.demo@okaxis",
        "status": "verified",
        "category": "Grocery & Supermarket",
        "risk_level": "LOW",
        "reported_count": 0,
        "trusted_since": "2022-01-15",
        "notes": "Verified brick-and-mortar neighborhood store.",
        "embedding_metadata": {
            "store_code": "SK-CHE-01",
            "aliases": ["Sri Krishna Stores", "Sri Krishna Provision Store", "Sri Krishna Groceries"]
        }
    },
    {
        "id": "merch_002",
        "merchant_name": "Chennai Fresh Mart",
        "normalized_name": normalize_merchant_name("Chennai Fresh Mart"),
        "vpa": "chennaifresh.demo@okicici",
        "status": "verified",
        "category": "Organic Fruits & Vegetables",
        "risk_level": "LOW",
        "reported_count": 0,
        "trusted_since": "2021-08-10",
        "notes": "Verified direct-farm organic retail outlet.",
        "embedding_metadata": {
            "store_code": "CFM-TN-04",
            "aliases": ["Chennai Fresh Mart", "Chennai Freshmart", "Fresh Mart Chennai"]
        }
    },
    {
        "id": "merch_003",
        "merchant_name": "Green Basket",
        "normalized_name": normalize_merchant_name("Green Basket"),
        "vpa": "greenbasket.demo@ybl",
        "status": "verified",
        "category": "Daily Essentials",
        "risk_level": "LOW",
        "reported_count": 0,
        "trusted_since": "2023-03-20",
        "notes": "Registered regional delivery chain.",
        "embedding_metadata": {
            "store_code": "GB-BLR-12",
            "aliases": ["Green Basket", "GreenBasket Daily", "The Green Basket"]
        }
    },
    {
        "id": "merch_004",
        "merchant_name": "Metro Electronics",
        "normalized_name": normalize_merchant_name("Metro Electronics"),
        "vpa": "metroelectronics.demo@okhdfc",
        "status": "verified",
        "category": "Consumer Electronics",
        "risk_level": "LOW",
        "reported_count": 0,
        "trusted_since": "2020-11-05",
        "notes": "Verified authorized appliance retailer.",
        "embedding_metadata": {
            "store_code": "METRO-ELEC-09",
            "aliases": ["Metro Electronics", "Metro Tech & Electronics", "Metro Electro Hub"]
        }
    },
    {
        "id": "merch_005",
        "merchant_name": "Lakshmi Textiles",
        "normalized_name": normalize_merchant_name("Lakshmi Textiles"),
        "vpa": "lakshmitextiles.demo@oksbi",
        "status": "verified",
        "category": "Apparel & Fabrics",
        "risk_level": "LOW",
        "reported_count": 0,
        "trusted_since": "2019-06-18",
        "notes": "Verified traditional silk and handloom showroom.",
        "embedding_metadata": {
            "store_code": "LT-COIM-03",
            "aliases": ["Lakshmi Textiles", "Lakshmi Silks and Textiles", "Sree Lakshmi Textiles"]
        }
    },

    # -------------------------------------------------------------
    # 2. REPORTED SCAM ENTITIES (High risk / fraudulent patterns)
    # -------------------------------------------------------------
    {
        "id": "scam_001",
        "merchant_name": "QuickReward Cashback Portal",
        "normalized_name": normalize_merchant_name("QuickReward Cashback Portal"),
        "vpa": "instantcashback.win@fakeupi",
        "status": "reported_scam",
        "category": "Phishing / Cashback Scam",
        "risk_level": "CRITICAL",
        "reported_count": 87,
        "trusted_since": None,
        "notes": "Phishing site promising instant 500% UPI cashback return on payment scan.",
        "embedding_metadata": {
            "scam_vector": "qr_refund_phishing",
            "aliases": ["Instant Cashback Win", "Quick Reward Club", "Cashback Claim Desk"]
        }
    },
    {
        "id": "scam_002",
        "merchant_name": "Electricity Bill Urgent Desk",
        "normalized_name": normalize_merchant_name("Electricity Bill Urgent Desk"),
        "vpa": "ebill.urgentpay@fakeaxis",
        "status": "reported_scam",
        "category": "Utility Disconnection Scam",
        "risk_level": "CRITICAL",
        "reported_count": 142,
        "trusted_since": None,
        "notes": "Impersonates electricity department threatening power cut in 30 minutes.",
        "embedding_metadata": {
            "scam_vector": "utility_impersonation",
            "aliases": ["Power Bill Support", "EB Urgency Pay", "State Electricity Pay Desk"]
        }
    },
    {
        "id": "scam_003",
        "merchant_name": "KYC Banking Verification Center",
        "normalized_name": normalize_merchant_name("KYC Banking Verification Center"),
        "vpa": "kycupdate.desk@fakeicici",
        "status": "reported_scam",
        "category": "Bank KYC Phishing",
        "risk_level": "CRITICAL",
        "reported_count": 215,
        "trusted_since": None,
        "notes": "Sends SMS claiming bank account suspended unless token fee paid to VPA.",
        "embedding_metadata": {
            "scam_vector": "kyc_impersonation",
            "aliases": ["KYC Update Center", "Account Verification Desk", "Bank Alert KYC"]
        }
    },
    {
        "id": "scam_004",
        "merchant_name": "International Lottery Tax Dept",
        "normalized_name": normalize_merchant_name("International Lottery Tax Dept"),
        "vpa": "prizewinner.customs@fakeybl",
        "status": "reported_scam",
        "category": "Lottery / Prize Advance Fee",
        "risk_level": "CRITICAL",
        "reported_count": 64,
        "trusted_since": None,
        "notes": "Demands advance GST processing fee to release non-existent prize money.",
        "embedding_metadata": {
            "scam_vector": "advance_fee_lottery",
            "aliases": ["Lottery Customs Clearance", "Prize Tax Counter", "Lucky Draw Bureau"]
        }
    },
    {
        "id": "scam_005",
        "merchant_name": "Work From Home Daily Payout",
        "normalized_name": normalize_merchant_name("Work From Home Daily Payout"),
        "vpa": "dailyincome.earn@fakeaxis",
        "status": "reported_scam",
        "category": "Part-time Job Task Scam",
        "risk_level": "HIGH",
        "reported_count": 53,
        "trusted_since": None,
        "notes": "Part-time task review scam demanding deposit to unlock higher payout levels.",
        "embedding_metadata": {
            "scam_vector": "task_investment_fraud",
            "aliases": ["Daily Income Earn", "VIP Task Bonus Hub", "Fast Earn Media"]
        }
    }
]

# Active runtime in-memory database
_CURRENT_MERCHANTS: List[Dict[str, Any]] = copy.deepcopy(MERCHANTS_DEMO_DATA)


def get_all_merchants() -> List[Dict[str, Any]]:
    """Return all mock merchants in the active dataset."""
    return copy.deepcopy(_CURRENT_MERCHANTS)


def get_merchant_by_vpa(vpa: str) -> Optional[Dict[str, Any]]:
    """Lookup merchant strictly by VPA (case-insensitive)."""
    if not vpa:
        return None
    vpa_clean = vpa.strip().lower()
    for item in _CURRENT_MERCHANTS:
        if item.get("vpa", "").lower() == vpa_clean:
            return copy.deepcopy(item)
    return None


def get_merchant_by_id(merchant_id: str) -> Optional[Dict[str, Any]]:
    """Lookup merchant by unique ID."""
    if not merchant_id:
        return None
    for item in _CURRENT_MERCHANTS:
        if item.get("id") == merchant_id:
            return copy.deepcopy(item)
    return None


def add_merchant(merchant: Dict[str, Any]) -> Dict[str, Any]:
    """Add a new merchant record to the mock database."""
    if "normalized_name" not in merchant and "merchant_name" in merchant:
        merchant["normalized_name"] = normalize_merchant_name(merchant["merchant_name"])
    _CURRENT_MERCHANTS.append(copy.deepcopy(merchant))
    return merchant


def reset_mock_data() -> int:
    """Reset the mock database back to the initial demo baseline."""
    global _CURRENT_MERCHANTS
    _CURRENT_MERCHANTS = copy.deepcopy(MERCHANTS_DEMO_DATA)
    return len(_CURRENT_MERCHANTS)
