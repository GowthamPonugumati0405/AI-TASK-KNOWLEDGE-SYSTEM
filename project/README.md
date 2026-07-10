# AI-Powered Task & Knowledge Management System

An MVP where an **admin** builds a knowledge base by uploading `.txt` documents and
assigns tasks to **users**, who search the knowledge base with AI-powered semantic
search and complete their tasks.

## Tech Stack

| Layer      | Technology |
|------------|------------|
| Backend    | Python, FastAPI, SQLAlchemy |
| Database   | MySQL |
| Auth       | JWT (python-jose) + RBAC |
| AI Search  | sentence-transformers (local embedding model) + FAISS |
| Frontend   | React 18 (Vite), React Router, Axios |

## Folder Structure

```
project/
├── backend/
│   ├── app/
│   │   ├── main.py            # FastAPI app + router registration
│   │   ├── config.py          # env-based settings
│   │   ├── database.py        # SQLAlchemy engine/session
│   │   ├── models/            # users, roles, tasks, documents, activity_logs
│   │   ├── schemas/           # Pydantic request/response models
│   │   ├── core/              # security (JWT/hashing), RBAC dependencies
│   │   ├── services/          # embedding_service, vector_store, activity_service
│   │   └── routers/           # auth, tasks, documents, search, analytics
│   ├── scripts/init_db.py     # seeds roles + default admin
│   ├── schema.sql             # reference relational schema
│   └── requirements.txt
└── frontend/
    └── src/
        ├── api/axios.js       # JWT-attached HTTP client
        ├── context/AuthContext.jsx
        ├── components/        # TaskList, TaskForm, DocumentUpload, SearchBar, Analytics
        └── pages/              # Login, AdminDashboard, UserDashboard
```

## How the AI Search Works (core logic, not just an LLM call)

1. **Upload**: admin uploads a `.txt` file. The raw text is chunked with a
   word-based sliding window (`chunk_text` in `embedding_service.py`).
2. **Embed**: each chunk is converted to a vector locally using
   `sentence-transformers` (`all-MiniLM-L6-v2`, 384 dimensions) — no external
   LLM API is called for this.
3. **Store**: vectors are L2-normalized and added to a FAISS `IndexFlatIP`
   index (`vector_store.py`), which makes inner-product search equivalent to
   cosine similarity. A parallel `metadata.json` maps vector ids back to
   `(document_id, title, chunk_text)`. Both are persisted to disk under
   `backend/vector_index/`.
4. **Query**: a search request is embedded the same way and FAISS returns the
   top-k most similar chunks with similarity scores.

## Setup

### 1. MySQL

```sql
CREATE DATABASE task_knowledge_db;
```
(Tables are auto-created on first backend run via SQLAlchemy; `schema.sql` is
provided as a reference / for manual setup.)

### 2. Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# edit .env with your MySQL credentials and a real JWT_SECRET_KEY

python -m scripts.init_db       # creates roles + default admin (admin / admin123)
uvicorn app.main:app --reload   # http://localhost:8000
```

API docs (Swagger UI) are auto-generated at **http://localhost:8000/docs**.

> First run will download the `all-MiniLM-L6-v2` embedding model from
> HuggingFace (~90MB) — needs an internet connection once, then it's cached.

### 3. Frontend

```bash
cd frontend
npm install
npm run dev                     # http://localhost:5173
```

### 4. Try it out

1. Log in as `admin` / `admin123`.
2. Register a normal user via `POST /auth/register` (Swagger UI) with
   `"role": "user"`, or add a registration form later.
3. As admin: upload a `.txt` file, then assign a task to the new user (using
   their user ID, visible via `GET /auth/me` or the DB).
4. Log in as that user: search the knowledge base and mark the task completed.
5. Back in admin: check `/analytics` for totals and most-searched queries.

## Required APIs

| Method | Path | Access |
|--------|------|--------|
| POST | `/auth/login` | public |
| POST | `/auth/register` | public |
| GET | `/auth/me` | authenticated |
| GET/POST | `/tasks` | authenticated (admin creates; users see only their own) |
| PATCH | `/tasks/{id}/status` | owner or admin |
| POST/GET | `/documents` | admin uploads; any authenticated user can list |
| POST | `/search` | authenticated |
| GET | `/analytics` | admin only |

Dynamic filtering example: `GET /tasks?status=completed&assigned_to=1`

## Notes / Trade-offs (for review)

- `Base.metadata.create_all()` is used for quick schema setup instead of
  Alembic migrations, appropriate for a 1.5-day MVP.
- `.txt` uploads only, per the mandatory requirement (PDF was optional and
  left out to keep scope tight — `documents.py`'s `ALLOWED_EXTENSIONS` is the
  single place to extend this).
- Chunking is word-based rather than token-based for simplicity and zero
  extra dependencies; swapping in a tokenizer-aware splitter is a drop-in
  change in `embedding_service.chunk_text`.
