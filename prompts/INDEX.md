# Prompt Index

| Module | Description | Artifact |
|---|---|---|
| 01_dataset_manifest | Defining the core corpus requirements and structural expectations. | `01_dataset_manifest.md` |
| 02_corpus_downloader | Building the asynchronous fetch mechanism for raw legal PDFs. | `02_corpus_downloader.md` |
| 03_pdf_parser | Extracting hierarchical text blocks and maintaining layout integrity. | `03_pdf_parser.md` |
| 04_document_normalizer | Applying regex sanitization and metadata standardization. | `04_document_normalizer.md` |
| 05_semantic_chunker | Partitioning text while respecting structural paragraph boundaries. | `05_semantic_chunker.md` |
| 06_chunk_optimizer | Pre-calculating token limits and extracting core metadata schemas. | `06_chunk_optimizer.md` |
| 07_embedding_pipeline | Integrating the legal-specific sentence transformer models. | `07_embedding_pipeline.md` |
| 08_elasticsearch | Establishing the BM25 index for precise lexical searches. | `08_elasticsearch.md` |
| 09_qdrant | Establishing the dense vector database for semantic similarity. | `09_qdrant.md` |
| 10_hybrid_retrieval | Fusing Elasticsearch and Qdrant results mathematically via RRF. | `10_hybrid_retrieval.md` |
| 11_answer_engine | Orchestrating prompts and LLM generation based on retrieved context. | `11_answer_engine.md` |
| 12_citation_verification | Validating deterministic mapping between generated citations and context. | `12_citation_verification.md` |
| 13_faithfulness_validation | Utilizing NLI models to verify claims and prevent hallucinations. | `13_faithfulness_validation.md` |
| 14_evaluation_framework | Executing the Golden Set benchmark and rendering Matplotlib metrics. | `14_evaluation_framework.md` |
| 15_fastapi | Wrapping the pipeline into an asynchronous RESTful microservice. | `15_fastapi.md` |
| 16_streamlit | Building the enterprise presentation layer and UI components. | `16_streamlit.md` |
| 17_docker | Containerizing the ecosystem using Docker Compose and multi-stage builds. | `17_docker.md` |
| 18_deployment | Preparing environment schemas, CORS rules, and SaaS CI/CD paths. | `18_deployment.md` |
| 19_documentation | Authoring the final architecture docs, ADSs, and Submission Report. | `19_documentation.md` |
