from fastapi import APIRouter, Depends, HTTPException
from api.models import QueryRequest, QueryResponse
from api.services.rag_service import RagService
from api.dependencies import get_rag_service

router = APIRouter(prefix="/query", tags=["Query"])

@router.post("", response_model=QueryResponse)
async def execute_query(
    request: QueryRequest,
    rag_service: RagService = Depends(get_rag_service)
):
    try:
        return rag_service.answer_query(request.query)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query execution failed: {str(e)}")
