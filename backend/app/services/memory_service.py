import json
from datetime import datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models import DecisionHistory, Memory, MemoryLink, QueryLog
from app.services.nlp import extract_entities, extract_keywords, preprocess_text, summarize_text
from app.services.vector_store import vector_store


class MemoryService:
    @staticmethod
    def _importance_score(keywords: list[str]) -> float:
        if not keywords:
            return 0.1
        matches = [word for word in keywords if word in settings.important_keywords]
        return min(1.0, 0.2 + (len(matches) * 0.2))

    @staticmethod
    def _frequency_score(db: Session, user_id: int, keywords: list[str]) -> float:
        if not keywords:
            return 0.0
        memories = db.scalars(
            select(Memory).where(Memory.user_id == user_id, Memory.is_deleted.is_(False))
        ).all()
        overlap = 0
        for memory in memories:
            old_keys = set(json.loads(memory.keywords))
            overlap += len(old_keys.intersection(set(keywords)))
        return min(1.0, overlap / max(1, len(keywords) * 5))

    @staticmethod
    def _decision(score: float) -> str:
        if score >= settings.high_score_threshold:
            return "store_full"
        if score >= settings.medium_score_threshold:
            return "store_summary"
        return "discard"

    @classmethod
    def ingest_memory(cls, db: Session, user_id: int, text: str) -> dict:
        clean = preprocess_text(text)
        keywords = extract_keywords(clean)
        entities = extract_entities(clean)

        importance = cls._importance_score(keywords)
        recency = 1.0
        frequency = cls._frequency_score(db, user_id, keywords)
        score = round((importance * 0.5) + (recency * 0.2) + (frequency * 0.3), 3)

        decision = cls._decision(score)
        reason = {
            "importance": importance,
            "recency": recency,
            "frequency": frequency,
            "keywords": keywords,
            "entities": entities,
        }

        memory = None
        if decision != "discard":
            memory = Memory(
                user_id=user_id,
                raw_text=clean,
                stored_text=clean if decision == "store_full" else summarize_text(clean),
                summary=summarize_text(clean),
                keywords=json.dumps(keywords),
                entities=json.dumps(entities),
                score=score,
                importance_score=importance,
                recency_score=recency,
                frequency_score=frequency,
                decision=decision,
                last_accessed=datetime.utcnow(),
            )
            db.add(memory)
            db.commit()
            db.refresh(memory)
            vector_store.add_memory(user_id, memory.id, memory.stored_text or clean)
            cls._link_memory(db, user_id, memory)

        db.add(
            DecisionHistory(
                user_id=user_id,
                memory_id=memory.id if memory else None,
                score=score,
                decision=decision,
                reason_json=json.dumps(reason),
            )
        )
        db.commit()

        return {
            "decision": decision,
            "reason": "High score kept fully" if decision == "store_full" else "Medium score summarized" if decision == "store_summary" else "Low score discarded",
            "score_breakdown": {
                "importance": importance,
                "recency": recency,
                "frequency": frequency,
                "final_score": score,
            },
            "memory": memory,
        }

    @staticmethod
    def _link_memory(db: Session, user_id: int, current: Memory) -> None:
        current_keys = set(json.loads(current.keywords))
        if not current_keys:
            return
        others = db.scalars(
            select(Memory).where(
                Memory.user_id == user_id,
                Memory.id != current.id,
                Memory.is_deleted.is_(False),
            )
        ).all()

        for other in others:
            other_keys = set(json.loads(other.keywords))
            union = current_keys.union(other_keys)
            if not union:
                continue
            overlap = current_keys.intersection(other_keys)
            link_score = len(overlap) / len(union)
            if link_score >= 0.2:
                db.add(
                    MemoryLink(
                        user_id=user_id,
                        source_memory_id=current.id,
                        target_memory_id=other.id,
                        relation_type="keyword_overlap",
                        link_score=round(link_score, 3),
                    )
                )
        db.commit()

    @staticmethod
    def apply_decay(db: Session, user_id: int) -> int:
        memories = db.scalars(
            select(Memory).where(Memory.user_id == user_id, Memory.is_deleted.is_(False))
        ).all()

        removed = 0
        now = datetime.utcnow()
        for memory in memories:
            days_old = max(0, (now - memory.last_accessed).days)
            memory.recency_score = max(0.0, 1 - (days_old * settings.decay_per_day))
            memory.score = round(
                (memory.importance_score * 0.5)
                + (memory.recency_score * 0.2)
                + (memory.frequency_score * 0.3),
                3,
            )
            if memory.score < settings.forgetting_threshold:
                memory.is_deleted = True
                vector_store.delete_memory(user_id, memory.id)
                removed += 1
        db.commit()
        return removed

    @staticmethod
    def retrieve_answer(db: Session, user_id: int, query: str, top_k: int = 5) -> dict:
        search_hits = vector_store.search(user_id, query, top_k)
        memory_ids = [hit[0] for hit in search_hits]
        if not memory_ids:
            return {
                "answer": "I do not have enough memory context yet. Add more memories first.",
                "confidence": 0.0,
                "source_memories": [],
            }

        memories = db.scalars(
            select(Memory).where(
                Memory.user_id == user_id,
                Memory.id.in_(memory_ids),
                Memory.is_deleted.is_(False),
            )
        ).all()
        memory_map = {memory.id: memory for memory in memories}
        ordered = [memory_map[mid] for mid in memory_ids if mid in memory_map]

        context_chunks = []
        sims = []
        now = datetime.utcnow()
        for memory_id, score in search_hits:
            if memory_id not in memory_map:
                continue
            memory = memory_map[memory_id]
            memory.access_count += 1
            memory.frequency_score = min(1.0, memory.frequency_score + 0.05)
            memory.last_accessed = now
            memory.score = round(
                (memory.importance_score * 0.5)
                + (memory.recency_score * 0.2)
                + (memory.frequency_score * 0.3),
                3,
            )
            context_chunks.append(f"- {memory.stored_text}")
            sims.append(score)

        db.add(
            QueryLog(
                user_id=user_id,
                query=query,
                retrieved_memory_ids=json.dumps(memory_ids),
            )
        )
        db.commit()

        answer = "Based on your stored memories:\n" + "\n".join(context_chunks[:top_k])
        confidence = round(sum(sims) / max(1, len(sims)), 3)
        return {
            "answer": answer,
            "confidence": confidence,
            "source_memories": ordered,
        }

    @staticmethod
    def reminders(db: Session, user_id: int) -> list[str]:
        tomorrow = datetime.utcnow() + timedelta(days=1)
        memories = db.scalars(
            select(Memory).where(
                Memory.user_id == user_id,
                Memory.is_deleted.is_(False),
                Memory.score >= 0.6,
            )
        ).all()
        reminders = []
        for memory in memories:
            text = (memory.stored_text or "").lower()
            if "deadline" in text or "exam" in text or "tomorrow" in text:
                reminders.append(f"Important memory #{memory.id}: {memory.stored_text[:90]}")
        if not reminders and memories:
            top = sorted(memories, key=lambda m: m.score, reverse=True)[:3]
            reminders = [f"Review memory #{memory.id}: {memory.stored_text[:90]}" for memory in top]
        if not reminders:
            reminders.append(f"No urgent reminders for {tomorrow.date()}. Keep adding useful memories.")
        return reminders

    @staticmethod
    def stats(db: Session, user_id: int) -> dict:
        total = db.scalar(
            select(func.count(Memory.id)).where(Memory.user_id == user_id, Memory.is_deleted.is_(False))
        ) or 0
        high = db.scalar(
            select(func.count(Memory.id)).where(
                Memory.user_id == user_id,
                Memory.is_deleted.is_(False),
                Memory.score >= settings.high_score_threshold,
            )
        ) or 0
        avg = db.scalar(
            select(func.avg(Memory.score)).where(Memory.user_id == user_id, Memory.is_deleted.is_(False))
        ) or 0.0
        return {
            "total_memories": int(total),
            "high_value_memories": int(high),
            "avg_score": round(float(avg), 3),
            "reminders": MemoryService.reminders(db, user_id),
        }


memory_service = MemoryService()
