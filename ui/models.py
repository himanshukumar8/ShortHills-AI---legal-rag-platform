from dataclasses import dataclass
from typing import List, Dict, Any, Optional

@dataclass
class Citation:
    document: str
    page: int
    section: str
    status: str
    confidence: float
    message: str

@dataclass
class QueryResponseModel:
    answer: str
    citations: List[Citation]
    confidence: str
    limitations: str
    retrieval_trace: Dict[str, Any]
    
@dataclass
class SystemHealth:
    status: str
    version: str
    
@dataclass
class SystemMetrics:
    total_requests: int
    error_rate: float
    average_latency_s: float
