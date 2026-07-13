# Project Guide: Legal AI Search System

## Project Objective
Develop a production-grade Legal AI Search System focused on the U.S. Tax & Legal domain. The system will enable advanced hybrid search, document parsing, citation generation, and legal question answering over a curated corpus of U.S. tax and legal documents.

## Assignment Requirements
- Build a robust backend supporting PDF parsing, chunking, metadata extraction, and embedding generation.
- Implement hybrid search combining keyword search (Elasticsearch) and vector search (Qdrant).
- Develop a citation engine to accurately trace LLM responses back to source documents.
- Design a scalable, modular architecture following enterprise best practices.
- Deliver an evaluation pipeline (Golden Set) and an interactive UI.

## Final Technology Stack
- **Backend:** Python, FastAPI
- **Frontend/UI:** Streamlit
- **Document Processing:** PyMuPDF
- **Keyword Search:** Elasticsearch
- **Vector Search:** Qdrant
- **Relational Database:** PostgreSQL
- **Graph Database:** Neo4j (Optional)
- **Deployment:** Docker, Docker Compose

## Folder Structure
```text
.
├── backend/
│   ├── api/          # FastAPI routes and endpoints
│   ├── core/         # Core business logic, configuration, exceptions
│   ├── db/           # Database connections and ORM models
│   ├── services/     # Domain services (parsing, embedding, search)
│   └── tests/        # Unit and integration tests
├── frontend/
│   ├── components/   # Reusable UI components
│   └── pages/        # Streamlit pages
├── data/
│   ├── raw/          # Raw PDF documents
│   └── processed/    # Processed chunks/metadata
├── docs/             # Project documentation
├── scripts/          # Utility scripts (downloaders, migrations)
├── docker-compose.yml
└── README.md
```

## Coding Standards
- **Language:** Python 3.10+
- **Style Guide:** PEP 8 compliance, enforced via `black` and `ruff`.
- **Type Hinting:** Strict type hints (`mypy` enforced) on all functions and methods.
- **Docstrings:** Google style docstrings for all modules, classes, and public functions.
- **Imports:** Sorted systematically using `isort`.

## Architecture Principles
- **SOLID Principles:** Single Responsibility, Open/Closed, Liskov Substitution, Interface Segregation, Dependency Inversion.
- **Clean Architecture:** Separation of concerns between API layer, business logic, and data access.
- **Modularity:** High cohesion and low coupling. Services should be easily swappable.
- **Configuration-Driven:** No hardcoded values. Use environment variables and configuration files (`pydantic-settings`).

## Production-Quality Expectations
- **Maintainability:** Code must be readable, self-documenting, and thoroughly tested.
- **Scalability:** Stateless API design, connection pooling, and asynchronous processing where appropriate.
- **Defensibility:** Every architectural and implementation decision must be justified and documented.

## Non-Functional Requirements
- **Performance:** Low latency search queries (<500ms).
- **Reliability:** Graceful degradation and robust error recovery.
- **Extensibility:** Easy integration of new embedding models or search databases.

## Security Considerations
- Input validation and sanitization (via Pydantic).
- Secure credential management (never commit secrets to version control).
- Proper CORS configuration and API rate limiting.

## Logging Strategy
- Use structured JSON logging for production environments.
- Log levels: `DEBUG` (development), `INFO` (general flow), `WARNING` (recoverable issues), `ERROR` (failures), `CRITICAL` (system stops).
- Include contextual information (request IDs, timestamps, module names).

## Error Handling Strategy
- Catch specific exceptions, never bare `except Exception:`.
- Define custom application exceptions in a central module.
- Translate internal exceptions to standard HTTP error responses at the API boundary (using FastAPI exception handlers).

## Testing Strategy
- **Unit Tests:** High coverage (>80%) for core business logic and utilities (`pytest`).
- **Integration Tests:** Verifying interactions with databases (Elasticsearch, Qdrant, Postgres) using Testcontainers or mock services.
- **Mocking:** Isolate external dependencies using `unittest.mock`.

## Deployment Strategy
- Fully containerized environment using Docker.
- `docker-compose` for local orchestration of all services.
- Multi-stage Docker builds to minimize production image size.

## Definition of Done
- Code is written, reviewed, and adheres to coding standards.
- Unit and integration tests are passing.
- Documentation (code and project level) is updated.
- No hardcoded values or "hacky" shortcuts exist.
- Feature is fully containerized and runs seamlessly via Docker.

## Important Project Rules
- Think and implement like a Senior Software Engineer with 10+ years of experience.
- Never take shortcuts just to make something work.
- Build module-by-module.
- Stop and wait for instructions after completing the assigned step.
