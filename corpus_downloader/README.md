# Corpus Download Pipeline

A production-grade module for downloading, validating, and cataloguing the 100 curated U.S. tax and legal PDF documents defined in `data/manifest/dataset_manifest.csv`.

## Architecture

```text
corpus_downloader/
├── __init__.py              # Package exports
├── __main__.py              # CLI entry point (python -m corpus_downloader)
├── config.py                # Centralized configuration (pydantic-settings)
├── models.py                # Domain dataclasses and enums
├── exceptions.py            # Custom exception hierarchy
├── manifest_reader.py       # CSV → list[DocumentRecord]
├── manifest_updater.py      # Merges results back into CSV
├── downloader.py            # Single-attempt HTTP download with streaming
├── validator.py             # Multi-layer PDF validation (PyMuPDF)
├── hash_generator.py        # Streaming SHA-256 checksum
├── duplicate_detector.py    # Thread-safe cross-document duplicate detection
├── reporter.py              # CSV detail + JSON summary report generation
├── utils.py                 # Category mapping, filename sanitization
├── main.py                  # Pipeline orchestrator (ThreadPoolExecutor)
└── README.md                # This file
```

### Module Responsibilities

| Module | Single Responsibility |
|---|---|
| `config.py` | Load and validate all configuration from env / `.env` |
| `models.py` | Define `DocumentRecord`, `DownloadResult`, `ValidationResult`, enums |
| `exceptions.py` | Custom exception hierarchy for granular error handling |
| `manifest_reader.py` | Read and validate the CSV manifest schema |
| `downloader.py` | Perform a single HTTP download attempt with streaming |
| `validator.py` | Validate PDF existence, magic bytes, corruption, encryption, pages |
| `hash_generator.py` | Compute SHA-256 checksums via streaming reads |
| `duplicate_detector.py` | Detect cross-document file duplicates by checksum |
| `manifest_updater.py` | Merge download results back into the manifest CSV |
| `reporter.py` | Generate per-document CSV and aggregate JSON reports |
| `utils.py` | Category→folder mapping, filename sanitization, directory creation |
| `main.py` | Orchestrate the full pipeline with concurrency and retries |

## How to Run

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure (Optional)

Copy `.env.example` to `.env` and adjust any values:

```bash
cp .env.example .env
```

All configuration defaults are sensible for local development. No `.env` file is required for default behavior.

### 3. Test Mode (5 Documents)

Run the pipeline with only one document per category:

```bash
python -m corpus_downloader --test-mode
```

### 4. Full Run (100 Documents)

```bash
python -m corpus_downloader
```

## Configuration Reference

All values are configurable via environment variables prefixed with `DOWNLOADER_`:

| Variable | Default | Description |
|---|---|---|
| `DOWNLOADER_MANIFEST_PATH` | `data/manifest/dataset_manifest.csv` | Path to the manifest file |
| `DOWNLOADER_DOWNLOAD_DIR` | `data/raw` | Base directory for downloaded PDFs |
| `DOWNLOADER_LOG_DIR` | `logs` | Directory for log files |
| `DOWNLOADER_REPORT_DIR` | `reports` | Directory for report files |
| `DOWNLOADER_TIMEOUT_SECONDS` | `120` | HTTP request timeout |
| `DOWNLOADER_MAX_RETRIES` | `3` | Maximum download retry attempts |
| `DOWNLOADER_REQUEST_DELAY_SECONDS` | `2.0` | Delay between requests (rate limiting) |
| `DOWNLOADER_VERIFY_SSL` | `true` | Whether to verify SSL certificates |
| `DOWNLOADER_USER_AGENT` | `LegalAISearchSystem/1.0 (...)` | HTTP User-Agent header |
| `DOWNLOADER_MAX_WORKERS` | `3` | Concurrent download threads |
| `DOWNLOADER_TEST_MODE` | `false` | Enable test mode |
| `DOWNLOADER_STREAM_CHUNK_SIZE` | `65536` | Streaming read chunk size (bytes) |

## Output Structure

### Downloaded Files

```text
data/raw/
├── acts/                  # Acts / Statutes
├── court_judgments/        # Court Judgments
├── irs_publications/      # IRS Publications
├── regulations/           # Treasury Regs
└── commentary/            # Legal Commentary
```

### Reports

```text
reports/
├── download_report.csv     # Per-document detail (status, pages, size, errors)
└── download_summary.json   # Aggregate stats (totals, averages, timing)
```

### Logs

```text
logs/
└── downloader.log          # Rotating log file (10 MB max, 3 backups)
```

## Design Decisions

1. **Manual retries in the orchestrator** instead of urllib3 automatic retries — gives full control over logging each attempt and counting.
2. **ThreadPoolExecutor** over asyncio — simpler for 100 documents, easier to debug.
3. **Streaming SHA-256** — the IRC (Title 26) is 4000+ pages; cannot load entirely into memory.
4. **CSV as source of truth** — the manifest CSV is read, updated, and written back by the pipeline.
5. **One failure never kills the pipeline** — each document is processed independently.
