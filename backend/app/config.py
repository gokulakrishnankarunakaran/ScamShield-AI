"""Application Configuration Module for ScamShield AI.

Manages environment variables, database connection parameters, and API keys.
Adheres strictly to the 12-factor configuration pattern.
"""

import os
from pathlib import Path
from typing import List, Optional
from dataclasses import dataclass, field


def _load_dotenv_fallback(dotenv_path: Path) -> None:
    """Fallback .env parser if python-dotenv is not installed."""
    if not dotenv_path.exists():
        return
    try:
        with open(dotenv_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, val = line.split("=", 1)
                key = key.strip()
                val = val.strip().strip("'\"")
                if key and key not in os.environ:
                    os.environ[key] = val
    except Exception:
        pass


# Attempt to load .env from project root or backend directory
_backend_dir = Path(__file__).resolve().parent.parent
_project_root = _backend_dir.parent
_load_dotenv_fallback(_backend_dir / ".env")
_load_dotenv_fallback(_project_root / ".env")


@dataclass
class Settings:
    """ScamShield AI Settings container."""

    # Server Settings
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "info")

    # Google Gemini AI Settings
    GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY", "")

    # Actian VectorAI / Actian Vector Database Settings
    ACTIAN_HOST: str = os.getenv("ACTIAN_HOST", "localhost")
    ACTIAN_PORT: int = int(os.getenv("ACTIAN_PORT", "27839"))
    ACTIAN_DATABASE: str = os.getenv("ACTIAN_DATABASE", "scamshield_vectors")
    ACTIAN_USER: str = os.getenv("ACTIAN_USER", "actian")
    ACTIAN_PASSWORD: Optional[str] = os.getenv("ACTIAN_PASSWORD", "")
    ACTIAN_TABLE_NAME: str = os.getenv("ACTIAN_TABLE_NAME", "merchant_vectors")
    ACTIAN_ENABLED: bool = os.getenv("ACTIAN_ENABLED", "true").lower() in ("true", "1", "yes")

    # Application Security
    CORS_ORIGINS: List[str] = field(
        default_factory=lambda: ["http://localhost:3000", "http://localhost:8080", "*"]
    )

    @property
    def is_actian_configured(self) -> bool:
        """Check if Actian connection parameters are configured."""
        return bool(self.ACTIAN_HOST and self.ACTIAN_DATABASE and self.ACTIAN_ENABLED)

    @property
    def is_gemini_configured(self) -> bool:
        """Check if Gemini API key is configured."""
        return bool(self.GEMINI_API_KEY and self.GEMINI_API_KEY != "your_gemini_api_key_here")


_settings_instance: Optional[Settings] = None


def get_settings() -> Settings:
    """Return a singleton Settings instance."""
    global _settings_instance
    if _settings_instance is None:
        _settings_instance = Settings()
    return _settings_instance

