# Production Deployment

## Objective
Audit the repository for deployment readiness and configure environment boundaries for split-tier PaaS orchestration.

----------------------------------------------------

## Representative Prompt

```text
Objective: Prepare the Legal RAG Platform for production deployment.

Requirements:
- Scaffold `deployment/backend.env.example` and `deployment/frontend.env.example` separately.
- Audit `.gitignore` to ensure secrets or local `.env` variables cannot leak.
- Inject `CORSMiddleware` into the FastAPI application to allow Cross-Origin queries from a separately hosted UI domain.
- Create a definitive `deployment_checklist.md` covering pre-flight security metrics.
- Produce `reports/deployment_validation.json` proving readiness.
```

----------------------------------------------------

## Outcome
- Secured the repository for public Git syncing.
- Configured FastAPI to accept public web traffic natively without CORS friction.

----------------------------------------------------

## Engineering Notes
- **Design Considerations:** Utilizing separate deployment profiles for Streamlit and FastAPI acknowledges the reality of scaling: APIs scale horizontally behind load balancers, whereas Streamlit typically scales via memory allocation.
- **Review Steps:** Verified the `CORS_ORIGINS` logic inside `app.py` properly defaulted to the `*` permissive state while allowing restriction in production.
- **Validation Approach:** The internal `.gitignore` validation sequence confirmed that data artifacts (`data/raw/`) would never be accidentally uploaded to public servers.
