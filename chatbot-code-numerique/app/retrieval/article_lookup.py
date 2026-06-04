import re
from typing import List, Dict

from app.core.chromadb_client import get_collection


def extract_article_numbers(question: str) -> List[str]:
    return re.findall(r"\b(?:article|art\.?)\s*(\d+)", question, re.IGNORECASE)


def lookup_articles(article_numbers: List[str]) -> List[Dict]:
    collection = get_collection()
    chunks = []
    seen_ids = set()
    all_docs = collection.get(include=["documents", "metadatas"])

    for doc, meta in zip(all_docs["documents"], all_docs["metadatas"]):
        for num in article_numbers:
            pattern = re.compile(rf"\bArticle\s+{re.escape(num)}\b", re.IGNORECASE)
            if pattern.search(doc):
                key = (meta["source"], meta["chunk_index"])
                if key not in seen_ids:
                    seen_ids.add(key)
                    chunks.append({
                        "contenu": doc,
                        "source": meta["source"],
                        "chunk_index": meta["chunk_index"],
                        "score": 1.0,
                    })
    return chunks
