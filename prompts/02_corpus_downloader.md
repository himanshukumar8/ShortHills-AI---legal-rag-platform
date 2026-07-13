# Corpus Downloader

## Objective
Build the asynchronous fetching mechanism responsible for safely acquiring raw legal PDFs based on the manifest definitions.

----------------------------------------------------

## Representative Prompt

```text
Objective: Implement the Corpus Downloader module.

Requirements:
- Parse `data/raw/manifest.json`.
- Implement asynchronous HTTP fetching using `aiohttp` to maximize throughput.
- Enforce strict error handling for HTTP timeouts and 404s.
- Avoid duplicate downloads by checking file hashes or existing local files.
- Store downloaded PDFs in `data/raw/`.
- Provide structured logging detailing download success, failure, and execution time.
```

----------------------------------------------------

## Outcome
- Production-ready `corpus_downloader/` module containing `fetcher.py` and `validator.py`.
- Validation script confirming successful PDF retrieval.

----------------------------------------------------

## Engineering Notes
- **Design Considerations:** Synchronous downloads bottleneck pipeline execution; `aiohttp` was chosen for concurrent I/O performance.
- **Review Steps:** Ensured exponential backoff logic was present to respect external server rate limits.
- **Validation Approach:** Executed a mock download sequence to verify hash integrity and duplicate skipping logic.
