from typing import Any, Dict, List
try:
    from fastapi import APIRouter
except ImportError:
    class APIRouter:  # type: ignore
        def __init__(self, *args: Any, **kwargs: Any) -> None: pass
        def get(self, *args: Any, **kwargs: Any) -> Any:
            return lambda f: f
        def post(self, *args: Any, **kwargs: Any) -> Any:
            return lambda f: f
from ..database.mock_data import get_all_merchants, reset_mock_data
from ..services.vector_service import get_vector_service

router = APIRouter(prefix="/demo", tags=["Demo Management"])


@router.get("/merchants", response_model=List[Dict[str, Any]])
def list_demo_merchants() -> List[Dict[str, Any]]:
    """List all synthetic merchants in the active demo dataset."""
    return get_all_merchants()


@router.post("/reset")
def reset_demo() -> Dict[str, Any]:
    """Reset the demo dataset and vector index to initial baseline."""
    count = reset_mock_data()
    vector_svc = get_vector_service()
    vector_svc._in_memory_index.clear()
    vector_svc._bootstrap_index()
    return {
        "status": "success",
        "message": "Demo merchants dataset and vector index successfully reset to baseline.",
        "merchant_count": count,
    }
