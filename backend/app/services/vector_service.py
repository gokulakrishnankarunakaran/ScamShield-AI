"""Semantic Vector Search Service for ScamShield AI.

Purpose:
Performs fuzzy, phonetic, and semantic merchant-name matching against registered
and reported merchant profiles (e.g. matching "Sri Krishnaa Store" against "Sri Krishna Stores").
Integrates with Actian VectorAI when online, with an in-memory cosine fallback.
"""

import math
import logging
from typing import Any, Dict, List, Optional, Tuple
from ..database.mock_data import get_all_merchants, normalize_merchant_name
from ..database.actian import get_actian_client, ActianVectorClient

logger = logging.getLogger(__name__)


def _generate_ngram_vector(text: str, n_range: Tuple[int, int] = (2, 4)) -> Dict[str, float]:
    """Generate subword character n-gram TF vector for robust typo and phonetic matching."""
    norm = normalize_merchant_name(text)
    if not norm:
        return {}
    
    padded = f"^{norm}$"
    ngrams: Dict[str, float] = {}
    
    for n in range(n_range[0], n_range[1] + 1):
        for i in range(len(padded) - n + 1):
            gram = padded[i:i + n]
            ngrams[gram] = ngrams.get(gram, 0.0) + 1.0
            
    # Normalize vector to unit length
    magnitude = math.sqrt(sum(v * v for v in ngrams.values()))
    if magnitude > 0:
        for k in ngrams:
            ngrams[k] /= magnitude
            
    return ngrams


def _cosine_similarity_sparse(v1: Dict[str, float], v2: Dict[str, float]) -> float:
    """Calculate cosine similarity between two sparse unit vectors."""
    if not v1 or not v2:
        return 0.0
    common_keys = set(v1.keys()).intersection(set(v2.keys()))
    return sum(v1[k] * v2[k] for k in common_keys)


class VectorService:
    """Service for indexing and searching merchant name embeddings."""

    def __init__(self, actian_client: Optional[ActianVectorClient] = None) -> None:
        self.actian_client = actian_client or get_actian_client()
        self._ml_model = None
        self._ml_available: bool = False
        self._in_memory_index: Dict[str, Dict[str, Any]] = {}
        
        self._initialize_ml_engine()
        self._bootstrap_index()

    def _initialize_ml_engine(self) -> None:
        """Attempt to load sentence-transformers if installed."""
        try:
            from sentence_transformers import SentenceTransformer  # type: ignore
            self._ml_model = SentenceTransformer("all-MiniLM-L6-v2")
            self._ml_available = True
            logger.info("SentenceTransformer (all-MiniLM-L6-v2) successfully loaded.")
        except Exception as e:
            self._ml_model = None
            self._ml_available = False
            logger.info(f"ML embedding engine (sentence-transformers) not loaded: {e}. Using n-gram vectorizer.")

    def _bootstrap_index(self) -> None:
        """Index all default mock merchants into the vector index."""
        merchants = get_all_merchants()
        for merchant in merchants:
            self.add_merchant_embedding(
                merchant_id=merchant["id"],
                name=merchant["merchant_name"],
                metadata=merchant,
            )

    @property
    def is_ml_active(self) -> bool:
        """Return True if dense ML neural embedding model is loaded."""
        return self._ml_available

    def calculate_similarity(self, name1: str, name2: str) -> float:
        """Calculate semantic/phonetic similarity between two merchant names (0.0 to 1.0)."""
        if not name1 or not name2:
            return 0.0
            
        norm1 = normalize_merchant_name(name1)
        norm2 = normalize_merchant_name(name2)
        
        if norm1 == norm2:
            return 1.0

        if self._ml_available and self._ml_model:
            try:
                embeddings = self._ml_model.encode([norm1, norm2])
                import numpy as np
                dot = np.dot(embeddings[0], embeddings[1])
                norm_a = np.linalg.norm(embeddings[0])
                norm_b = np.linalg.norm(embeddings[1])
                return float(dot / (norm_a * norm_b))
            except Exception as e:
                logger.warning(f"Dense vector calculation failed: {e}, using n-gram fallback.")

        # Robust character n-gram cosine fallback
        v1 = _generate_ngram_vector(norm1)
        v2 = _generate_ngram_vector(norm2)
        return float(_cosine_similarity_sparse(v1, v2))

    def add_merchant_embedding(
        self,
        merchant_id: str,
        name: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Generate and store embedding for a merchant entity."""
        norm_name = normalize_merchant_name(name)
        sparse_vec = _generate_ngram_vector(norm_name)
        
        self._in_memory_index[merchant_id] = {
            "merchant_id": merchant_id,
            "merchant_name": name,
            "normalized_name": norm_name,
            "sparse_vector": sparse_vec,
            "metadata": metadata or {},
        }

        # If Actian Vector is available, also persist to Actian Vector database
        if self.actian_client.is_available():
            dense_vec: List[float] = []
            if self._ml_available and self._ml_model:
                try:
                    dense_vec = self._ml_model.encode(norm_name).tolist()
                except Exception:
                    pass
            self.actian_client.insert_vector(merchant_id, dense_vec, metadata)

        return True

    def search_similar_merchant(
        self,
        query_name: str,
        top_k: int = 3,
        min_similarity: float = 0.4,
    ) -> List[Dict[str, Any]]:
        """Search for merchants matching the given query name by similarity score.

        Returns sorted list of matches with similarity scores and confidence tiers.
        """
        if not query_name or not query_name.strip():
            return []

        clean_query = normalize_merchant_name(query_name)
        query_vec = _generate_ngram_vector(clean_query)
        
        candidates: List[Tuple[float, Dict[str, Any]]] = []

        for m_id, item in self._in_memory_index.items():
            sim = _cosine_similarity_sparse(query_vec, item["sparse_vector"])
            
            # Exact match boost
            if clean_query == item["normalized_name"]:
                sim = 1.0
                
            if sim >= min_similarity:
                candidates.append((sim, item))

        # Sort descending by similarity score
        candidates.sort(key=lambda x: x[0], reverse=True)
        top_candidates = candidates[:top_k]

        results: List[Dict[str, Any]] = []
        for score, item in top_candidates:
            meta = item.get("metadata", {})
            
            confidence = "HIGH" if score >= 0.85 else ("MEDIUM" if score >= 0.65 else "LOW")
            match_type = "EXACT" if score >= 0.99 else ("FUZZY_PHONETIC" if score >= 0.70 else "PARTIAL")

            results.append({
                "merchant_id": item["merchant_id"],
                "merchant_name": item["merchant_name"],
                "normalized_name": item["normalized_name"],
                "vpa": meta.get("vpa", "unknown"),
                "status": meta.get("status", "unknown"),
                "similarity_score": round(score, 4),
                "confidence_tier": confidence,
                "match_type": match_type,
                "category": meta.get("category"),
                "risk_level": meta.get("risk_level"),
            })

        return results


_vector_service_instance: Optional[VectorService] = None


def get_vector_service() -> VectorService:
    """Return singleton VectorService instance."""
    global _vector_service_instance
    if _vector_service_instance is None:
        _vector_service_instance = VectorService()
    return _vector_service_instance

