from typing import Any
try:
    from fastapi import APIRouter
except ImportError:
    class APIRouter:  # type: ignore
        def __init__(self, *args: Any, **kwargs: Any) -> None: pass
        def get(self, *args: Any, **kwargs: Any) -> Any:
            return lambda f: f
        def post(self, *args: Any, **kwargs: Any) -> Any:
            return lambda f: f
from ..schemas.screenshot import ScreenshotCheckRequest, ScreenshotCheckResponse

router = APIRouter(prefix="/check-screenshot", tags=["Screenshot Verifier"])


@router.post("", response_model=ScreenshotCheckResponse)
def check_screenshot(request: ScreenshotCheckRequest) -> ScreenshotCheckResponse:
    """Scaffolded endpoint for Screenshot Verification (Phase 2 full implementation).

    Performs contract validation and placeholders.
    """
    return ScreenshotCheckResponse(
        status="pending_implementation_phase_2",
        fraud_indicators=["Screenshot OCR & Vision pipeline is scheduled for Phase 2 implementation."],
        explanation="Phase 1 architecture scaffolding is active. Full screenshot analysis will activate in Phase 2.",
    )
