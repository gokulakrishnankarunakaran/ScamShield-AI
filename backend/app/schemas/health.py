from typing import Any, Dict, Optional
try:
    from pydantic import BaseModel, Field
except ImportError:
    class BaseModel:  # type: ignore
        def __init__(self, **kwargs: Any) -> None:
            for k, v in kwargs.items():
                setattr(self, k, v)
        def model_dump(self) -> Dict[str, Any]:
            return self.__dict__
    def Field(*args: Any, **kwargs: Any) -> Any:  # type: ignore
        return kwargs.get("default", None)


class ComponentStatus(BaseModel):
    """Detailed status of an underlying subsystem."""
    status: str
    details: Optional[Dict[str, Any]] = None


class HealthResponse(BaseModel):
    """API Health Check Response Schema."""
    status: str = Field(default="ok", description="Overall health status")
    app: str = Field(default="ScamShield AI", description="Application name")
    version: str = Field(default="1.0.0", description="Application version")
    team: str = Field(default="CYBERTRON", description="Hackathon Team")
    actian_status: Optional[str] = Field(default="unavailable", description="Actian Vector status")
    actian_details: Optional[Dict[str, Any]] = Field(default=None, description="Actian Vector diagnostic telemetry")
    environment: Optional[str] = Field(default="development", description="Runtime environment")
