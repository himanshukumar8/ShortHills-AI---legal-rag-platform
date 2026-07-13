from api.services.rag_service import RagService
from api.services.evaluation_service import EvaluationService
from fastapi import Request

def get_rag_service() -> RagService:
    return RagService()

def get_evaluation_service() -> EvaluationService:
    return EvaluationService()
