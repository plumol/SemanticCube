# models/request_schema.py
from pydantic import BaseModel


class QueryRequest(BaseModel):
    query: str
