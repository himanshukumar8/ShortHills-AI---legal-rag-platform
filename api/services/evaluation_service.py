from evaluation.evaluator import run_evaluation
from evaluation.config import EVALUATION_SUMMARY_JSON
import json
from pathlib import Path

class EvaluationService:
    def run_eval(self) -> dict:
        # Run the full suite
        run_evaluation()
        
        # Read the resulting summary
        summary_path = EVALUATION_SUMMARY_JSON
        
        if summary_path.exists():
            with open(summary_path, "r", encoding="utf-8") as f:
                return json.load(f)
        
        return {"status": "Evaluation ran but summary file not found."}
