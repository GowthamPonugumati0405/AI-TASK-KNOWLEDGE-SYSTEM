from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.routers import analytics, auth, documents, search, tasks

# Create tables if they don't exist (for quick start; use Alembic for real migrations)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI-Powered Task & Knowledge Management System",
    version="1.0.0",
    description="JWT-secured RBAC API with embedding-based semantic search over uploaded documents.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(tasks.router)
app.include_router(documents.router)
app.include_router(search.router)
app.include_router(analytics.router)


@app.get("/health")
def health_check():
    return {"status": "ok"}
