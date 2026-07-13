# Production Deployment Steps

## Hosting Strategy Recommendations

### Backend: Render
**Recommendation: Render**
**Why:** Render offers native Python Web Service deployments directly from GitHub. It seamlessly reads the `Procfile` and `requirements.txt`, automatically handles dependency installation, and exposes a public HTTPS endpoint. Unlike Fly.io which requires writing internal `fly.toml` files and handling Docker routing, Render manages the entire networking stack natively. We have supplied `runtime.txt` to lock Python 3.10.11.

### Frontend: Streamlit Community Cloud
**Recommendation: Streamlit Community Cloud**
**Why:** Streamlit provides a dedicated, free-tier managed cloud environment specifically designed to host Streamlit applications. It hooks directly into your GitHub repository and automatically deploys the UI. Render Static does not support Python runtimes for Streamlit, and Vercel is optimized for Next.js, making Streamlit Cloud the definitive choice.

---

## Deployment Instructions

### 1. Backend Deployment (Render)
1. Navigate to [Render Dashboard](https://dashboard.render.com).
2. Click **New +** -> **Web Service**.
3. Connect your GitHub account and select your `ShorthillsAI-Legal-RAG` repository.
4. **Configuration:**
   - **Name:** `shorthills-api`
   - **Runtime:** Python
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn api.app:app --host 0.0.0.0 --port $PORT`
5. **Environment Variables:**
   - Add all keys present in `deployment/backend.env.example` (e.g., `OPENAI_API_KEY`, `ELASTICSEARCH_URL`).
   - Set `CORS_ORIGINS` to `*` temporarily, and update it to your Streamlit Cloud URL later.
6. Click **Deploy Web Service**. Render will return a public URL (e.g., `https://shorthills-api.onrender.com`).

### 2. Frontend Deployment (Streamlit Cloud)
1. Navigate to [Streamlit Community Cloud](https://share.streamlit.io).
2. Click **New app** -> **Deploy a public app from GitHub**.
3. **Configuration:**
   - **Repository:** `<your-github-username>/ShorthillsAI-Legal-RAG`
   - **Branch:** `main`
   - **Main file path:** `ui/app.py`
4. **Environment Variables:**
   - Click "Advanced settings...".
   - Enter your variables (specifically defining `API_BASE_URL` to point to the Render URL you just generated).
5. Click **Deploy**.

### 3. Health Verification
- **API Check:** Navigate to `https://shorthills-api.onrender.com/health`. You should receive `{"status": "healthy"}`.
- **UI Check:** Navigate to your Streamlit app URL and execute a test query. Ensure the answer traces complete successfully.

### 4. Troubleshooting
- **CORS Errors:** If Streamlit fails to fetch data, ensure the Render backend environment variable `CORS_ORIGINS` explicitly allows the Streamlit domain.
- **Memory Errors on Render:** The Free tier of Render has 512MB of RAM. If you are using the Mock Providers (which load thousands of vectors into memory), the app will crash. **You MUST use real external Elasticsearch and Qdrant clusters (like Elastic Cloud and Qdrant Cloud) in production to avoid OOM crashes.**
