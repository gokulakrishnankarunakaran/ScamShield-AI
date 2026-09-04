"""Database package for ScamShield AI.

Includes Actian VectorAI client abstraction and demo/mock data stores.
"""

from .actian import ActianVectorClient, get_actian_client
from .mock_data import (
    MERCHANTS_DEMO_DATA,
    get_all_merchants,
    get_merchant_by_vpa,
    get_merchant_by_id,
    reset_mock_data,
)

__all__ = [
    "ActianVectorClient",
    "get_actian_client",
    "MERCHANTS_DEMO_DATA",
    "get_all_merchants",
    "get_merchant_by_vpa",
    "get_merchant_by_id",
    "reset_mock_data",
]

