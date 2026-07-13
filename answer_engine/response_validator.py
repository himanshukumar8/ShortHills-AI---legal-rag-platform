from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

class ValidationFailedError(Exception):
    pass

def validate_answer_schema(parsed_json: dict) -> bool:
    """Verifies that the parsed JSON meets the strict Answer Engine schema constraints."""
    
    # 1. Verify required fields exist
    required_fields = ["answer", "citations", "confidence", "limitations"]
    for field in required_fields:
        if field not in parsed_json:
            raise ValidationFailedError(f"Missing required field: '{field}'")
            
    # 2. Check for empty answers
    if not str(parsed_json["answer"]).strip():
        raise ValidationFailedError("Answer field is empty.")
        
    # 3. Verify citations array
    if not isinstance(parsed_json["citations"], list):
        raise ValidationFailedError("Citations must be a JSON array.")
        
    for i, cit in enumerate(parsed_json["citations"]):
        for cit_field in ["document_title", "page_number", "section", "citation"]:
            if cit_field not in cit:
                raise ValidationFailedError(f"Citation at index {i} is missing '{cit_field}'")
                
    # 4. Enforce confidence constraints
    if parsed_json["confidence"] not in ["HIGH", "MEDIUM", "LOW"]:
        logger.warning(f"Unexpected confidence value: {parsed_json['confidence']}")
        # We don't fail hard here, just log a warning.
        
    return True
