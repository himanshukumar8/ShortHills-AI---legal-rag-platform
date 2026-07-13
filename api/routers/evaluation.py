from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any
from api.services.evaluation_service import EvaluationService
from api.dependencies import get_evaluation_service

router = APIRouter(prefix="/evaluate", tags=["Evaluation"])

@router.post("", response_model=Dict[str, Any])
async def run_evaluation(
    eval_service: EvaluationService = Depends(get_evaluation_service)
):
    try:
        return eval_service.run_eval()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Evaluation failed: {str(e)}")
