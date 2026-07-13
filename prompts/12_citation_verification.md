# Citation Verification

## Objective
Implement deterministic logic to prove every LLM-generated citation maps explicitly to an underlying retrieved document.

----------------------------------------------------

## Representative Prompt

```text
Objective: Build the Citation Verification Engine.

Requirements:
- Parse the structured JSON citations produced by the LLM.
- Cross-reference each citation against the metadata of the retrieved context chunks.
- Score the citation accuracy based on whether the referenced document ID and section actually exist in the retrieved subset.
- Output a deterministic verification payload (e.g., FAILED, PARTIAL, PASSED).
- Do NOT call an LLM to perform this verification. It must be programmatic.
```

----------------------------------------------------

## Outcome
- Delivered `answer_engine/citation_engine.py` to cryptographically verify LLM claims against the database.
- Generated the verification badges (Green/Red) utilized heavily by the Streamlit frontend.

----------------------------------------------------

## Engineering Notes
- **Design Considerations:** Using an LLM to verify another LLM's citations introduces circular hallucination risks. Programmatic, strict-string matching ensures deterministic accountability.
- **Review Steps:** Verified the parsing regex could handle slight variations in LLM citation syntax without falsely flagging correct citations as failures.
- **Validation Approach:** Injected deliberate fake citations into the pipeline to assert the engine correctly flagged them as `FAILED`.
