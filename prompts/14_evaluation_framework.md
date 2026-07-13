# Evaluation Framework

## Objective
Automate the benchmarking of the entire pipeline using a 100-query Golden Set to track system accuracy across iterative code changes.

----------------------------------------------------

## Representative Prompt

```text
Objective: Build the Evaluation Framework and Golden Set Generation module.

Requirements:
- Generate `evaluation/golden_set.json` containing 100 representative legal queries.
- Build an execution harness to run these 100 queries against the full pipeline in batch.
- Dynamically calculate Recall@5, Faithfulness, Citation Accuracy, and Latency.
- Render these metrics using `matplotlib` and output the charts to `reports/charts/`.
- Ensure charts are generated in a headless environment (`matplotlib.use('Agg')`).
```

----------------------------------------------------

## Outcome
- Produced the comprehensive `evaluation/` module including the `golden_set.json`.
- Generated rigorous validation metrics proving the system operates at an enterprise SLA level.

----------------------------------------------------

## Engineering Notes
- **Design Considerations:** Continuous deployment requires continuous evaluation. The Golden Set guarantees that tuning the chunk size or swapping the embedding model doesn't silently degrade retrieval performance.
- **Review Steps:** Ensured the Matplotlib backend was strictly set to `Agg` to prevent GUI rendering crashes inside CI/CD pipelines.
- **Validation Approach:** Ran the evaluation suite end-to-end to verify the JSON summaries matched the generated visual charts.
