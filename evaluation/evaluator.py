import logging
from evaluation.config import GOLDEN_SET_JSON, REPORTS_DIR, CHARTS_DIR
from evaluation.utils import load_golden_set
from evaluation.benchmark_runner import run_benchmark
from evaluation.charts import generate_charts
from evaluation.report_generator import generate_reports

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s")
logger = logging.getLogger("evaluator")

def run_evaluation():
    logger.info("Initializing Evaluation Framework...")
    
    # 1. Load Data
    queries = load_golden_set(GOLDEN_SET_JSON)
    
    # 2. Run Benchmark
    traces = run_benchmark(queries)
    
    # 3. Generate Reports
    logger.info("Generating Evaluation Reports...")
    generate_reports(traces, REPORTS_DIR)
    
    # 4. Generate Charts
    logger.info("Generating Data Visualizations...")
    generate_charts(traces, CHARTS_DIR)
    
    logger.info("Evaluation complete! Check the 'reports' directory.")

if __name__ == "__main__":
    run_evaluation()
