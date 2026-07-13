# Legal RAG Cloud Deployment Guide

This guide details the procedure for deploying the Legal RAG Platform to production cloud environments.

## Architecture Paradigm
The system is built on a split-tier architecture:
- **Frontend**: Streamlit. Best hosted on [Streamlit Community Cloud](https://streamlit.io/cloud).
- **Backend**: FastAPI. Best hosted on a container PaaS like [Render](https://render.com), [Fly.io](https://fly.io), or [Railway](https://railway.app).

---

## 1. Deploying the Backend (FastAPI)
We recommend deploying the backend first to establish the API host URL.

### Using Render
1. Connect your GitHub repository to Render and create a **New Web Service**.
2. **Environment**: Select `Docker`. Render will automatically detect `Dockerfile.api`.
3. **Configuration**: 
   - Root Directory: `.`
   - Build Command: Automatically managed by Docker.
4. **Environment Variables**: Open `deployment/backend.env.example` and copy the variables into Render's dashboard. Set `ENVIRONMENT=production`.
5. **Deploy**: Render will expose the service at `https://your-app.onrender.com`.

---

## 2. Deploying the Frontend (Streamlit)
Once the backend is live, deploy the UI.

### Using Streamlit Community Cloud
1. Log into Streamlit Cloud and click **New App**.
2. Select your repository and set the Main file path to `ui/app.py`.
3. Before clicking Deploy, click **Advanced Settings** and configure the Secrets.
4. Inject your variables from `deployment/frontend.env.example`.
   **CRITICAL**: Set `API_HOST` to the public URL of your Render backend.
5. **Deploy**: Streamlit will spin up the container and expose the UI.

---

## 3. Post-Deployment Validation
1. Verify `https://your-app.onrender.com/health` returns `{"status": "healthy"}`.
2. Load the Streamlit URL and check the Sidebar. The **Backend Status** should display as a green dot (`Online`).
3. Run an example query to ensure the system communicates flawlessly end-to-end.

---

## Rollback Procedures
If a new deployment breaks the API contract:
1. Revert the commit in `git`.
2. Both Render and Streamlit automatically redeploy on `main` branch updates.
3. If database schemas change, ensure you revert the `ELASTICSEARCH_INDEX` in the environment variables to the previous version.

## Common Issues
- **Backend Offline in UI**: The `API_HOST` environment variable is missing or incorrect. It must include `https://` and drop trailing slashes.
- **CORS Errors in Browser**: The backend `CORS_ORIGINS` does not contain the exact Streamlit URL.
- **Timeout during Retrieval**: The free tier of Render spins down after 15 minutes of inactivity. The first query might take 50 seconds while the container wakes up.
