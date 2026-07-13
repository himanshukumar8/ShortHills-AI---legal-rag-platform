from fastapi import APIRouter
from typing import Dict, Any
from api.utils import metrics_store

router = APIRouter(prefix="/metrics", tags=["Metrics"])

@router.get("", response_model=Dict[str, Any])
async def get_metrics():
    return metrics_store.get_metrics()
