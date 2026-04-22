import re

WORD_RE = re.compile(r"[A-Za-z0-9_]+")


def preprocess_text(text: str) -> str:
    return " ".join(text.strip().split())


def extract_keywords(text: str, max_keywords: int = 12) -> list[str]:
    words = [w.lower() for w in WORD_RE.findall(text)]
    stop_words = {
        "the",
        "and",
        "for",
        "that",
        "this",
        "with",
        "from",
        "have",
        "will",
        "your",
        "about",
        "into",
        "when",
        "what",
        "where",
        "which",
        "then",
        "than",
        "them",
        "they",
        "been",
        "were",
        "also",
    }
    scored: dict[str, int] = {}
    for word in words:
        if len(word) <= 2 or word in stop_words:
            continue
        scored[word] = scored.get(word, 0) + 1
    return [w for w, _ in sorted(scored.items(), key=lambda x: x[1], reverse=True)[:max_keywords]]


def extract_entities(text: str) -> list[str]:
    tokens = text.split()
    entities = []
    for token in tokens:
        clean = token.strip(".,:;!?()[]{}")
        if clean and clean[0].isupper() and len(clean) > 2:
            entities.append(clean)
    return list(dict.fromkeys(entities))[:10]


def summarize_text(text: str) -> str:
    sentences = re.split(r"(?<=[.!?])\s+", text)
    return " ".join(sentences[:2]).strip()[:300]
