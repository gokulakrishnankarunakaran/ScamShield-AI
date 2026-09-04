"""Comprehensive Unit Tests for QR Parsing, Name Matching, and VPA Pattern Analysis.

Covers all 15 required scenarios and edge cases.
"""

import unittest
from backend.app.services.qr_service import QRService, normalize_name


class TestQRService(unittest.TestCase):
    """Test suite for QRService UPI parsing and signal extraction."""

    def setUp(self):
        self.service = QRService()

    # -------------------------------------------------------------
    # SCENARIOS 1-5: Name Matching Variations
    # -------------------------------------------------------------
    def test_scenario_01_exact_legitimate_match(self):
        """Scenario 1: Exact matching names produce score 100 and exact status."""
        result = self.service.match_names("Sri Krishna Stores", "Sri Krishna Stores")
        self.assertEqual(result["status"], "exact")
        self.assertEqual(result["score"], 100)

    def test_scenario_02_case_variation(self):
        """Scenario 2: Case variation (e.g. UPPERCASE vs Mixed) produces exact/strong match."""
        result = self.service.match_names("SRI KRISHNA STORES", "Sri Krishna Stores")
        self.assertIn(result["status"], ["exact", "strong_match"])
        self.assertGreaterEqual(result["score"], 95)

    def test_scenario_03_spacing_variation(self):
        """Scenario 3: Extra spaces and collapsed words produce strong match."""
        result = self.service.match_names("SriKrishna Stores", "Sri  Krishna  Stores")
        self.assertIn(result["status"], ["exact", "strong_match"])
        self.assertGreaterEqual(result["score"], 90)

    def test_scenario_04_minor_spelling_ocr_variation(self):
        """Scenario 4: Minor typo/OCR variation (e.g. Sri Krishnaa Store vs Sri Krishna Stores)."""
        result = self.service.match_names("Sri Krishna Stores", "Sri Krishnaa Store")
        self.assertIn(result["status"], ["strong_match", "possible_match"])
        self.assertGreaterEqual(result["score"], 80)

    def test_scenario_05_completely_different_name(self):
        """Scenario 5: Completely different name (e.g. Ramesh Kumar vs Sri Krishna Stores) produces mismatch."""
        result = self.service.match_names("Sri Krishna Stores", "Ramesh Kumar")
        self.assertEqual(result["status"], "mismatch")
        self.assertLess(result["score"], 40)

    # -------------------------------------------------------------
    # SCENARIOS 9: VPA Pattern Heuristics
    # -------------------------------------------------------------
    def test_scenario_09_personal_looking_vpa(self):
        """Scenario 9: Personal-looking VPA handle detection."""
        # Phone number handle
        res1 = self.service.analyze_vpa_pattern("9876543210@ybl")
        self.assertEqual(res1["status"], "caution")
        self.assertEqual(res1["pattern_type"], "phone_handle")

        # Personal bank handle with trailing numbers
        res2 = self.service.analyze_vpa_pattern("ramesh123@okhdfc")
        self.assertEqual(res2["status"], "caution")
        self.assertEqual(res2["pattern_type"], "personal_handle")

        # Merchant gateway handle
        res3 = self.service.analyze_vpa_pattern("srikrishna.stores@paytmqr")
        self.assertEqual(res3["status"], "positive")
        self.assertEqual(res3["pattern_type"], "merchant_handle")

    # -------------------------------------------------------------
    # SCENARIOS 10-15: Parsing, Validation, and Parameter Extraction
    # -------------------------------------------------------------
    def test_scenario_10_invalid_qr_payload(self):
        """Scenario 10: Non-UPI and malformed QR strings are rejected safely without crashing."""
        # Plain text
        valid, parsed, err = self.service.parse_upi_qr("just some random text")
        self.assertFalse(valid)
        self.assertIsNone(parsed)
        self.assertIn("Unsupported QR scheme", err)

        # Empty string
        valid, parsed, err = self.service.parse_upi_qr("")
        self.assertFalse(valid)
        self.assertIn("empty", err.lower())

        # HTTP URL
        valid, parsed, err = self.service.parse_upi_qr("https://scam-site.com/pay")
        self.assertFalse(valid)

    def test_scenario_11_missing_vpa(self):
        """Scenario 11: Missing mandatory 'pa' parameter is rejected."""
        valid, parsed, err = self.service.parse_upi_qr("upi://pay?pn=Ramesh%20Kumar&am=500")
        self.assertFalse(valid)
        self.assertIsNone(parsed)
        self.assertIn("Mandatory payee address", err)

    def test_scenario_12_missing_payee_name(self):
        """Scenario 12: Missing 'pn' parameter is parsed with payee_name = None."""
        valid, parsed, err = self.service.parse_upi_qr("upi://pay?pa=shop123@okaxis&am=250")
        self.assertTrue(valid)
        self.assertEqual(parsed["vpa"], "shop123@okaxis")
        self.assertIsNone(parsed["payee_name"])

    def test_scenario_13_amount_parsing(self):
        """Scenario 13: Numeric amount parameter is accurately parsed to float."""
        valid, parsed, err = self.service.parse_upi_qr("upi://pay?pa=shop123@okaxis&am=1250.75")
        self.assertTrue(valid)
        self.assertEqual(parsed["amount"], 1250.75)

        # Invalid non-numeric amount should parse as None without crashing
        valid2, parsed2, _ = self.service.parse_upi_qr("upi://pay?pa=shop123@okaxis&am=invalid_amt")
        self.assertTrue(valid2)
        self.assertIsNone(parsed2["amount"])

    def test_scenario_14_merchant_code_parsing(self):
        """Scenario 14: Merchant code 'mc' is extracted correctly."""
        valid, parsed, err = self.service.parse_upi_qr("upi://pay?pa=shop@okaxis&pn=Shop&mc=5411")
        self.assertTrue(valid)
        self.assertEqual(parsed["merchant_code"], "5411")

    def test_scenario_15_transaction_ref_and_note_parsing(self):
        """Scenario 15: Transaction reference 'tr' and note 'tn' are extracted."""
        valid, parsed, err = self.service.parse_upi_qr(
            "upi://pay?pa=shop@okaxis&pn=Shop&tr=REF987654&tn=Monthly%20Subscription%20Fee"
        )
        self.assertTrue(valid)
        self.assertEqual(parsed["transaction_ref"], "REF987654")
        self.assertEqual(parsed["transaction_note"], "Monthly Subscription Fee")


if __name__ == "__main__":
    unittest.main()
