import json

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.core.database import get_db
from app.models import User
from app.schemas import AskRequest, AskResponse, MemoryOut
from app.services.memory_service import memory_service

router = APIRouter(prefix="/ask", tags=["ask-ai"])


@router.post("", response_model=AskResponse)
def ask_ai(
    payload: AskRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = memory_service.retrieve_answer(db, current_user.id, payload.query, payload.top_k)
    sources = [
        MemoryOut(
            id=memory.id,
            raw_text=memory.raw_text,
            stored_text=memory.stored_text,
            summary=memory.summary,
            keywords=json.loads(memory.keywords),
            entities=json.loads(memory.entities),
            score=memory.score,
            decision=memory.decision,
            access_count=memory.access_count,
            created_at=memory.created_at,
        )
        for memory in result["source_memories"]
    ]
    return AskResponse(answer=result["answer"], confidence=result["confidence"], source_memories=sources)
