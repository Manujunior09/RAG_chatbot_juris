from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    db_path: str = "./chroma_db"
    embedding_model: str = "paraphrase-multilingual-MiniLM-L12-v2"
    ollama_host: str = "http://10.46.3.3:11434"
    ollama_model: str = "mistral"
    llm_temperature: float = 0.1
    chunk_size: int = 800
    chunk_overlap: int = 150
    min_score: float = 0.60
    session_timeout_minutes: int = 30

    model_config = {"env_file": ".env", "extra": "ignore"}

settings = Settings()
