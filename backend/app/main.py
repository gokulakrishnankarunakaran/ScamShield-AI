"""ScamShield AI — Core Backend API.

Team CYBERTRON.
Product Principle: "VERIFY BEFORE YOU TRUST."
Deterministic evidence first; AI explanation second.
"""

import sys
import logging
from typing import Any, Dict

# Setup structured logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("scamshield_api")

try:
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False
    logger.warning("FastAPI not installed in current environment. Using standard HTTP fallback runner.")

from .config import get_settings
from .routers.health import router as health_router
from .routers.qr import router as qr_router
from .routers.screenshot import router as screenshot_router
from .routers.demo import router as demo_router

settings = get_settings()


def create_app() -> Any:
    """Initialize and configure the FastAPI application instance."""
    if not FASTAPI_AVAILABLE:
        return None

    app = FastAPI(
        title="ScamShield AI API",
        description=(
            "Deterministic Payment Security & Scam Detection Engine for Team CYBERTRON.\n\n"
            "Core Principle: 'VERIFY BEFORE YOU TRUST'."
        ),
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # Configure CORS for multi-platform clients (Flutter mobile, web, desktop)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register API Routers
    app.include_router(health_router)
    app.include_router(qr_router)
    app.include_router(screenshot_router)
    app.include_router(demo_router)

    @app.get("/")
    def root() -> Dict[str, Any]:
        return {
            "app": "ScamShield AI API",
            "team": "CYBERTRON",
            "version": "1.0.0",
            "status": "online",
            "principle": "VERIFY BEFORE YOU TRUST",
            "health_endpoint": "/health",
            "docs": "/docs",
        }

    return app


app = create_app()


def run_standalone_server(host: str = "127.0.0.1", port: int = 8000) -> None:
    """Run server with uvicorn if available, or standard HTTP server as a robust fallback."""
    try:
        import uvicorn
        logger.info(f"Starting ScamShield Uvicorn server on http://{host}:{port}")
        uvicorn.run("backend.app.main:app", host=host, port=port, reload=False)
    except ImportError:
        # Standard library HTTP server fallback to ensure GET /health works in any offline/standard Python env
        import json
        from http.server import HTTPServer, BaseHTTPRequestHandler
        from .database.actian import get_actian_client
        from .database.mock_data import get_all_merchants, reset_mock_data

        class StandaloneHandler(BaseHTTPRequestHandler):
            def do_GET(self) -> None:
                if self.path == "/health":
                    actian_client = get_actian_client()
                    status_payload = {
                        "status": "ok",
                        "app": "ScamShield AI",
                        "version": "1.0.0",
                        "team": "CYBERTRON",
                        "actian_status": actian_client.get_status().get("status", "unavailable"),
                        "environment": settings.ENVIRONMENT,
                    }
                    self._send_json(200, status_payload)
                elif self.path == "/" or self.path == "":
                    self._send_json(200, {
                        "app": "ScamShield AI API",
                        "team": "CYBERTRON",
                        "status": "online",
                        "health_endpoint": "/health"
                    })
                elif self.path == "/demo/merchants":
                    self._send_json(200, get_all_merchants())
                else:
                    self._send_json(404, {"detail": "Not Found"})

            def do_POST(self) -> None:
                content_length = int(self.headers.get("Content-Length", 0))
                post_body = self.rfile.read(content_length).decode("utf-8") if content_length > 0 else "{}"
                try:
                    payload = json.loads(post_body)
                except Exception:
                    payload = {}

                if self.path == "/check-qr":
                    from .services.qr_service import get_qr_service
                    from .services.risk_engine import get_risk_engine
                    from .services.gemini_service import get_gemini_service

                    raw_qr = payload.get("qr_data") or payload.get("raw_payload", "")
                    expected_name = payload.get("expected_name")

                    qr_svc = get_qr_service()
                    risk_eng = get_risk_engine()
                    gemini_svc = get_gemini_service()

                    is_valid, parsed_upi, error_msg = qr_svc.parse_upi_qr(raw_qr)

                    if not is_valid or not parsed_upi:
                        result = {
                            "verdict": "INVALID_QR",
                            "risk_score": 100,
                            "confidence": "high",
                            "payee": {},
                            "expected_recipient": expected_name,
                            "checks": {
                                "name_match": {"status": "not_provided", "score": 0},
                                "vpa_reputation": {"status": "unknown"},
                                "vpa_pattern": {"status": "caution", "pattern_type": "invalid"},
                                "semantic_match": {"status": "skipped", "score": 0},
                            },
                            "reasons": [error_msg or "Invalid UPI QR code."],
                            "recommendation": "Do not scan or pay. Use an official payment QR code issued by the merchant.",
                            "explanation": f"QR parsing failed: {error_msg}",
                            "raw_payload": raw_qr,
                            "is_valid_upi": False,
                            "error_message": error_msg,
                        }
                    else:
                        result = risk_eng.evaluate_qr_payment(parsed_upi, expected_name)
                        result["explanation"] = gemini_svc.generate_explanation(result)
                        result["raw_payload"] = raw_qr
                        result["is_valid_upi"] = True
                        result["error_message"] = None

                    self._send_json(200, result)
                elif self.path == "/check-screenshot":
                    self._send_json(200, {
                        "status": "pending_implementation_phase_3",
                        "fraud_indicators": ["Screenshot OCR & Vision pipeline scheduled for Phase 3."]
                    })
                elif self.path == "/demo/reset":
                    cnt = reset_mock_data()
                    self._send_json(200, {"status": "success", "merchant_count": cnt})
                else:
                    self._send_json(404, {"detail": "Not Found"})

            def _send_json(self, status_code: int, data: Any) -> None:
                body = json.dumps(data, indent=2).encode("utf-8")
                self.send_response(status_code)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(body)

            def log_message(self, format: str, *args: Any) -> None:
                logger.info("%s - - [%s] %s" % (self.client_address[0], self.log_date_time_string(), format % args))

        server = HTTPServer((host, port), StandaloneHandler)
        logger.info(f"ScamShield API server listening on http://{host}:{port}")
        server.serve_forever()


if __name__ == "__main__":
    host = settings.HOST if settings.HOST != "0.0.0.0" else "127.0.0.1"
    port = settings.PORT
    run_standalone_server(host=host, port=port)

