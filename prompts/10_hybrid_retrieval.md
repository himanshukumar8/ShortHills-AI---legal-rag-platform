# Hybrid Retrieval

## Objective
Fuse Elasticsearch (keyword) and Qdrant (vector) results mathematically to eliminate the blind spots of individual search methods.

----------------------------------------------------

## Representative Prompt

```text
Objective: Construct the Hybrid Retrieval Engine.

Requirements:
- Accept a user query and process it through the embedding model.
- Execute asynchronous, parallel searches against both Elasticsearch and Qdrant.
- Apply Reciprocal Rank Fusion (RRF) to merge the candidate lists without requiring score normalization.
- Apply metadata filters (e.g., by domain or year).
- Verify exact citations and return the highly ranked, deduplicated Top-K chunks.
```

----------------------------------------------------

## Outcome
- Delivered `hybrid_retriever/` module featuring RRF fusion and concurrency.
- Created the definitive "Retrieval" pipeline utilized by the Answer Engine.

----------------------------------------------------

## Engineering Notes
- **Design Considerations:** BM25 returns scores from 0-to-infinity based on term frequency. Vectors return Cosine scores from 0-to-1. Direct addition is mathematically invalid. RRF was implemented to rank candidates strictly based on their relative positional ordering in both lists.
- **Review Steps:** Ensured parallel `asyncio.gather` execution to prevent retrieval latency from doubling.
- **Validation Approach:** Confirmed that a chunk ranked #1 in both DBs bubbled immediately to the top of the final candidate list.
