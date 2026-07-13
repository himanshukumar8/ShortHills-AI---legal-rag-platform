from __future__ import annotations

import logging
import sys
import json

from answer_engine.config import AnswerEngineConfig
from answer_engine.models import PromptContext, GeneratedPrompt
from answer_engine.prompt_builder import PromptBuilder
from answer_engine.validator import validate_prompt
from answer_engine.answer_generator import AnswerGenerator
from answer_engine.citation_engine import CitationEngine
from answer_engine.faithfulness_validator import FaithfulnessValidator
from answer_engine.reporter import CitationReporter, FaithfulnessReporter

# We import the pipeline to mock out the retrieval step so we have real data to build the prompt
from hybrid_retriever.main import run_pipeline as run_hybrid
from hybrid_retriever.config import HybridConfig
from hybrid_retriever.models import RetrievedResult

logger = logging.getLogger("answer_engine")

def _setup_logging(config: AnswerEngineConfig) -> None:
    config.log_dir.mkdir(parents=True, exist_ok=True)
    root_logger = logging.getLogger("answer_engine")
    root_logger.setLevel(logging.INFO)
    root_logger.handlers.clear()
    
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)-8s | ANSWER | %(message)s"))
    root_logger.addHandler(console_handler)

def run_prompt_builder(query: str = "Taxation rules for independent contractors under IRS Section 162") -> dict:
    """Executes the prompt builder pipeline."""
    config = AnswerEngineConfig()
    _setup_logging(config)
    
    logger.info("=" * 60)
    logger.info(f"Answer Engine \u2014 Prompt Builder Starting")
    logger.info(f"Query: '{query}'")
    logger.info("=" * 60)
    
    # 1. Retrieve Data (Mocking the Retrieval Step)
    logger.info("Retrieving legal context chunks...")
    
    # We suppress logs from hybrid retriever to keep output clean
    logging.getLogger("hybrid_retriever").setLevel(logging.WARNING)
    logging.getLogger("es_indexer").setLevel(logging.ERROR)
    logging.getLogger("qdrant_indexer").setLevel(logging.ERROR)
    
    hybrid_conf = HybridConfig(use_mock=True, top_k=5)
    retrieval_trace = run_hybrid(hybrid_conf, query=query)
    
    # The hybrid retrieval trace returns dictionaries in "results" 
    # We map them back to RetrievedResult objects for the builder
    chunks = []
    for r in retrieval_trace.get("results", []):
        chunks.append(RetrievedResult(
            chunk_id=r["chunk_id"],
            document_id=r["document_id"],
            document_title=r["document_title"],
            category=r["category"],
            citation=r["citation"],
            page_start=r["pages"][0],
            page_end=r["pages"][1],
            bm25_rank=r["retrieval_metadata"]["bm25_rank"],
            vector_rank=r["retrieval_metadata"]["vector_rank"],
            rrf_score=r["retrieval_metadata"]["rrf_score"],
            retrieval_source=r["retrieval_metadata"]["source"]
        ))
        
    # In the mock, chunks might be empty because of strict simulated heuristic matching
    # To test the Prompt Builder, we inject a dummy chunk if none were retrieved
    if not chunks:
        logger.info("Injecting mock chunk for test generation...")
        chunks.append(RetrievedResult(
            chunk_id="CHK_MOCK_1",
            document_id="DOC_MOCK_1",
            document_title="Mock IRS Publication 15",
            category="IRS Publications",
            citation="IRS Pub 15",
            page_start=12,
            page_end=13
        ))
        chunks.append(RetrievedResult(
            chunk_id="CHK_MOCK_2",
            document_id="DOC_MOCK_2",
            document_title="Internal Revenue Code",
            category="Acts / Statutes",
            citation="26 U.S.C. 162",
            page_start=1,
            page_end=1
        ))

    context = PromptContext(query=query, retrieved_chunks=chunks)
    
    # 2. Build Prompt
    logger.info("Building structured prompt...")
    builder = PromptBuilder(config)
    prompt = builder.build(context)
    
    # 3. Validate
    logger.info("Validating prompt constraints...")
    validate_prompt(prompt)
    logger.info("Validation PASSED (Guardrails present, tokens within limits).")
    
    # 4. Save test trace
    report = {
        "query": query,
        "token_usage": {
            "estimated_total_tokens": prompt.estimated_tokens,
            "context_token_count": prompt.context_token_count,
            "included_chunks": prompt.included_chunks
        },
        "prompt": {
            "system_instructions": prompt.system_prompt,
            "user_prompt": prompt.user_prompt
        }
    }
    
    config.report_dir.mkdir(parents=True, exist_ok=True)
    report_path = config.report_dir / "prompt_builder_trace.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=4)
        
    logger.info(f"Generated prompt trace written to {report_path}")
    logger.info(f"Total prompt tokens: {prompt.estimated_tokens} | Chunks included: {prompt.included_chunks}")
    logger.info("=" * 60)
    logger.info("Prompt Builder executed successfully. Output ready for LLM.")
    logger.info("=" * 60)
    
    # 5. LLM Answer Generation
    logger.info("Initiating Answer Generation Phase...")
    generator = AnswerGenerator(config)
    
    # The PromptBuilder returned a GeneratedPrompt. We pass it to the AnswerGenerator.
    answer_payload = generator.generate_answer(prompt)
    
    logger.info("=" * 60)
    logger.info("Final Answer Generated Successfully!")
    logger.info("Confidence: " + answer_payload.get("confidence", "UNKNOWN"))
    logger.info("Citations Used: " + str(len(answer_payload.get("citations", []))))
    logger.info("=" * 60)
    
    # 6. Citation Verification
    logger.info("Initiating Citation Verification Phase...")
    cit_engine = CitationEngine(config)
    cit_output = cit_engine.verify(query, context.retrieved_chunks, answer_payload)
    
    CitationReporter.generate_reports(cit_output, config.report_dir)
    
    logger.info("=" * 60)
    logger.info(f"Citation Verification Complete: {cit_output.verification_status} (Score: {cit_output.overall_score:.1f})")
    logger.info("=" * 60)
    
    # 7. Faithfulness Validation
    logger.info("Initiating Faithfulness Validation Phase...")
    faith_engine = FaithfulnessValidator(config)
    faith_output = faith_engine.validate(answer_payload, cit_output, context.retrieved_chunks)
    
    FaithfulnessReporter.generate_reports(faith_output, config.report_dir)
    
    logger.info("=" * 60)
    logger.info(f"Faithfulness Validation Complete: {faith_output.overall_status} (Score: {faith_output.overall_faithfulness_score:.1f})")
    logger.info("=" * 60)

    return report

if __name__ == "__main__":
    run_prompt_builder()
