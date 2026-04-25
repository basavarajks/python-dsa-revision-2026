from pydantic import BaseModel


class Settings(BaseModel):
    app_name: str = "MemoryVault AI"
    secret_key: str = "change-this-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24
    database_url: str = "sqlite:///./memoryvault.db"
    cors_origins: tuple[str, ...] = ("http://127.0.0.1:5173", "http://localhost:5173")
    important_keywords: tuple[str, ...] = (
        "exam",
        "deadline",
        "interview",
        "meeting",
        "payment",
        "urgent",
        "doctor",
        "assignment",
        "project",
        "tomorrow",
    )
    high_score_threshold: float = 0.70
    medium_score_threshold: float = 0.40
    forgetting_threshold: float = 0.20
    decay_per_day: float = 0.01


settings = Settings()
