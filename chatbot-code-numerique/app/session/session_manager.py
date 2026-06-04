import uuid
from datetime import datetime, timedelta
from typing import Dict, List

from app.core.config import settings

_sessions: Dict[str, List[Dict]] = {}
_last_activity: Dict[str, datetime] = {}
_timeout = timedelta(minutes=settings.session_timeout_minutes)


def create_session() -> str:
    sid = str(uuid.uuid4())
    _sessions[sid] = []
    _last_activity[sid] = datetime.now()
    return sid


def get_or_create(session_id: str) -> List[Dict]:
    if session_id not in _sessions:
        _sessions[session_id] = []
        _last_activity[session_id] = datetime.now()
    return _sessions[session_id]


def update(session_id: str, question: str, answer: str) -> None:
    _sessions[session_id].append({"role": "user", "content": question})
    _sessions[session_id].append({"role": "assistant", "content": answer})
    _last_activity[session_id] = datetime.now()


def clear(session_id: str) -> bool:
    if session_id in _sessions:
        del _sessions[session_id]
        del _last_activity[session_id]
        return True
    return False


def list_sessions() -> List[Dict]:
    now = datetime.now()
    return [
        {
            "session_id": sid,
            "age_minutes": int((now - _last_activity[sid]).total_seconds() / 60),
            "nb_messages": len(hist),
        }
        for sid, hist in _sessions.items()
    ]


def cleanup_inactive() -> None:
    now = datetime.now()
    to_delete = [sid for sid, last in _last_activity.items() if now - last > _timeout]
    for sid in to_delete:
        del _sessions[sid]
        del _last_activity[sid]
