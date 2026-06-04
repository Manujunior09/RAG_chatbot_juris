import time
from typing import List

from fastapi import APIRouter, HTTPException

from app.schemas.models import AskRequest, AskResponse, SessionResponse, SessionInfo, SourceItem
from app.retrieval.retriever import retrieve
from app.inference.prompt_builder import build_prompt
from app.inference.llm import call_llm
from app.session import session_manager

router = APIRouter()


@router.post("/session", response_model=SessionResponse)
def new_session():
    return {"session_id": session_manager.create_session()}


@router.post("/ask", response_model=AskResponse)
def ask(body: AskRequest):
    session_manager.cleanup_inactive()
    history = session_manager.get_or_create(body.session_id)

    t0 = time.time()
    chunks = retrieve(body.question)
    t1 = time.time()

    if not chunks:
        answer = "Je ne trouve pas d'information pertinente dans les documents disponibles pour répondre à cette question."
    else:
        prompt = build_prompt(body.question, chunks, history)
        answer = call_llm(prompt)
    t2 = time.time()

    session_manager.update(body.session_id, body.question, answer)

    sources = [
        SourceItem(
            document=c["source"],
            chunk_index=c["chunk_index"],
            score=c["score"],
            extrait=c["contenu"][:150],
        )
        for c in chunks
    ]

    return AskResponse(
        reponse=answer,
        sources=sources,
        temps_retrieval_ms=int((t1 - t0) * 1000),
        temps_llm_ms=int((t2 - t1) * 1000),
        temps_total_ms=int((t2 - t0) * 1000),
        session_id=body.session_id,
        nb_chunks_trouves=len(chunks),
        question=body.question,
    )


@router.delete("/session/{session_id}")
def clear_session(session_id: str):
    if not session_manager.clear(session_id):
        raise HTTPException(status_code=404, detail="Session introuvable")
    return {"detail": "Session supprimée"}


@router.get("/sessions", response_model=List[SessionInfo])
def list_sessions():
    return session_manager.list_sessions()
