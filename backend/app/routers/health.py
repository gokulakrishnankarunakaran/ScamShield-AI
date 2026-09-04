try:
    from fastapi import APIRouter
except ImportError:
    class APIRouter:  # type: ignore
        def __init__(self, *args: Any, **kwargs: Any) -> None: pass
        def get(self, *args: Any, **kwargs: Any) -> Any:
            return lambda f: f
        def post(self, *args: Any, **kwargs: Any) -> Any:
            return lambda f: f

from typing import Any
from ..config import get_settings
from ..database.actian import get_actian_client
from ..schemas.health import HealthResponse

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse)
def get_health() -> HealthResponse:
    """Check API server health, version, and database connectivity."""
    settings = get_settings()
    actian_client = get_actian_client()
    actian_status_data = actian_client.get_status()

    return HealthResponse(
        status="ok",
        app="ScamShield AI",
        version="1.0.0",
        team="CYBERTRON",
        actian_status=actian_status_data.get("status", "unavailable"),
        actian_details=actian_status_data,
        environment=settings.ENVIRONMENT,
    )
