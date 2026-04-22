from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"


class MemoryIngestRequest(BaseModel):
    text: str = Field(min_length=3)


class ScoreBreakdown(BaseModel):
    importance: float
    recency: float
    frequency: float
    final_score: float


class MemoryOut(BaseModel):
    id: int
    raw_text: str
    stored_text: str | None
    summary: str | None
    keywords: list[str]
    entities: list[str]
    score: float
    decision: str
    access_count: int
    created_at: datetime

    class Config:
        from_attributes = True


class MemoryIngestResponse(BaseModel):
    decision: str
    reason: str
    score_breakdown: ScoreBreakdown
    memory: MemoryOut | None


class AskRequest(BaseModel):
    query: str
    top_k: int = 5


class AskResponse(BaseModel):
    answer: str
    confidence: float
    source_memories: list[MemoryOut]


class DashboardStats(BaseModel):
    total_memories: int
    high_value_memories: int
    avg_score: float
    reminders: list[str]


class TimelineItem(BaseModel):
    id: int
    event_type: str
    description: str
    created_at: datetime


class LinkOut(BaseModel):
    source_memory_id: int
    target_memory_id: int
    relation_type: str
    link_score: float


class DecisionHistoryOut(BaseModel):
    id: int
    memory_id: int | None
    score: float
    decision: str
    reason_json: str
    created_at: datetime

    class Config:
        from_attributes = True
