# Legal RAG API Documentation

The Legal RAG backend is built on **FastAPI** to provide production-grade REST APIs over the core retrieval and answer engines. 

## Endpoints

### 1. `GET /health`
Returns the application health status.
**Request:**
```bash
curl -X 'GET' 'http://localhost:8000/health' -H 'accept: application/json'
```
**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

### 2. `GET /metrics`
Returns high-level runtime request metrics tracked via the custom `TimingMiddleware`.
**Request:**
```bash
curl -X 'GET' 'http://localhost:8000/metrics' -H 'accept: application/json'
```
**Response:**
```json
{
  "total_requests": 42,
  "error_rate": 0.0,
  "average_latency_s": 0.015
}
```

### 3. `POST /query`
Executes an end-to-end Legal RAG query. This retrieves context using the Hybrid Engine, builds the prompt, generates an answer, and validates citations and faithfulness.
**Request:**
```bash
curl -X 'POST' \
  'http://localhost:8000/query' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "query": "What are the rules for independent contractors under IRS Section 162?"
}'
```
**Response:**
```json
{
  "answer": "According to Section 162, independent contractors...",
  "citations": [
    {
      "document": "IRS Publication 15",
      "page": 12,
      "section": "Independent Contractors",
      "status": "VERIFIED",
      "confidence": 0.95,
      "message": "Citation accurately reflects source material."
    }
  ],
  "confidence": "HIGH",
  "limitations": "Does not constitute official tax advice.",
  "retrieval_trace": {
    "total_latency": 0.452,
    "es_candidate_count": 50,
    "qdrant_candidate_count": 50,
    "results": [...]
  }
}
```

### 4. `POST /evaluate`
Executes the evaluation framework over the Golden Set and returns the summary metrics.
**Request:**
```bash
curl -X 'POST' 'http://localhost:8000/evaluate' -H 'accept: application/json' -d ''
```
**Response:**
```json
{
  "Top-1 Accuracy": 0.85,
  "Recall@5": 0.92,
  "Average Faithfulness": 0.95,
  "Citation Accuracy": 0.98
}
```

## OpenAPI
You can access the automated OpenAPI documentation by running the server and navigating to:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
