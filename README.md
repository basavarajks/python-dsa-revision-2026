# MemoryVault AI – Adaptive External Brain with Smart Forgetting

MemoryVault AI is a **100% free, local-first full-stack app** that simulates human-like memory behavior:
- learns what matters,
- forgets low-value information,
- links related knowledge,
- answers with context and confidence.

## 1) Architecture Explanation

### Backend (FastAPI + SQLite + FAISS)
- **Auth Layer**: JWT signup/login, user-isolated memories
- **Ingestion Pipeline**:
  - preprocess input
  - keyword/entity extraction
  - score calculation (importance + recency + frequency)
  - decision engine: `store_full`, `store_summary`, `discard`
  - decision history logging for explainability
- **Memory Engine**:
  - adaptive learning (score updates on retrieval)
  - time decay & forgetting (remove low-score memories)
  - knowledge linking (keyword-overlap edges)
- **Vector Memory**:
  - SentenceTransformer embeddings (`all-MiniLM-L6-v2`)
  - FAISS similarity search
  - SQLite metadata mapping
- **RAG-style Retrieval**:
  - top-k vector retrieval
  - context assembly
  - confidence score output
- **Proactive AI**:
  - reminder suggestions from high-priority memories

### Frontend (React + Tailwind)
- **Auth screen** (signup/login)
- **Dashboard** (stats + reminders + activity timeline)
- **Memory Explorer** (ingest memories + score explainability + linked memory graph list)
- **Ask AI** (query, answer, confidence, source memories)

---

## 2) Backend Code (Modular)

Backend source folder:
- `/home/runner/work/python-dsa-revision-2026/python-dsa-revision-2026/backend/app/main.py`
- `/home/runner/work/python-dsa-revision-2026/python-dsa-revision-2026/backend/app/models.py`
- `/home/runner/work/python-dsa-revision-2026/python-dsa-revision-2026/backend/app/schemas.py`
- `/home/runner/work/python-dsa-revision-2026/python-dsa-revision-2026/backend/app/routers/`
- `/home/runner/work/python-dsa-revision-2026/python-dsa-revision-2026/backend/app/services/`

Install requirements from:
- `/home/runner/work/python-dsa-revision-2026/python-dsa-revision-2026/backend/requirements.txt`

---

## 3) Frontend Code (React Components)

Frontend source folder:
- `/home/runner/work/python-dsa-revision-2026/python-dsa-revision-2026/frontend/src/App.jsx`
- `/home/runner/work/python-dsa-revision-2026/python-dsa-revision-2026/frontend/src/lib/api.js`
- Tailwind setup in:
  - `/home/runner/work/python-dsa-revision-2026/python-dsa-revision-2026/frontend/tailwind.config.js`
  - `/home/runner/work/python-dsa-revision-2026/python-dsa-revision-2026/frontend/src/index.css`

---

## 4) Setup Instructions (Windows 11 + VS Code, 100% Free)

### Prerequisites
1. Install **Python 3.11+** from python.org (check “Add Python to PATH”)
2. Install **Node.js LTS** from nodejs.org
3. Install **Git**
4. Install **VS Code**

### Open project in VS Code
1. Open VS Code
2. `File -> Open Folder`
3. Select:
   `C:\path\to\python-dsa-revision-2026`

### Backend setup (PowerShell)
```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
uvicorn app.main:app --reload
```
Backend runs at: `http://127.0.0.1:8000`

### Frontend setup (new terminal)
```powershell
cd frontend
npm install
npm run dev
```
Frontend runs at: `http://127.0.0.1:5173`

---

## 5) API Endpoints List

### Auth
- `POST /auth/signup`
- `POST /auth/login`

### Memory
- `POST /memories/ingest`
- `GET /memories`
- `GET /memories/decisions`
- `POST /memories/decay`
- `GET /memories/{memory_id}/links`
- `GET /memories/reminders/list`

### AI + Dashboard
- `POST /ask`
- `GET /dashboard/stats`
- `GET /dashboard/timeline`

---

## 6) Example Test Data
Use sample inputs from:
- `/home/runner/work/python-dsa-revision-2026/python-dsa-revision-2026/backend/sample_data/memory_samples.json`

Example memory text:
- `Project Atlas deadline is tomorrow at 5 PM. Submit architecture diagram and API docs.`
- `AWS certification exam is on next Monday. Revise IAM, VPC, and EC2.`

---

## 7) Demo Flow (Hackathon-ready)
1. Sign up in UI
2. Ingest 4–5 memories
3. Observe decision type and score breakdown
4. Open Dashboard for stats/reminders
5. Ask: “What are my urgent tasks?”
6. See answer + confidence + source memories
7. Open Memory Explorer and inspect linked memories
8. Trigger `/memories/decay` to simulate forgetting

---

## Improvements You Can Add Next
1. Add Redis queue + APScheduler for automatic daily decay jobs
2. Use spaCy NER for stronger entity extraction
3. Add OCR/file/voice ingestion pipeline
4. Add graph visualization library (React Flow/Cytoscape)
5. Add evaluation metrics and feedback loop for answer quality
