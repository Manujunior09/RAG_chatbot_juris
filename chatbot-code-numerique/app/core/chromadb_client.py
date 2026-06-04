import chromadb
from app.core.config import settings

_client = None
_collection = None

def get_collection():
    global _client, _collection
    if _collection is None:
        _client = chromadb.PersistentClient(path=settings.db_path)
        _collection = _client.get_or_create_collection(
            "documents",
            metadata={"hnsw:space": "cosine"}
        )
    return _collection
