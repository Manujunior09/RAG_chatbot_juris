import ollama
from app.core.config import settings

_client = None

def get_ollama_client() -> ollama.Client:
    global _client
    if _client is None:
        _client = ollama.Client(host=settings.ollama_host)
    return _client
