# Architecture Document

## Project Overview
The Legal RAG (Retrieval-Augmented Generation) Platform is an enterprise-grade application designed to answer complex legal questions using a curated corpus of legal texts. It utilizes a hybrid retrieval mechanism to fetch the most relevant legal passages and employs a large language model (Gemini 3.5 Flash) to generate accurate, verifiable, and cited answers.

## Problem Statement
Legal professionals require highly accurate and strictly cited answers to legal queries. Traditional LLMs are prone to hallucination, inventing statutes, and providing uncited legal advice. The challenge is to build a robust architecture that forces the LLM to rely strictly on an authoritative corpus, retrieves the correct passages with high precision, and validates the output against the source documents.

## Technology Stack

### Backend
- **FastAPI**: Provides a high-performance, asynchronous REST API for the application.
- **Gemini 3.5 Flash**: Google's LLM used for high-speed, high-quality legal answer generation.
- **Prompt Builder**: Dynamically constructs secure prompts incorporating the user query and retrieved metadata to prevent prompt injection and hallucination.
- **Answer Generator**: Manages the LLM lifecycle, calls the provider, and logs latency and token metrics.
- **Response Parser**: Strictly parses and validates the LLM's JSON output against Pydantic schemas.

### Retrieval Pipeline
- **Embedding Generation**: Converts text chunks into 1024-dimensional dense vectors for semantic search.
- **BM25 Retrieval (Elasticsearch)**: Performs fast, exact-match keyword (lexical) search.
- **Dense Retrieval (Qdrant)**: Performs semantic vector similarity search.
- **Reciprocal Rank Fusion (RRF)**: Merges BM25 and Dense Retrieval results, re-ranking them to surface the most relevant chunks.
- **Top-k Selection**: Truncates the fused list to the top-k highest scoring excerpts for context injection.

### Frontend
- **Streamlit UI**: An interactive, professional web interface built with Streamlit.
- **Backend Communication**: Uses Python's `requests` library to communicate asynchronously with the FastAPI backend.

## Deployment
- **Backend**: Deployed on Render as a Dockerized FastAPI application.
- **Frontend**: Deployed on Streamlit Community Cloud.

## Application Flow

### Architecture Diagram

```ascii
     User Query
         |
    Streamlit UI
         | (HTTP POST /query)
      FastAPI
         |
   Hybrid Retriever
    |            |
  BM25         Dense Retrieval
 (ES)          (Qdrant)
    \            /
 Reciprocal Rank Fusion
         |
  Retrieved Chunks (with Text & Metadata)
         |
   Prompt Builder
         | (System Prompt + Context + Query)
  Gemini 3.5 Flash
         | (JSON String)
   Response Parser & Validator
         |
    JSON Response
         | (HTTP 200 OK)
    Streamlit UI
         |
     User Answer
```

### Component Explanation
1. **Streamlit UI**: Captures the user's question and sends it to the FastAPI backend. It receives the JSON response and renders the answer, citations, and metrics panels.
2. **FastAPI**: Acts as the entry point for the backend logic, routing the query to the RAG Service.
3. **Hybrid Retriever**: The core retrieval engine. It queries Elasticsearch (BM25) and Qdrant (Dense Vectors) simultaneously. 
4. **Reciprocal Rank Fusion**: Combines the lexical and semantic scores using RRF to produce a highly accurate ranked list of legal excerpts.
5. **Prompt Builder**: Injects the exact legal text and metadata (citation, document title, pages) into a structured prompt alongside strict hallucination-prevention instructions.
6. **Gemini 3.5 Flash**: The LLM reads the context and generates an answer strictly constrained by the prompt instructions.
7. **Response Parser**: Ensures the LLM output conforms to the required JSON schema, containing the answer, citations, confidence, and limitations.
8. **UI Rendering**: The JSON is sent back to the frontend, where it is beautifully formatted with metric badges and expandable citation panels.
