import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pathlib import Path
from typing import List
from evaluation.models import TraceResult
from collections import Counter

def generate_charts(traces: List[TraceResult], output_dir: Path):
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 1. Accuracy by Category
    categories = {}
    for t in traces:
        cat = t.golden_query.category
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(t.metrics.top_1_accuracy)
        
    cats = list(categories.keys())
    accs = [sum(categories[c])/len(categories[c]) * 100 for c in cats]
    
    plt.figure(figsize=(10, 6))
    plt.bar(cats, accs, color="steelblue")
    plt.title("Top-1 Accuracy by Category")
    plt.ylabel("Accuracy (%)")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(output_dir / "accuracy_by_category.png")
    plt.close()
    
    # 2. Latency Distribution
    latencies = [t.metrics.total_time_ms for t in traces if t.metrics.success]
    plt.figure(figsize=(10, 6))
    plt.hist(latencies, bins=20, color="blue", alpha=0.7)
    plt.title("End-to-End Latency Distribution")
    plt.xlabel("Latency (ms)")
    plt.ylabel("Frequency")
    plt.tight_layout()
    plt.savefig(output_dir / "latency_distribution.png")
    plt.close()
    
    # 3. Failure Distribution
    failures = [t.metrics.error_category for t in traces if t.metrics.error_category]
    if failures:
        counts = Counter(failures)
        plt.figure(figsize=(10, 6))
        plt.barh(list(counts.keys()), list(counts.values()), color="salmon")
        plt.title("Failure Distribution by Category")
        plt.xlabel("Count")
        plt.tight_layout()
        plt.savefig(output_dir / "failure_distribution.png")
        plt.close()
        
    # 4. Faithfulness Distribution
    faith = [t.metrics.faithfulness_score for t in traces if t.metrics.success]
    plt.figure(figsize=(10, 6))
    plt.hist(faith, bins=10, color="green", alpha=0.7)
    plt.title("Faithfulness Score Distribution")
    plt.xlabel("Faithfulness (0-1)")
    plt.ylabel("Frequency")
    plt.tight_layout()
    plt.savefig(output_dir / "faithfulness_distribution.png")
    plt.close()
    
    # 5. Citation Accuracy Distribution
    cit = [t.metrics.citation_accuracy for t in traces if t.metrics.success]
    plt.figure(figsize=(10, 6))
    plt.hist(cit, bins=10, color="orange", alpha=0.7)
    plt.title("Citation Accuracy Distribution")
    plt.xlabel("Citation Accuracy (0-1)")
    plt.ylabel("Frequency")
    plt.tight_layout()
    plt.savefig(output_dir / "citation_distribution.png")
    plt.close()
