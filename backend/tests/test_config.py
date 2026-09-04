"""Unit tests for configuration loading and validation."""

import os
import unittest
from backend.app.config import Settings, get_settings


class TestConfigurationLoading(unittest.TestCase):
    """Test suite for settings and environment loading."""

    def test_default_settings_instantiation(self):
        """Verify settings initialize with clean default values."""
        settings = Settings()
        self.assertEqual(settings.ENVIRONMENT, os.getenv("ENVIRONMENT", "development"))
        self.assertIsInstance(settings.PORT, int)
        self.assertIn(settings.LOG_LEVEL.lower(), ["info", "debug", "warning", "error"])
        self.assertIsInstance(settings.CORS_ORIGINS, list)

    def test_singleton_get_settings(self):
        """Verify get_settings returns a consistent singleton."""
        s1 = get_settings()
        s2 = get_settings()
        self.assertIs(s1, s2)

    def test_actian_configuration_detection(self):
        """Verify Actian configuration property correctly reflects state."""
        settings = Settings(ACTIAN_HOST="localhost", ACTIAN_DATABASE="scamshield_vectors", ACTIAN_ENABLED=True)
        self.assertTrue(settings.is_actian_configured)

        disabled_settings = Settings(ACTIAN_ENABLED=False)
        self.assertFalse(disabled_settings.is_actian_configured)


if __name__ == "__main__":
    unittest.main()

