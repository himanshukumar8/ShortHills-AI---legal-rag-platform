from pathlib import Path

# Paths
BASE_DIR = Path("d:/Projects/ShorthillsAI")
EVALUATION_DIR = BASE_DIR / "evaluation"
REPORTS_DIR = BASE_DIR / "reports"
CHARTS_DIR = REPORTS_DIR / "charts"

GOLDEN_SET_JSON = EVALUATION_DIR / "golden_set.json"
EVALUATION_REPORT_CSV = REPORTS_DIR / "evaluation_report.csv"
EVALUATION_SUMMARY_JSON = REPORTS_DIR / "evaluation_summary.json"
EVALUATION_DASHBOARD_JSON = REPORTS_DIR / "evaluation_dashboard.json"
EVALUATION_REPORT_MD = REPORTS_DIR / "evaluation_report.md"

# Weights for final score
WEIGHT_RETRIEVAL = 0.35
WEIGHT_FAITHFULNESS = 0.25
WEIGHT_CITATION = 0.20
WEIGHT_LATENCY = 0.10
WEIGHT_RELIABILITY = 0.10

# Score Thresholds
LATENCY_IDEAL_MS = 1500
LATENCY_MAX_MS = 5000
