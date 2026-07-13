from pydantic import BaseModel, Field
from typing import List, Dict, Any

class QueryRequest(BaseModel):
    query: str = Field(..., description="The legal question to answer")

class CitationModel(BaseModel):
    document: str
    page: int
    section: str
    status: str
    confidence: float
    message: str

class QueryResponse(BaseModel):
    answer: str
    citations: List[CitationModel]
    confidence: str
    limitations: str
    retrieval_trace: Dict[str, Any]

class HealthResponse(BaseModel):
    status: str
    version: str
