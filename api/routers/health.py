from fastapi import APIRouter
from api.models import HealthResponse
from api.config import api_config

router = APIRouter(prefix="/health", tags=["Health"])

@router.get("", response_model=HealthResponse)
async def check_health():
    return HealthResponse(
        status="healthy",
        version=api_config.version
    )
