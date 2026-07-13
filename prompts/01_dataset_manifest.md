# Dataset Manifest

## Objective
Establish the core structural requirements for the raw legal corpus, defining the target documents and metadata schemas required before ingestion begins.

----------------------------------------------------

## Representative Prompt

```text
Objective: Construct the Dataset Manifest module for the Legal RAG platform.

Requirements:
- Define a strict JSON schema for the dataset configuration.
- Target U.S. Tax codes, IRS Publications, and Court Judgments.
- Ensure the manifest tracks document title, source URL, structural hierarchy (Act, Chapter, Section), and expected token volumes.
- Output the finalized manifest to `data/raw/manifest.json`.
- Do NOT begin downloading files. This module strictly defines the expected corpus.
```

----------------------------------------------------

## Outcome
- Generated a strictly typed Pydantic configuration file defining the expected corpus.
- Produced `manifest.json` ensuring deterministic behavior for subsequent pipeline stages.

----------------------------------------------------

## Engineering Notes
- **Design Considerations:** A static manifest guarantees reproducibility and prevents the downloader from continuously crawling unknown domains.
- **Review Steps:** Verified the URLs pointed to legitimate governmental repositories (.gov).
- **Validation Approach:** Ensured the JSON schema matched the internal Python dataclass structure.
