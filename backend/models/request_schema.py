# backend/models/request_schema.py
from pydantic import BaseModel
from enum import Enum

class QueryMode(str, Enum):
    ROLLUP = "rollup"
    FILTERING = "filtering"

class QueryRequest(BaseModel):
    query: str
    mode: QueryMode = QueryMode.ROLLUP  # Default to rollup mode