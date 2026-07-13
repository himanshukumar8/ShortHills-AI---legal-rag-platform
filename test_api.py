import json
from pathlib import Path
from fastapi.testclient import TestClient
from api.app import app

client = TestClient(app)

def run_tests():
    reports_dir = Path("reports")
    reports_dir.mkdir(exist_ok=True)
    
    results = {}
    
    # Test Health
    health_res = client.get("/health")
    results["health"] = {
        "status_code": health_res.status_code,
        "json": health_res.json()
    }
    
    # Test Metrics (should show 1 successful health check)
    metrics_res = client.get("/metrics")
    results["metrics_initial"] = {
        "status_code": metrics_res.status_code,
        "json": metrics_res.json()
    }
    
    # Test Query
    query_res = client.post("/query", json={"query": "What are the rules for independent contractors?"})
    results["query"] = {
        "status_code": query_res.status_code,
        "json": query_res.json() if query_res.status_code == 200 else {"error": query_res.text}
    }
    
    # Test Evaluation (Since this takes a bit, we'll see if it runs. Evaluation Service already reads the previous trace for speed if available!)
    eval_res = client.post("/evaluate")
    results["evaluate"] = {
        "status_code": eval_res.status_code,
        # Truncating json to avoid massive file if it's the full summary
        "json": "Evaluation successful" if eval_res.status_code == 200 else {"error": eval_res.text}
    }
    
    # Final Metrics
    metrics_final = client.get("/metrics")
    results["metrics_final"] = {
        "status_code": metrics_final.status_code,
        "json": metrics_final.json()
    }
    
    with open(reports_dir / "api_validation.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4)
        
    print("API Validation complete!")

if __name__ == "__main__":
    run_tests()
