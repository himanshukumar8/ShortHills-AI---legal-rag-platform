# Repository Pre-Release Checklist

## 1. Secrets & Security
- [x] `.env` files are ignored and excluded.
- [x] No `OPENAI_API_KEY` or `ANTHROPIC_API_KEY` hardcoded in source code.
- [x] No plaintext passwords or internal IP addresses committed.
- [x] `deployment/backend.env.example` successfully sanitizes secret values.

## 2. `.gitignore` Verification
- [x] Python artifacts (`__pycache__`, `.venv`, `.pyc`) are excluded.
- [x] Developer IDE configs (`.vscode`, `.idea`) are excluded.
- [x] Data directories (`data/raw/`, `data/embeddings/`) are explicitly excluded. *Justification*: Legal corpora are massive and can bloat repository history beyond GitHub's 1GB limit. Embeddings and pre-chunked datasets should be regenerated locally by users or downloaded from an external S3 bucket, not pushed to `git`.

## 3. Repository Hygiene
- [x] No `debug_print()` scattered randomly in production code.
- [x] No active `FIXME` or `HACK` comments discovered.
- [ ] *Action Required*: Several testing scripts (`test_api.py`, `test_ui_client.py`, `generate_diagrams.py`) sit in the root directory. They should ideally be moved to `tests/` or `scripts/` to maintain root cleanliness.
- [ ] *Action Required*: The `README.md` still contains explicit `TODO` markers for missing Streamlit UI screenshots.

## 4. Configuration
- [x] Environment variables define external database connections (Elasticsearch/Qdrant).
- [x] Fallback "Mock" providers are correctly segregated and do not accidentally deploy in production profiles.
- [x] CORS origins in `app.py` correctly draw from the `.env` configuration.

## 5. Dependencies
- [x] `requirements.txt` is strictly typed and version-pinned where necessary.
- [x] Unused packages are absent.

## 6. Submission Documentation
- [x] README.md is present and enterprise-grade.
- [x] Architecture diagrams (`docs/architecture.*`) are populated.
- [x] The `prompts/` collection is populated with 19 representative execution samples.
- [x] The `submission/Assignment_Report.md` exists and meets hiring committee standards.
