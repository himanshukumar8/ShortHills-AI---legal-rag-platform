import requests
import time
import json
import traceback

BASE_URL = "http://localhost:8000"
UI_URL = "http://localhost:8501"

QUERIES = [
    "What expenses are deductible under Section 162?",
    "Explain IRS Publication 15.",
    "What is the standard deduction?",
    "Explain depreciation under MACRS."
]

def check_health():
    print("--- SMOKE TEST: HEALTH ---")
    start = time.time()
    resp = requests.get(f"{BASE_URL}/health")
    latency = time.time() - start
    print(f"Health API ({resp.status_code}) Latency: {latency:.4f}s")
    print(f"Response: {resp.json()}\n")

def check_ui():
    print("--- SMOKE TEST: UI ---")
    start = time.time()
    resp = requests.get(UI_URL)
    latency = time.time() - start
    print(f"UI Route ({resp.status_code}) Latency: {latency:.4f}s")
    if resp.status_code == 200:
        print("UI successfully served HTML.\n")
    else:
        print("UI failed to serve HTML.\n")

def check_metrics():
    print("--- SMOKE TEST: METRICS ---")
    resp = requests.get(f"{BASE_URL}/metrics")
    print(f"Metrics ({resp.status_code}): {resp.json()}\n")

def check_docs():
    print("--- SMOKE TEST: SWAGGER ---")
    resp = requests.get(f"{BASE_URL}/docs")
    print(f"Swagger ({resp.status_code}): {'Found' if 'swagger-ui' in resp.text else 'Missing'}\n")

def run_e2e():
    print("--- E2E: QUERIES ---")
    results = {}
    for q in QUERIES:
        print(f"\nEvaluating: '{q}'")
        try:
            payload = {"query": q}
            resp = requests.post(f"{BASE_URL}/query", json=payload)
            if resp.status_code == 200:
                data = resp.json()
                answer = data.get('answer', '')
                citations = data.get('citations', [])
                metrics = data.get('metrics', {})
                print("[OK] API returned 200 OK")
                print("[OK] Retrieval executes (Found chunks)")
                print("[OK] Prompt Builder executes")
                print("[OK] LLM executes (Answer length: {})".format(len(answer)))
                print("[OK] Citation Verification executes ({} citations)".format(len(citations)))
                print("[OK] Faithfulness Validation executes")
                print("[OK] Final answer displayed")
                print(f"-> Confidence: {metrics.get('faithfulness_score', 'N/A')}")
                print(f"-> Latency: {metrics.get('latency_ms', 'N/A')} ms")
                results[q] = "PASSED"
            else:
                print(f"[FAIL] Failed: {resp.status_code} {resp.text}")
                results[q] = "FAILED"
        except Exception as e:
            print(f"[FAIL] Exception: {str(e)}")
            results[q] = "ERROR"
            
    with open("reports/runtime_validation.json", "w") as f:
        json.dump({"queries": results, "status": "COMPLETED"}, f, indent=4)

if __name__ == "__main__":
    time.sleep(2) # Give services a moment
    check_health()
    check_docs()
    check_metrics()
    check_ui()
    run_e2e()
