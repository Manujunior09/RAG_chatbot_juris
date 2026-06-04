from typing import List, Dict

from sentence_transformers import SentenceTransformer

from app.core.config import settings
from app.core.chromadb_client import get_collection
from app.retrieval.article_lookup import extract_article_numbers, lookup_articles

_model = None

def _get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer(settings.embedding_model)
    return _model


def retrieve(question: str, n_results: int = 6, min_score: float = None) -> List[Dict]:
    if min_score is None:
        min_score = settings.min_score

    # 1. Lookup direct par numéro d'article
    article_numbers = extract_article_numbers(question)
    direct_chunks = lookup_articles(article_numbers) if article_numbers else []
    direct_keys = {(c["source"], c["chunk_index"]) for c in direct_chunks}

    # 2. Recherche sémantique
    collection = get_collection()
    q_embed = _get_model().encode([question]).tolist()
    results = collection.query(
        query_embeddings=q_embed,
        n_results=n_results,
        include=["documents", "metadatas", "distances"],
    )

    semantic_chunks = []
    if results["documents"] and results["documents"][0]:
        for doc, meta, dist in zip(
            results["documents"][0], results["metadatas"][0], results["distances"][0]
        ):
            score = 1 - dist
            key = (meta["source"], meta["chunk_index"])
            if score >= min_score and key not in direct_keys:
                semantic_chunks.append({
                    "contenu": doc,
                    "source": meta["source"],
                    "chunk_index": meta["chunk_index"],
                    "score": score,
                })

    return direct_chunks + semantic_chunks
