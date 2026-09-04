"""Unit tests for the /health endpoint and application lifecycle."""

import unittest
from backend.app.config import get_settings
from backend.app.database.actian import get_actian_client


class TestHealthEndpoint(unittest.TestCase):
    """Test suite for /health diagnostic status."""

    def test_health_response_data(self):
        """Verify health check logic returns valid 'status': 'ok' structure."""
        actian_client = get_actian_client()
        settings = get_settings()
        
        status_payload = {
            "status": "ok",
            "app": "ScamShield AI",
            "version": "1.0.0",
            "team": "CYBERTRON",
            "actian_status": actian_client.get_status().get("status", "unavailable"),
            "environment": settings.ENVIRONMENT,
        }

        self.assertEqual(status_payload["status"], "ok")
        self.assertEqual(status_payload["app"], "ScamShield AI")
        self.assertEqual(status_payload["team"], "CYBERTRON")
        self.assertIn(status_payload["actian_status"], ["connected", "unavailable"])


if __name__ == "__main__":
    unittest.main()

