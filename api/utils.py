# Utility functions for the API layer

class MetricsStore:
    def __init__(self):
        self.request_count = 0
        self.error_count = 0
        self.total_response_time = 0.0

    def record_request(self, duration: float, error: bool = False):
        self.request_count += 1
        self.total_response_time += duration
        if error:
            self.error_count += 1

    def get_metrics(self):
        avg_latency = (self.total_response_time / self.request_count) if self.request_count > 0 else 0
        return {
            "total_requests": self.request_count,
            "error_rate": (self.error_count / self.request_count) if self.request_count > 0 else 0,
            "average_latency_s": avg_latency
        }

metrics_store = MetricsStore()
