# AI Context Guide

## Current Phase
PDF Parsing & Metadata Extraction — Implementation Complete.

## Completed Work
- Initialized core project documentation (PROJECT_GUIDE.md, TRACKER.md, DECISIONS.md, CONTEXT.md).
- Finalized curated dataset plan (100 U.S. tax and legal documents).
- Created dataset manifest in CSV and JSON formats.
- Implemented the Corpus Download Pipeline (`corpus_downloader/`).
- Implemented the PDF Parsing & Metadata Extraction module (`pdf_parser/`).
- Parsing output verified in test mode: `data/processed/{category}/{doc_id}` contains `document.json`, `pages.json`, `metadata.json`, and `full_text.txt`.
- Fallback logic implemented (PyMuPDF -> pdfplumber).
- Quality checks and structured reporting generated in `reports/`.

## Current Status
We have completed **Document Ingestion, Chunking, Embeddings**, **Elasticsearch Indexing & QA**, **Qdrant Vector Indexing & QA**, **Hybrid Retrieval Engine**, the **Answer Engine (Prompt Builder, LLM Generation, Citation Verification, Faithfulness Validation)**, **Golden Set Generator**, the **Evaluation Framework**, the **FastAPI Service Layer**, and the **Streamlit Presentation Layer**.
The entire platform is now **fully containerized** using Docker Compose, strictly configured for **Production Deployment**, and fully mapped with **Enterprise Architecture Documentation** and a professional `README.md` for public open-source exposure.
The system is fully implemented end-to-end. The `evaluation` module executes 100 queries across the pipeline and dynamically measures Retrieval Accuracy, Faithfulness, Citation accuracy, and generates charts using Matplotlib.
The `api/` module successfully wraps all services in robust REST API endpoints.
The `ui/` module provides a professional enterprise frontend using Streamlit, relying strictly on the API layer.

## Pending Work
- Embedding Generation service.
- Elasticsearch and Qdrant setup and indexing.
- Hybrid Search engine.
- Citation Engine.
- LLM integration.
- Streamlit UI.
- Evaluation pipeline (Golden Set).
- Docker containerization.

## Current Goal
Awaiting next instructions. The next logical milestone is implementing the text chunking strategy.

## Important Constraints
- **Quality Standard:** Code must reflect a Senior Software Engineer level (10+ years experience).
- **Architecture:** Emphasize clean architecture, SOLID principles, and modularity.
- **Configurability:** No hardcoded values. Use environment variables and pydantic-settings.
- **Workflow:** Build module-by-module. Do not generate the entire project at once.

## Architecture Summary
The system is a containerized application utilizing FastAPI for the backend and Streamlit for the frontend. It employs a hybrid search architecture combining Elasticsearch (lexical search) and Qdrant (vector search). PostgreSQL manages application state, PyMuPDF (with pdfplumber fallback) handles document ingestion. The downloader and parser are standalone, modular packages following SOLID principles.

## Tech Stack
Python 3.10+, FastAPI, Streamlit, PyMuPDF, pdfplumber, Elasticsearch, Qdrant, PostgreSQL, Neo4j (Optional), Docker, requests, pydantic-settings.

## Note for Future AI Models
When continuing this project:
1. Read `PROJECT_GUIDE.md` for coding standards.
2. Read `TRACKER.md` to understand the current phase.
3. Read `DECISIONS.md` for architecture decisions.
4. The `corpus_downloader/` and `pdf_parser/` packages are complete and tested. Do not modify them unless fixing bugs.
5. Run modules with `--test-mode` to verify they work on the 5-document subset before full processing.
