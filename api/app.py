from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.config import api_config
from api.middleware.timing import TimingMiddleware
from api.middleware.logging import LoggingMiddleware
from api.middleware.exception_handler import global_exception_handler
from api.routers import query, evaluation, health, metrics

def create_app() -> FastAPI:
    app = FastAPI(
        title=api_config.app_name,
        version=api_config.version,
        description="REST APIs for the Legal RAG System"
    )

    # Middlewares (Order matters: outermost is added first/last depending on starlette internals)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"], # In production, read from CORS_ORIGINS env var
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(LoggingMiddleware)
    app.add_middleware(TimingMiddleware)

    # Exception Handlers
    app.add_exception_handler(Exception, global_exception_handler)

    # Routers
    app.include_router(query.router)
    app.include_router(evaluation.router)
    app.include_router(health.router)
    app.include_router(metrics.router)

    return app

app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.app:app", host=api_config.host, port=api_config.port, reload=api_config.debug)
