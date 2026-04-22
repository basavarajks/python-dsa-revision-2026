import json

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.core.database import get_db
from app.models import DecisionHistory, Memory, MemoryLink, User
from app.schemas import DecisionHistoryOut, LinkOut, MemoryIngestRequest, MemoryIngestResponse, MemoryOut
from app.services.memory_service import memory_service

router = APIRouter(prefix="/memories", tags=["memories"])


def _to_memory_out(memory: Memory) -> MemoryOut:
    return MemoryOut(
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


@router.post("/ingest", response_model=MemoryIngestResponse)
def ingest_memory(
    payload: MemoryIngestRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = memory_service.ingest_memory(db, current_user.id, payload.text)
    memory = result["memory"]
    return MemoryIngestResponse(
        decision=result["decision"],
        reason=result["reason"],
        score_breakdown=result["score_breakdown"],
        memory=_to_memory_out(memory) if memory else None,
    )


@router.get("", response_model=list[MemoryOut])
def list_memories(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    memories = db.scalars(
        select(Memory)
        .where(Memory.user_id == current_user.id, Memory.is_deleted.is_(False))
        .order_by(Memory.score.desc())
    ).all()
    return [_to_memory_out(memory) for memory in memories]


@router.get("/decisions", response_model=list[DecisionHistoryOut])
def decision_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    history = db.scalars(
        select(DecisionHistory)
        .where(DecisionHistory.user_id == current_user.id)
        .order_by(DecisionHistory.created_at.desc())
        .limit(50)
    ).all()
    return history


@router.post("/decay")
def run_decay(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    removed = memory_service.apply_decay(db, current_user.id)
    return {"removed": removed, "message": "Decay engine executed"}


@router.get("/{memory_id}/links", response_model=list[LinkOut])
def get_links(
    memory_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    links = db.scalars(
        select(MemoryLink).where(
            MemoryLink.user_id == current_user.id,
            (MemoryLink.source_memory_id == memory_id) | (MemoryLink.target_memory_id == memory_id),
        )
    ).all()
    return links


@router.get("/reminders/list")
def get_reminders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return {"reminders": memory_service.reminders(db, current_user.id)}
