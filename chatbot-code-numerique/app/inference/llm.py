from app.core.config import settings
from app.core.ollama_client import get_ollama_client


def call_llm(prompt: str) -> str:
    client = get_ollama_client()
    response = client.chat(
        model=settings.ollama_model,
        messages=[{"role": "user", "content": prompt}],
        options={"temperature": settings.llm_temperature},
    )
    return response["message"]["content"]
