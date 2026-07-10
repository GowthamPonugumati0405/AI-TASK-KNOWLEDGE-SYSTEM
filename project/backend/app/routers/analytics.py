from collections import Counter

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import require_role
from app.database import get_db
from app.models.activity_log import ActivityLog
from app.models.document import Document
from app.models.task import Task, TaskStatus
from app.models.user import User
from app.schemas.analytics import AnalyticsOut, SearchQueryCount

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/", response_model=AnalyticsOut)
def get_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
):
    total_tasks = db.query(Task).count()
    completed_tasks = db.query(Task).filter(Task.status == TaskStatus.completed).count()
    pending_tasks = db.query(Task).filter(Task.status == TaskStatus.pending).count()
    total_documents = db.query(Document).count()
    total_users = db.query(User).count()

    search_logs = db.query(ActivityLog).filter(ActivityLog.action == "search").all()
    counter = Counter(log.details.strip().lower() for log in search_logs if log.details)
    most_searched = [
        SearchQueryCount(query=q, count=c) for q, c in counter.most_common(10)
    ]

    return AnalyticsOut(
        total_tasks=total_tasks,
        completed_tasks=completed_tasks,
        pending_tasks=pending_tasks,
        total_documents=total_documents,
        total_users=total_users,
        most_searched_queries=most_searched,
    )
