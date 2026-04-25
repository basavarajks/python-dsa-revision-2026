from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.core.database import get_db
from app.models import DecisionHistory, QueryLog, User
from app.schemas import DashboardStats, TimelineItem
from app.services.memory_service import memory_service

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/stats", response_model=DashboardStats)
def stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    memory_service.apply_decay(db, current_user.id)
    data = memory_service.stats(db, current_user.id)
    return DashboardStats(**data)


@router.get("/timeline", response_model=list[TimelineItem])
def timeline(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    decisions = db.scalars(
        select(DecisionHistory)
        .where(DecisionHistory.user_id == current_user.id)
        .order_by(DecisionHistory.created_at.desc())
        .limit(25)
    ).all()
    queries = db.scalars(
        select(QueryLog)
        .where(QueryLog.user_id == current_user.id)
        .order_by(QueryLog.created_at.desc())
        .limit(25)
    ).all()

    events: list[TimelineItem] = []
    for decision in decisions:
        events.append(
            TimelineItem(
                id=decision.id,
                event_type="decision",
                description=f"Decision={decision.decision} score={decision.score}",
                created_at=decision.created_at,
            )
        )
    for query in queries:
        events.append(
            TimelineItem(
                id=query.id,
                event_type="query",
                description=f"Asked: {query.query[:80]}",
                created_at=query.created_at,
            )
        )
    events.sort(key=lambda item: item.created_at, reverse=True)
    return events[:30]
