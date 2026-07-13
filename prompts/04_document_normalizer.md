# Document Normalizer

## Objective
Sanitize the raw extracted text by resolving encoding anomalies, standardizing whitespace, and mapping regex-identified legal citations.

----------------------------------------------------

## Representative Prompt

```text
Objective: Implement the Document Normalizer module.

Requirements:
- Parse the output JSONs from the PDF Parser.
- Implement regex sanitization to remove excessive whitespace, newline artifacts, and OCR errors.
- Implement a citation standardization layer (e.g., ensuring "Sec. 162" maps consistently to "Section 162").
- Prepare the text for semantic chunking by preserving sentence cohesion.
- Save the normalized documents to `data/archives/normalized_docs.json`.
```

----------------------------------------------------

## Outcome
- Production-ready `document_normalizer/cleaner.py`.
- Generated clean, machine-readable datasets stripped of visual artifacts.

----------------------------------------------------

## Engineering Notes
- **Design Considerations:** Tokenizer efficiency drops when documents are littered with non-breaking spaces and newline artifacts. Normalization provides a clean bedrock for embeddings.
- **Review Steps:** Verified regex boundaries to ensure legitimate legal phrasing wasn't accidentally stripped.
- **Validation Approach:** Unit tests asserting that input strings containing common OCR errors mapped correctly to sanitized outputs.
