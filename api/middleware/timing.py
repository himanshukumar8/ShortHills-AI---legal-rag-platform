import time
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request
from api.utils import metrics_store

class TimingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            
            # Record metrics
            error = response.status_code >= 400
            metrics_store.record_request(process_time, error)
            
            response.headers["X-Process-Time"] = str(process_time)
            return response
        except Exception as e:
            process_time = time.time() - start_time
            metrics_store.record_request(process_time, error=True)
            raise e
