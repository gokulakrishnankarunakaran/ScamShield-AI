"""Unit tests for the deterministic reputation lookup service."""

import unittest
from backend.app.services.reputation_service import ReputationService, get_reputation_service
from backend.app.database.mock_data import reset_mock_data


class TestReputationService(unittest.TestCase):
    """Test suite for VPA reputation verification."""

    def setUp(self):
        reset_mock_data()
        self.service = ReputationService()

    def test_verified_merchant_lookup(self):
        """Lookup of legitimate demo merchant must return verified status with LOW risk."""
        result = self.service.lookup_vpa("srikrishna.demo@okaxis")
        self.assertEqual(result["status"], "verified")
        self.assertEqual(result["risk_level"], "LOW")
        self.assertTrue(result["is_known"])
        self.assertIsNotNone(result["merchant"])
        self.assertEqual(result["merchant"]["merchant_name"], "Sri Krishna Stores")

    def test_reported_scam_lookup(self):
        """Lookup of known scam VPA must return reported_scam status with CRITICAL risk."""
        result = self.service.lookup_vpa("instantcashback.win@fakeupi")
        self.assertEqual(result["status"], "reported_scam")
        self.assertEqual(result["risk_level"], "CRITICAL")
        self.assertTrue(result["is_known"])
        self.assertGreater(result["merchant"]["reported_count"], 0)

    def test_unknown_vpa_lookup(self):
        """Lookup of unregistered VPA must return unknown status with MEDIUM risk."""
        result = self.service.lookup_vpa("unregistered.merchant.xyz@oksbi")
        self.assertEqual(result["status"], "unknown")
        self.assertEqual(result["risk_level"], "MEDIUM")
        self.assertFalse(result["is_known"])
        self.assertIsNone(result["merchant"])

    def test_case_insensitive_lookup(self):
        """VPA lookup must be case-insensitive."""
        result = self.service.lookup_vpa("SRIKRISHNA.DEMO@OKAXIS")
        self.assertEqual(result["status"], "verified")
        self.assertEqual(result["vpa"], "srikrishna.demo@okaxis")

    def test_malformed_vpa_handling(self):
        """Malformed VPA string must return unknown status without raising exceptions."""
        result = self.service.lookup_vpa("invalid-vpa-format")
        self.assertEqual(result["status"], "unknown")
        self.assertFalse(result["is_known"])


if __name__ == "__main__":
    unittest.main()

