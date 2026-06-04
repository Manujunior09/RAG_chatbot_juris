import hashlib
import os
from datetime import datetime
from typing import Dict, Any

from sentence_transformers import SentenceTransformer

from app.core.config import settings
from app.core.chromadb_client import get_collection
from app.ingestion.text_extractor import extract_text
from app.ingestion.chunker import chunk


def ingest(file_path: str, strategy: str = "semantic") -> None:
    collection = get_collection()
    model = SentenceTransformer(settings.embedding_model)
    filename = os.path.basename(file_path)
    print(f"Traitement de {filename}...")

    existing = collection.get(where={"source": filename})
    if existing["ids"]:
        collection.delete(ids=existing["ids"])
        print(f"  → {len(existing['ids'])} anciens chunks supprimés")

    raw_text = extract_text(file_path)
    chunks = chunk(raw_text, strategy)
    if not chunks:
        print("  Aucun chunk valide généré.")
        return

    embeddings = model.encode(chunks).tolist()
    now = datetime.now().isoformat()
    total = len(chunks)
    ids, metadatas = [], []

    for idx, c in enumerate(chunks):
        ids.append(f"{hashlib.md5(c.encode()).hexdigest()}_{idx}")
        metadatas.append({
            "source": filename,
            "format": os.path.splitext(filename)[1][1:],
            "chunk_index": idx,
            "total_chunks": total,
            "date_ingestion": now,
            "taille_chars": len(c),
        })

    collection.add(ids=ids, embeddings=embeddings, documents=chunks, metadatas=metadatas)
    print(f"  → {len(chunks)} nouveaux chunks indexés")


def get_stats() -> Dict[str, Any]:
    collection = get_collection()
    total = collection.count()
    if total == 0:
        return {"total_chunks": 0, "documents": {}, "taille_moyenne_chunk": 0, "date_derniere_ingestion": None}

    all_meta = collection.get()["metadatas"]
    doc_stats: Dict[str, int] = {}
    total_chars = 0
    last_ingestion = None

    for meta in all_meta:
        src = meta["source"]
        doc_stats[src] = doc_stats.get(src, 0) + 1
        total_chars += meta["taille_chars"]
        if not last_ingestion or meta["date_ingestion"] > last_ingestion:
            last_ingestion = meta["date_ingestion"]

    return {
        "total_chunks": total,
        "documents": doc_stats,
        "taille_moyenne_chunk": total_chars / total,
        "date_derniere_ingestion": last_ingestion,
    }
