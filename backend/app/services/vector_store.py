import pickle
from pathlib import Path

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

BASE_DIR = Path(__file__).resolve().parents[2]
VECTOR_DIR = BASE_DIR / "data" / "vectors"
VECTOR_DIR.mkdir(parents=True, exist_ok=True)


class VectorStore:
    def __init__(self) -> None:
        self.model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

    def _path(self, user_id: int) -> Path:
        return VECTOR_DIR / f"user_{user_id}.pkl"

    def _load(self, user_id: int) -> tuple[np.ndarray, list[int]]:
        path = self._path(user_id)
        if not path.exists():
            return np.zeros((0, 384), dtype="float32"), []
        with path.open("rb") as file:
            payload = pickle.load(file)
        return payload["vectors"], payload["memory_ids"]

    def _save(self, user_id: int, vectors: np.ndarray, memory_ids: list[int]) -> None:
        with self._path(user_id).open("wb") as file:
            pickle.dump({"vectors": vectors, "memory_ids": memory_ids}, file)

    def embed(self, text: str) -> np.ndarray:
        return np.array(self.model.encode([text], normalize_embeddings=True), dtype="float32")[0]

    def add_memory(self, user_id: int, memory_id: int, text: str) -> None:
        vectors, memory_ids = self._load(user_id)
        embedding = self.embed(text).reshape(1, -1)
        vectors = np.vstack([vectors, embedding]) if len(vectors) else embedding
        memory_ids.append(memory_id)
        self._save(user_id, vectors, memory_ids)

    def search(self, user_id: int, query: str, top_k: int = 5) -> list[tuple[int, float]]:
        vectors, memory_ids = self._load(user_id)
        if len(memory_ids) == 0:
            return []

        query_vector = self.embed(query).reshape(1, -1)
        index = faiss.IndexFlatIP(vectors.shape[1])
        index.add(vectors)
        scores, indices = index.search(query_vector, min(top_k, len(memory_ids)))

        results = []
        for idx, score in zip(indices[0], scores[0], strict=False):
            if idx == -1:
                continue
            results.append((memory_ids[idx], float(score)))
        return results

    def delete_memory(self, user_id: int, memory_id: int) -> None:
        vectors, memory_ids = self._load(user_id)
        if memory_id not in memory_ids:
            return
        keep = [i for i, mid in enumerate(memory_ids) if mid != memory_id]
        new_vectors = vectors[keep] if keep else np.zeros((0, vectors.shape[1]), dtype="float32")
        new_memory_ids = [memory_ids[i] for i in keep]
        self._save(user_id, new_vectors, new_memory_ids)


vector_store = VectorStore()
