# Legal RAG Platform - Interview Assignment Submission

## Project Summary
This project is an enterprise-grade Legal Retrieval-Augmented Generation (RAG) platform. It provides high-accuracy, verifiable answers to legal queries by performing hybrid retrieval across a comprehensive Indian legal corpus (GST, Tax, Constitution, IPC, CrPC, etc.) and leveraging Google's Gemini 3.5 Flash LLM. Built to eliminate AI hallucinations, the platform forces strict citation of retrieved context and enforces a rigid JSON schema for verifiable UI presentation.

## Features
- **Hybrid Retrieval**: Combines BM25 lexical search (via Elasticsearch) and Dense Vector semantic search (via Qdrant) using Reciprocal Rank Fusion (RRF).
- **Hallucination Prevention**: Prompt engineering strictly confines the LLM to retrieved context and enforces citation matching.
- **Answer Engine**: Provides LLM Answer Generation, Citation Engine Verification, and Faithfulness Validation metrics.
- **RESTful API**: Fast and asynchronous FastAPI backend routing.
- **Professional UI**: A fully-featured Streamlit frontend displaying answers, detailed citations, and retrieval latency metrics.

## Tech Stack
- **Backend**: Python 3.12, FastAPI, Uvicorn, Pydantic
- **LLM**: Google Gemini 3.5 Flash (via `google-genai` SDK)
- **Retrieval**: Mock architectures ready to interface with Elasticsearch and Qdrant
- **Frontend**: Streamlit
- **Environment**: Docker, Docker Compose

## Deployment Links
- **GitHub Repository**: [Placeholder for GitHub Repo URL]
- **Backend URL**: [Placeholder for Render Backend URL]
- **Frontend URL**: [Placeholder for Streamlit Frontend URL]

## Folder Structure
```text
├── api/                     # FastAPI Service Layer
├── answer_engine/           # LLM Prompting, Generation, and Validation logic
├── hybrid_retriever/        # BM25, Dense Vector, and RRF retrieval logic
├── ui/                      # Streamlit Frontend application
├── evaluation/              # Automated Golden Set benchmarking suite
├── data/                    # Corpus storage (PDFs, parsed metadata, optimized chunks)
├── Assignment/              # Submission documents (Prompts, Architecture, Dataset)
└── docker-compose.yml       # Containerization configurations
```

## Future Improvements
1. **Live Database Integration**: Transition from the in-memory mock environment back to dedicated, high-availability Elasticsearch and Qdrant clusters.
2. **Advanced Chunking**: Implement semantic chunking strategies to preserve complex legal clause boundaries better than fixed-token windowing.
3. **Multi-turn Conversation**: Expand the Answer Engine to handle follow-up legal queries while preserving session context.
4. **Enhanced Faithfulness Checking**: Implement an LLM-as-a-judge secondary verification step to actively cross-verify the primary LLM's citations against the retrieved text.
