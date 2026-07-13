# Dataset Manifest

This directory contains the definitive curated dataset manifest for the Legal AI Search System.
The manifest represents exactly 100 foundational U.S. tax and legal documents required for the hybrid search and citation system.

## Files

- `dataset_manifest.csv`: The dataset manifest in comma-separated values format for easy viewing and spreadsheet processing.
- `dataset_manifest.json`: The dataset manifest in structured JSON format, ideal for programmatic ingestion by the corpus downloader and database seeders.

## Field Dictionary

Every record in the manifest contains the following fields:

| Field Name | Type | Description |
| :--- | :--- | :--- |
| **document_id** | String | A unique alphanumeric identifier for the document (e.g., ACT-01, IRS-12). Used as the primary key. |
| **title** | String | The official title of the legal document, statute, or publication. |
| **category** | String | The document classification. Must be one of: `Acts / Statutes`, `Court Judgments`, `IRS Publications`, `Treasury Regs`, `Legal Commentary`. |
| **source_name** | String | The name of the authoritative issuing body or publisher (e.g., Congress.gov, IRS.gov, Supreme Court). |
| **source_url** | String | The web URL where the document was originally published or referenced. |
| **pdf_url** | String | The direct URL to the machine-readable PDF file. Used by the Corpus Downloader. |
| **publication_year** | Integer | The year the document was originally published, enacted, or decided. |
| **estimated_pages** | Integer | The approximate length of the document. Helps in planning chunking capacity. |
| **document_status** | String | The ingestion state of the document. Initializes as `NOT_DOWNLOADED`. Will be updated by the downloader to `DOWNLOADED` or `FAILED`. |
| **local_file_path** | String | The relative or absolute path where the downloaded PDF is stored locally. Empty until downloaded. |
| **checksum** | String | An SHA-256 hash of the downloaded PDF to ensure file integrity. Empty until downloaded. |
| **notes** | String | Editorial justification for why this specific document is included in the AI's knowledge base. |
