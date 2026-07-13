from __future__ import annotations

import json
import logging
from answer_engine.config import AnswerEngineConfig
from answer_engine.models import PromptContext, GeneratedPrompt, TokenLimitExceededError
from answer_engine.prompt_templates import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE
from answer_engine.utils import estimate_tokens

logger = logging.getLogger(__name__)

class PromptBuilder:
    def __init__(self, config: AnswerEngineConfig):
        self.config = config
        
    def build(self, context: PromptContext) -> GeneratedPrompt:
        """Constructs the full prompt from the user query and retrieved context."""
        
        # 1. Format context blocks
        context_blocks_str = ""
        included_chunks = 0
        context_tokens = 0
        
        for res in context.retrieved_chunks:
            # We mock the actual text content here since RetrievedResult doesn't carry full text 
            # to save memory. In a real engine, we'd fetch the chunk text from the DB or payload.
            # We represent the chunk text via a placeholder for the Prompt Builder test.
            chunk_text = f"[Text content for chunk {res.chunk_id}]"
            
            block = (
                f"### Excerpt {included_chunks + 1}\n"
                f"Document Title: {res.document_title}\n"
                f"Citation: {res.citation}\n"
                f"Page Range: {res.page_start}-{res.page_end}\n"
                f"Category: {res.category}\n"
                f"Content:\n{chunk_text}\n\n"
            )
            
            block_tokens = estimate_tokens(block)
            if context_tokens + block_tokens > self.config.max_context_tokens:
                logger.warning(f"Context token limit reached ({context_tokens}/{self.config.max_context_tokens}). Truncating further chunks.")
                break
                
            context_blocks_str += block
            context_tokens += block_tokens
            included_chunks += 1
            
        # 2. Construct User Prompt
        user_prompt = USER_PROMPT_TEMPLATE.format(
            query=context.query,
            context_blocks=context_blocks_str
        )
        
        total_tokens = estimate_tokens(SYSTEM_PROMPT) + estimate_tokens(user_prompt)
        
        if total_tokens > self.config.max_total_tokens:
            raise TokenLimitExceededError(f"Total prompt tokens ({total_tokens}) exceed max ({self.config.max_total_tokens})")
            
        return GeneratedPrompt(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=user_prompt,
            estimated_tokens=total_tokens,
            context_token_count=context_tokens,
            included_chunks=included_chunks
        )
