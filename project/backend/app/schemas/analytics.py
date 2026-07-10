from typing import List

from pydantic import BaseModel


class SearchQueryCount(BaseModel):
    query: str
    count: int


class AnalyticsOut(BaseModel):
    total_tasks: int
    completed_tasks: int
    pending_tasks: int
    total_documents: int
    total_users: int
    most_searched_queries: List[SearchQueryCount]
