"""Unit tests for semantic vector search and fuzzy merchant matching."""

import unittest
from backend.app.services.vector_service import VectorService, normalize_merchant_name
from backend.app.database.mock_data import reset_mock_data


class TestVectorService(unittest.TestCase):
    """Test suite for semantic and fuzzy merchant matching."""

    def setUp(self):
        reset_mock_data()
        self.service = VectorService()

    def test_name_normalization(self):
        """Verify normalization removes extra whitespace, symbols, and lowercases text."""
        raw = "  Sri Krishna   Stores & Provisions!!  "
        normalized = normalize_merchant_name(raw)
        self.assertEqual(normalized, "sri krishna stores provisions")

    def test_exact_name_similarity(self):
        """Exact matching names must return 1.0 similarity."""
        score = self.service.calculate_similarity("Sri Krishna Stores", "Sri Krishna Stores")
        self.assertEqual(score, 1.0)

    def test_typo_fuzzy_matching(self):
        """Typo variant 'Sri Krishnaa Store' must match 'Sri Krishna Stores' with high similarity."""
        results = self.service.search_similar_merchant("Sri Krishnaa Store", top_k=3, min_similarity=0.6)
        self.assertGreater(len(results), 0)
        top_match = results[0]
        self.assertEqual(top_match["merchant_id"], "merch_001")
        self.assertGreaterEqual(top_match["similarity_score"], 0.70)
        self.assertIn(top_match["confidence_tier"], ["HIGH", "MEDIUM"])

    def test_distinct_merchants_have_low_similarity(self):
        """Unrelated merchant names must have very low similarity score."""
        score = self.service.calculate_similarity("Lakshmi Textiles", "Electricity Bill Urgent Desk")
        self.assertLess(score, 0.3)


if __name__ == "__main__":
    unittest.main()

