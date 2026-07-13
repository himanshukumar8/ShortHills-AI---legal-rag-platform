from __future__ import annotations

import logging
from answer_engine.models import GeneratedPrompt, MissingRequirementError

logger = logging.getLogger(__name__)

def validate_prompt(prompt: GeneratedPrompt) -> bool:
    """Validates that the generated prompt strictly adheres to all rules."""
    
    issues = []
    
    # 1. Hallucination Guardrails
    if "NEVER invent facts" not in prompt.system_prompt:
        issues.append("Missing 'NEVER invent facts' guardrail.")
    if "cannot be determined from the provided documents" not in prompt.system_prompt:
        issues.append("Missing fallback instruction for insufficient evidence.")
        
    # 2. Citation Instructions
    if "Citation Rules" not in prompt.system_prompt:
        issues.append("Missing 'Citation Rules' section.")
        
    # 3. Output Format Rules
    if "Output Format Rules" not in prompt.system_prompt:
        issues.append("Missing 'Output Format Rules' section.")
    if "{" not in prompt.system_prompt or "}" not in prompt.system_prompt:
        issues.append("JSON output schema is missing or malformed.")
        
    # 4. Context Inclusion
    if prompt.included_chunks == 0 and prompt.context_token_count == 0:
        issues.append("No context chunks were included in the prompt.")
        
    if "Retrieved Context" not in prompt.user_prompt:
        issues.append("Missing 'Retrieved Context' header in user prompt.")
        
    if issues:
        raise MissingRequirementError(f"Prompt validation failed: {issues}")
        
    return True
