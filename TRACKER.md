# Project Tracker

## Project Setup
- [x] Create project documentation (PROJECT_GUIDE.md, TRACKER.md, DECISIONS.md, CONTEXT.md)
- [ ] Initialize Git repository and `.gitignore`
- [ ] Set up Python virtual environment and dependency management
- [ ] Configure linting and formatting tools (`black`, `ruff`, `mypy`)
- [x] Define base folder structure

## Dataset & Corpus
- [x] Finalize curated dataset plan (100 documents)
- [x] Create dataset manifest (CSV + JSON)
- [x] Phase 1: Corpus Downloader & Manifest
- [x] Phase 2: PDF Parsing & Extraction
- [x] Phase 3: Document Normalization
- [x] Phase 4: Semantic Legal Chunking
- [x] Phase 4.1: Chunk QA & Validation
## Retrieval Engine
- [x] Phase 7.1: Setup Lexical & Semantic Adapters
- [x] Phase 7.2: Reciprocal Rank Fusion (RRF) Logic
- [x] Phase 7.3: Implement Citation Validation
- [x] Phase 7.4: Build Response Schema (JSON Trace)

## Answer Engine
- [x] Phase 7: Hybrid Retrieval Engine
- [x] Phase 8: Answer Engine & Generation
- [x] Phase 9: Golden Set Evaluation Dataset Module
- [x] Phase 10: Evaluation Framework
- [x] Phase 11: FastAPI Service Layer
- [x] Phase 12: Streamlit Presentation Layer
- [x] Phase 13: Containerization & Deployment
- [x] Phase 14: Production Deployment Preparation
- [x] Phase 15: Architecture Documentation
- [x] Phase 16: Final Project README
- [x] Phase 8.3: Citation Verification Engine
- [x] Phase 8.4: Faithfulness Validation Engine
- [x] Phase 5: Embeddings Generation
- [x] Phase 6.1: Keyword Search Indexing (Elasticsearch)
- [x] Phase 6.1.1: Elasticsearch QA & Benchmark
- [x] Phase 6.1.2: Elasticsearch Error Analysis
- [x] Phase 6.2: Vector Search Indexing (Qdrant)
- [x] Phase 6.2.1: Qdrant QA & Validation

## Document Processing
- [x] Implement PDF Parsing module (PyMuPDF + pdfplumber fallback)
- [x] Metadata Extraction pipeline
- [x] Implement text Chunking strategy (e.g., semantic or recursive character splitting)

## Embedding & Indexing
- [ ] Implement Embedding Generation service
- [ ] Set up and configure Elasticsearch for keyword search
- [ ] Set up and configure Qdrant for vector search
- [ ] Implement data ingestion pipelines for both databases

## Search & QA
- [ ] Implement Hybrid Search engine (combining Elasticsearch and Qdrant)
- [ ] Implement LLM integration for answering legal queries
- [ ] Implement Citation Engine for tracing answers to source chunks

## Storage
- [ ] Set up PostgreSQL for application state and metadata
- [ ] Implement database migrations (e.g., Alembic)
- [ ] (Optional) Set up Neo4j for knowledge graph integration

## User Interface
- [ ] Set up Streamlit application
- [ ] Build search interface
- [ ] Build document viewer and citation UI

## Evaluation & Deployment
- [ ] Develop Golden Set evaluation pipeline
- [ ] Dockerize all application components (API, UI, databases)
- [ ] Write deployment documentation
