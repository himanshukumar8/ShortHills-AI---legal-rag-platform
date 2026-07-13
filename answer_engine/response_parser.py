from __future__ import annotations

import json
import logging
from answer_engine.llm_provider import LLMResponse

logger = logging.getLogger(__name__)

class JSONParsingError(Exception):
    pass

def parse_llm_response(response: LLMResponse) -> dict:
    """Safely extracts and parses JSON from the LLM's raw text response."""
    raw_text = response.raw_response.strip()
    
    # Strip markdown code blocks if the LLM wrapped it
    if raw_text.startswith("```json"):
        raw_text = raw_text[7:]
    elif raw_text.startswith("```"):
        raw_text = raw_text[3:]
        
    if raw_text.endswith("```"):
        raw_text = raw_text[:-3]
        
    raw_text = raw_text.strip()
    
    try:
        parsed_data = json.loads(raw_text)
        return parsed_data
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse LLM JSON: {e}")
        logger.debug(f"Raw text was: {raw_text}")
        raise JSONParsingError(f"Invalid JSON returned from LLM: {e}")
