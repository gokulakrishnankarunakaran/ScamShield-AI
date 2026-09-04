"""Comprehensive Unit Tests for Risk Engine and End-to-End Verification Pipeline."""

import unittest
from backend.app.services.risk_engine import RiskEngine, get_risk_engine
from backend.app.services.qr_service import get_qr_service
from backend.app.services.gemini_service import get_gemini_service
from backend.app.database.mock_data import reset_mock_data


class TestRiskEngine(unittest.TestCase):
    """Test suite for the deterministic multi-layer Risk Engine."""

    def setUp(self):
        reset_mock_data()
        self.risk_engine = RiskEngine()
        self.qr_service = get_qr_service()
        self.gemini_service = get_gemini_service()

    def test_scenario_06_verified_vpa_legitimate_payment(self):
        """Scenario 6: Verified VPA with matching name produces GREEN verdict."""
        # Verified merchant: Sri Krishna Stores (srikrishna.demo@okaxis)
        raw_qr = "upi://pay?pa=srikrishna.demo@okaxis&pn=Sri%20Krishna%20Stores&am=350"
        _, parsed, _ = self.qr_service.parse_upi_qr(raw_qr)
        
        result = self.risk_engine.evaluate_qr_payment(parsed, expected_name="Sri Krishna Stores")

        self.assertEqual(result["verdict"], "GREEN")
        self.assertLess(result["risk_score"], 20)
        self.assertEqual(result["confidence"], "high")
        self.assertEqual(result["checks"]["vpa_reputation"]["status"], "verified")
        self.assertIn("Verified Merchant", " ".join(result["reasons"]))

    def test_scenario_07_reported_scam_vpa_hard_red(self):
        """Scenario 7: Reported scam VPA produces HARD RED verdict regardless of payee name."""
        # Known scam: instantcashback.win@fakeupi
        raw_qr = "upi://pay?pa=instantcashback.win@fakeupi&pn=QuickReward%20Cashback&am=1000"
        _, parsed, _ = self.qr_service.parse_upi_qr(raw_qr)

        result = self.risk_engine.evaluate_qr_payment(parsed, expected_name="QuickReward Cashback")

        self.assertEqual(result["verdict"], "RED")
        self.assertGreaterEqual(result["risk_score"], 90)
        self.assertEqual(result["confidence"], "high")
        self.assertEqual(result["checks"]["vpa_reputation"]["status"], "reported_scam")
        self.assertIn("CRITICAL FRAUD ALERT", " ".join(result["reasons"]))

    def test_scenario_08_unknown_vpa_neutral_handling(self):
        """Scenario 8: Unknown VPA with no explicit name is handled neutrally (YELLOW), never called fraud."""
        raw_qr = "upi://pay?pa=randomcorner.shop@oksbi&pn=Corner%20Shop&am=150"
        _, parsed, _ = self.qr_service.parse_upi_qr(raw_qr)

        result = self.risk_engine.evaluate_qr_payment(parsed, expected_name=None)

        self.assertEqual(result["verdict"], "YELLOW")
        self.assertGreaterEqual(result["risk_score"], 20)
        self.assertLess(result["risk_score"], 60)
        self.assertEqual(result["checks"]["vpa_reputation"]["status"], "unknown")

    def test_identity_mismatch_produces_red(self):
        """Expected merchant differs completely from QR payee name -> RED verdict."""
        # User entered "Sri Krishna Stores", but QR is for individual "Ramesh Kumar" (ramesh123@okhdfc)
        raw_qr = "upi://pay?pa=ramesh123@okhdfc&pn=Ramesh%20Kumar&am=500"
        _, parsed, _ = self.qr_service.parse_upi_qr(raw_qr)

        result = self.risk_engine.evaluate_qr_payment(parsed, expected_name="Sri Krishna Stores")

        self.assertEqual(result["verdict"], "RED")
        self.assertGreaterEqual(result["risk_score"], 60)
        self.assertEqual(result["checks"]["name_match"]["status"], "mismatch")
        self.assertIn("IDENTITY MISMATCH", " ".join(result["reasons"]))

    def test_semantic_match_resolves_typo(self):
        """Minor typo in payee name is resolved by semantic matcher without false alarms."""
        raw_qr = "upi://pay?pa=srikrishna.demo@okaxis&pn=Sri%20Krishnaa%20Store&am=200"
        _, parsed, _ = self.qr_service.parse_upi_qr(raw_qr)

        result = self.risk_engine.evaluate_qr_payment(parsed, expected_name="Sri Krishna Stores")

        self.assertEqual(result["verdict"], "GREEN")
        self.assertLess(result["risk_score"], 20)

    def test_gemini_explanation_preserves_deterministic_verdict(self):
        """Gemini explanation generator must preserve the exact verdict and risk score."""
        raw_qr = "upi://pay?pa=instantcashback.win@fakeupi&pn=QuickReward&am=500"
        _, parsed, _ = self.qr_service.parse_upi_qr(raw_qr)
        result = self.risk_engine.evaluate_qr_payment(parsed, expected_name="QuickReward")

        explanation = self.gemini_service.generate_explanation(result)
        self.assertIsInstance(explanation, str)
        self.assertIn("CRITICAL WARNING", explanation)
        self.assertEqual(result["verdict"], "RED")


if __name__ == "__main__":
    unittest.main()
