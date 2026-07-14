import requests
from typing import Dict, Any, Optional
from config import UIConfig
import logging

logger = logging.getLogger(__name__)

class APIClient:
    def __init__(self):
        self.base_url = UIConfig.API_HOST
        self.timeout = 10  # Seconds
        
    def check_health(self) -> bool:
        try:
            response = requests.get(f"{self.base_url}/health", timeout=self.timeout)
            if response.status_code == 200:
                data = response.json()
                return data.get("status") == "healthy"
            return False
        except requests.RequestException as e:
            logger.error(f"Health check failed: {e}")
            return False
            
    def get_metrics(self) -> Optional[Dict[str, Any]]:
        try:
            response = requests.get(f"{self.base_url}/metrics", timeout=self.timeout)
            if response.status_code == 200:
                return response.json()
            return None
        except requests.RequestException as e:
            logger.error(f"Metrics fetch failed: {e}")
            return None
            
    def execute_query(self, query: str) -> Optional[Dict[str, Any]]:
        try:
            response = requests.post(
                f"{self.base_url}/query", 
                json={"query": query},
                timeout=60 # Queries might take longer due to retrieval and LLM
            )
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Query failed with status {response.status_code}: {response.text}")
                return None
        except requests.RequestException as e:
            logger.error(f"Query execution failed: {e}")
            return None
            
    def run_evaluation(self) -> Optional[Dict[str, Any]]:
        try:
            response = requests.post(f"{self.base_url}/evaluate", timeout=120)
            if response.status_code == 200:
                return response.json()
            return None
        except requests.RequestException as e:
            logger.error(f"Evaluation failed: {e}")
            return None

# Singleton client instance
api_client = APIClient()
