# Production Pre-Flight Checklist

## 1. Secrets & Environment
- [ ] `.env` files are NOT committed to version control.
- [ ] `deployment/backend.env.example` has been transferred to the production secret manager.
- [ ] Production API keys (OpenAI/Anthropic) have been injected into the PaaS environment variables.
- [ ] `CORS_ORIGINS` strictly specifies the deployed Streamlit public URL (no wildcards `*`).

## 2. Infrastructure
- [ ] Elasticsearch cluster is provisioned and securely accessible via HTTPS.
- [ ] Qdrant cluster is provisioned and securely accessible via HTTPS.
- [ ] The `legal_corpus_v1` and `legal_vectors_v1` databases have been successfully indexed.

## 3. API Backend (FastAPI)
- [ ] Backend is deployed behind a secure HTTPS load balancer.
- [ ] `GET /health` returns `200 OK`.
- [ ] Global exception handlers mask internal stack traces from the end user.
- [ ] FastAPI `docs` (Swagger) is disabled or secured (if strictly internal).

## 4. UI Frontend (Streamlit)
- [ ] Streamlit is deployed to Community Cloud (or another container runtime).
- [ ] `API_HOST` is correctly pointing to the production FastAPI endpoint (e.g., `https://my-backend.onrender.com`).
- [ ] Attempting a query returns results cleanly without CORS policy violations.

## 5. Fallbacks
- [ ] The backend handles provider rate-limits cleanly (Tenacity backoff).
- [ ] The UI gracefully degrades if the backend is offline ("Backend Offline" message rather than Python crash).
