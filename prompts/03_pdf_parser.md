# PDF Parser

## Objective
Extract textual data from complex legal PDFs while preserving critical hierarchical layout boundaries, such as headers, sections, and paragraphs.

----------------------------------------------------

## Representative Prompt

```text
Objective: Implement the PDF Parser module.

Requirements:
- Utilize `PyMuPDF` (fitz) to extract text from raw PDFs located in `data/raw/`.
- Ensure the extraction logic preserves physical layout and text blocks.
- Detect and tag structural elements (e.g., distinguishing a bold 'Section 1.0' from body text).
- Output the extracted, hierarchically structured data to JSON format in `data/archives/`.
- Produce a `validation.py` script to confirm structural integrity against known legal patterns.
```

----------------------------------------------------

## Outcome
- Implementation of `pdf_parser/extractor.py` and structural validation rules.
- High-fidelity text extraction that maps spatial blocks to logical paragraphs.

----------------------------------------------------

## Engineering Notes
- **Design Considerations:** Legal documents rely heavily on formatting to convey meaning. Standard `PyPDF2` destroys layout; hence `PyMuPDF` was selected for block-level spatial extraction.
- **Review Steps:** Manually verified parsed JSON output against visual PDF structures to ensure footnotes and margins didn't corrupt the main body text.
- **Validation Approach:** The validation script checked for continuous block extraction without arbitrary sentence breakage.
