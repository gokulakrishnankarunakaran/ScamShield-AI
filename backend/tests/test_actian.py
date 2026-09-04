"""Unit tests for Actian Vector database client abstraction."""

import unittest
from backend.app.database.actian import ActianVectorClient


class TestActianVectorClient(unittest.TestCase):
    """Test suite for Actian Vector connectivity abstraction and fallback."""

    def test_actian_client_graceful_status(self):
        """Actian client must gracefully report status without crashing when offline."""
        client = ActianVectorClient()
        status = client.get_status()
        self.assertIn("available", status)
        self.assertIn("status", status)
        self.assertIn(status["status"], ["connected", "unavailable"])
        self.assertIsInstance(status["available"], bool)

    def test_search_vectors_fallback(self):
        """Offline Actian client must safely return empty list without crashing."""
        client = ActianVectorClient()
        # Force offline state for deterministic unit test
        client._is_connected = False
        results = client.search_vectors([0.1, 0.2, 0.3], top_k=5)
        self.assertEqual(results, [])

    def test_insert_vector_fallback(self):
        """Offline Actian client must return False on vector insert without raising exceptions."""
        client = ActianVectorClient()
        client._is_connected = False
        success = client.insert_vector("merch_test", [0.1, 0.2, 0.3])
        self.assertFalse(success)


if __name__ == "__main__":
    unittest.main()

