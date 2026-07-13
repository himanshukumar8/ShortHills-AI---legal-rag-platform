import json
from pathlib import Path
from ui.api_client import api_client

def validate_ui_client():
    reports_dir = Path("reports")
    reports_dir.mkdir(exist_ok=True)
    
    validation = {
        "health_check": api_client.check_health(),
        "metrics_check": api_client.get_metrics() is not None,
        "query_execution": api_client.execute_query("What is IRS Section 162?") is not None
    }
    
    with open(reports_dir / "ui_validation.json", "w", encoding="utf-8") as f:
        json.dump(validation, f, indent=4)
        
    print("UI API Client Validation complete!")

if __name__ == "__main__":
    validate_ui_client()
