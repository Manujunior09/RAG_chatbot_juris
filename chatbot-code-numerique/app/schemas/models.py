from typing import List, Optional
from pydantic import BaseModel


class AskRequest(BaseModel):
    question: str
    session_id: str


class SourceItem(BaseModel):
    document: str
    chunk_index: int
    score: float
    extrait: str


class AskResponse(BaseModel):
    reponse: str
    sources: List[SourceItem]
    temps_retrieval_ms: int
    temps_llm_ms: int
    temps_total_ms: int
    session_id: str
    nb_chunks_trouves: int
    question: str


class SessionResponse(BaseModel):
    session_id: str


class SessionInfo(BaseModel):
    session_id: str
    age_minutes: int
    nb_messages: int
