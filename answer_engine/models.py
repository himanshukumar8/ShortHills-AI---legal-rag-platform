from __future__ import annotations
from dataclasses import dataclass, field
from hybrid_retriever.models import RetrievedResult

@dataclass
class PromptContext:
    query: str
    retrieved_chunks: list[RetrievedResult]
    
@dataclass
class GeneratedPrompt:
    system_prompt: str
    user_prompt: str
    estimated_tokens: int
    context_token_count: int
    included_chunks: int
    
class PromptGenerationError(Exception):
    pass

class TokenLimitExceededError(PromptGenerationError):
    pass

class MissingRequirementError(PromptGenerationError):
    pass

@dataclass
class CitationVerificationResult:
    document: str
    page: int
    section: str
    status: str
    supporting_chunk_id: str | None
    confidence: float
    message: str

@dataclass
class EngineVerificationOutput:
    verification_status: str
    overall_score: float
    citations: list[CitationVerificationResult]
    unsupported_claims: list[str]
    warnings: list[str]

@dataclass
class ClaimVerificationResult:
    claim: str
    status: str
    supporting_chunks: list[str]
    confidence: float

@dataclass
class FaithfulnessOutput:
    overall_faithfulness_score: float
    overall_status: str
    claims: list[ClaimVerificationResult]
    unsupported_claims: list[str]
    contradictions: list[str]

