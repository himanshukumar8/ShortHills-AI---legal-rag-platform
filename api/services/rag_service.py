from answer_engine.main import run_prompt_builder
from api.models import QueryResponse, CitationModel

class RagService:
    def answer_query(self, query: str) -> QueryResponse:
        # We reuse the run_prompt_builder from answer_engine which internally 
        # calls hybrid_retriever, builds prompt, generates answer, and verifies it.
        # But wait, run_prompt_builder returns the *prompt* trace currently!
        # Let's import the full pipeline components directly instead of relying on the CLI test wrapper.
        
        from hybrid_retriever.config import HybridConfig
        from hybrid_retriever.main import run_pipeline as run_hybrid
        from answer_engine.config import AnswerEngineConfig
        from answer_engine.prompt_builder import PromptBuilder
        from answer_engine.answer_generator import AnswerGenerator
        from answer_engine.citation_engine import CitationEngine
        from answer_engine.faithfulness_validator import FaithfulnessValidator
        from answer_engine.models import PromptContext, RetrievedResult
        
        # 1. Retrieval
        hybrid_conf = HybridConfig(top_k=5)
        retrieval_trace = run_hybrid(hybrid_conf, query=query)
        
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
            
        context = PromptContext(query=query, retrieved_chunks=chunks)
        
        # 2. Answer Engine
        config = AnswerEngineConfig()
        builder = PromptBuilder(config)
        prompt = builder.build(context)
        
        generator = AnswerGenerator(config)
        answer_payload = generator.generate_answer(prompt)
        
        # 3. Verification
        cit_engine = CitationEngine(config)
        cit_output = cit_engine.verify(query, context.retrieved_chunks, answer_payload)
        
        faith_engine = FaithfulnessValidator(config)
        faith_output = faith_engine.validate(answer_payload, cit_output, context.retrieved_chunks)
        
        # 4. Format Response
        citations = []
        for c in cit_output.citations:
            citations.append(CitationModel(
                document=c.document,
                page=c.page,
                section=c.section,
                status=c.status,
                confidence=c.confidence,
                message=c.message
            ))
            
        return QueryResponse(
            answer=answer_payload.get("answer", ""),
            citations=citations,
            confidence=answer_payload.get("confidence", "UNKNOWN"),
            limitations=answer_payload.get("limitations", "None"),
            retrieval_trace=retrieval_trace
        )
