from __future__ import annotations

import json
import logging
import csv
import math
import statistics
from collections import defaultdict
from pathlib import Path

# Configure basic logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")
logger = logging.getLogger("chunk_qa")

def run_qa(chunks_dir: Path = Path("data/chunks"), reports_prefix: str = "chunk"):
    reports_dir = Path("reports")
    reports_dir.mkdir(parents=True, exist_ok=True)
    
    if not chunks_dir.exists():
        logger.error(f"Chunks directory not found: {chunks_dir}")
        return
        
    all_chunks = []
    
    # 1. Load all chunks
    logger.info("Loading chunks from disk...")
    for category_dir in chunks_dir.iterdir():
        if category_dir.is_dir():
            for doc_dir in category_dir.iterdir():
                if doc_dir.is_dir():
                    chunks_file = doc_dir / "chunks.json"
                    if chunks_file.exists():
                        with open(chunks_file, "r", encoding="utf-8") as f:
                            doc_chunks = json.load(f)
                            all_chunks.extend(doc_chunks)
                            
    total_chunks = len(all_chunks)
    logger.info(f"Loaded {total_chunks} total chunks.")
    
    if total_chunks == 0:
        logger.error("No chunks to analyze.")
        return
        
    # 2. Gather metrics
    category_counts = defaultdict(int)
    document_counts = defaultdict(int)
    token_counts = []
    
    empty_chunks = []
    tiny_chunks = [] # < 20 tokens
    oversized_chunks = [] # > 2000 tokens
    duplicate_hashes = set()
    seen_hashes = set()
    
    missing_citations = []
    missing_page_refs = []
    orphan_chunks = [] # no parent doc id
    
    for c in all_chunks:
        category_counts[c.get("category", "Unknown")] += 1
        doc_id = c.get("parent_document_id")
        if doc_id:
            document_counts[doc_id] += 1
        else:
            orphan_chunks.append(c["chunk_id"])
            
        tokens = c.get("token_estimate", 0)
        token_counts.append(tokens)
        
        text = c.get("text", "")
        if not text.strip():
            empty_chunks.append(c["chunk_id"])
        elif tokens < 20:
            tiny_chunks.append(c["chunk_id"])
        elif tokens > 2000:
            oversized_chunks.append(c["chunk_id"])
            
        chash = c.get("chunk_hash")
        if chash in seen_hashes:
            duplicate_hashes.add(chash)
        else:
            seen_hashes.add(chash)
            
        if not c.get("citation"):
            missing_citations.append(c["chunk_id"])
            
        if c.get("page_start") is None or c.get("page_start") == 0:
            missing_page_refs.append(c["chunk_id"])
            
    # 3. Calculate statistics
    avg_tokens = statistics.mean(token_counts)
    median_tokens = statistics.median(token_counts)
    min_tokens = min(token_counts)
    max_tokens = max(token_counts)
    
    sorted_tokens = sorted(token_counts)
    p25 = sorted_tokens[int(len(sorted_tokens) * 0.25)]
    p75 = sorted_tokens[int(len(sorted_tokens) * 0.75)]
    p90 = sorted_tokens[int(len(sorted_tokens) * 0.90)]
    p99 = sorted_tokens[int(len(sorted_tokens) * 0.99)]
    
    # 4. Generate Chunk Quality Score (0-100)
    score = 100
    deductions = []
    
    if empty_chunks:
        deductions.append(f"-{min(20, len(empty_chunks))} for empty chunks")
        score -= min(20, len(empty_chunks))
        
    oversized_penalty = min(30, (len(oversized_chunks) / total_chunks) * 500)
    if oversized_penalty > 0:
        deductions.append(f"-{round(oversized_penalty)} for oversized chunks (>2000 tokens)")
        score -= oversized_penalty
        
    tiny_penalty = min(20, (len(tiny_chunks) / total_chunks) * 100)
    if tiny_penalty > 0:
        deductions.append(f"-{round(tiny_penalty)} for tiny chunks (<20 tokens)")
        score -= tiny_penalty
        
    duplicate_penalty = min(15, (len(duplicate_hashes) / total_chunks) * 100)
    if duplicate_penalty > 0:
        deductions.append(f"-{round(duplicate_penalty)} for duplicate hashes")
        score -= duplicate_penalty
        
    if missing_page_refs:
        deductions.append("-10 for missing page references")
        score -= 10
        
    if orphan_chunks:
        deductions.append("-20 for orphan chunks")
        score -= 20
        
    score = max(0, round(score))
    
    # Improvements
    improvements = []
    if oversized_chunks:
        improvements.append("Refine regex boundary in chunk_builder.py to prevent oversized chunks (e.g., implement a recursive sub-splitter for sections > 2000 tokens).")
    if tiny_chunks:
        improvements.append("Implement chunk merging (coalescing) to combine tiny chunks (<20 tokens) with their previous sibling to preserve LLM context.")
    if missing_citations:
        improvements.append("Ensure `citation` field is deeply propagated during hierarchy tracking, even for isolated paragraphs.")
        
    # 5. Write JSON Summary
    summary = {
        "quality_score": score,
        "score_deductions": deductions,
        "recommended_improvements": improvements,
        "global_metrics": {
            "total_chunks": total_chunks,
            "total_documents": len(document_counts),
            "total_categories": len(category_counts),
        },
        "token_distribution": {
            "average": round(avg_tokens, 2),
            "median": median_tokens,
            "min": min_tokens,
            "max": max_tokens,
            "p25": p25,
            "p75": p75,
            "p90": p90,
            "p99": p99
        },
        "quality_issues": {
            "empty_chunks": len(empty_chunks),
            "tiny_chunks": len(tiny_chunks),
            "oversized_chunks": len(oversized_chunks),
            "duplicate_hashes": len(duplicate_hashes),
            "missing_citations": len(missing_citations),
            "missing_page_references": len(missing_page_refs),
            "orphan_chunks": len(orphan_chunks)
        },
        "category_breakdown": category_counts
    }
    
    summary_path = reports_dir / f"{reports_prefix}_quality_summary.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=4)
    logger.info(f"Wrote {summary_path}")
    
    # 6. Write CSV Report
    csv_path = reports_dir / f"{reports_prefix}_quality_report.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Issue Type", "Count", "Sample IDs (up to 5)"])
        writer.writerow(["Empty Chunks", len(empty_chunks), ", ".join(empty_chunks[:5])])
        writer.writerow(["Tiny Chunks (<20t)", len(tiny_chunks), ", ".join(tiny_chunks[:5])])
        writer.writerow(["Oversized Chunks (>2000t)", len(oversized_chunks), ", ".join(oversized_chunks[:5])])
        writer.writerow(["Missing Citations", len(missing_citations), ", ".join(missing_citations[:5])])
        writer.writerow(["Missing Page Refs", len(missing_page_refs), ", ".join(missing_page_refs[:5])])
        writer.writerow(["Orphan Chunks", len(orphan_chunks), ", ".join(orphan_chunks[:5])])
    logger.info(f"Wrote {csv_path}")
    
    # 7. Generate ASCII Histogram
    print("\nToken Size Distribution Histogram:")
    bins = [0, 100, 250, 500, 1000, 2000, 5000, max_tokens]
    hist = [0] * (len(bins) - 1)
    for t in token_counts:
        for i in range(len(bins)-1):
            if bins[i] <= t < bins[i+1]:
                hist[i] += 1
                break
        if t == max_tokens:
            hist[-1] += 1
            
    max_hist = max(hist) if hist else 1
    for i in range(len(bins)-1):
        bar_len = int((hist[i] / max_hist) * 40)
        bar = "=" * bar_len
        print(f"{bins[i]:>4} - {bins[i+1]:>4} | {hist[i]:>5} | {bar}")
        
    return score

if __name__ == "__main__":
    import sys
    d = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("data/chunks")
    p = sys.argv[2] if len(sys.argv) > 2 else "chunk"
    run_qa(d, p)
