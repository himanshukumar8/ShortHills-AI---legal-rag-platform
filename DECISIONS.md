# Architectural Decisions Record

## Template
**Decision Number:** [Number]
**Problem:** [Description of the problem]
**Options Considered:** [List of options]
**Selected Option:** [The chosen option]
**Reason:** [Why this option was selected]
**Pros:** [Advantages]
**Cons:** [Disadvantages]
**Status:** [Proposed / Accepted / Deprecated]

---

## Decision 001: Primary Programming Language
**Problem:** Select the core language for backend and data processing.
**Options Considered:** Python, Go, Node.js, Java
**Selected Option:** Python
**Reason:** Python is the industry standard for AI, ML, and NLP tasks. It boasts the richest ecosystem for document processing, embeddings, and LLM integrations.
**Pros:** Massive ecosystem, rapid development, excellent AI libraries.
**Cons:** Slower execution speed compared to compiled languages like Go.
**Status:** Accepted

## Decision 002: Web Framework
**Problem:** Select a web framework for the backend API.
**Options Considered:** FastAPI, Flask, Django
**Selected Option:** FastAPI
**Reason:** FastAPI provides excellent performance, built-in asynchronous support, and automatic OpenAPI documentation. It synergizes perfectly with Pydantic for data validation.
**Pros:** High performance, native async, automatic docs, strict typing.
**Cons:** Smaller ecosystem than Django.
**Status:** Accepted

## Decision 003: Frontend Framework
**Problem:** Select a framework for the User Interface.
**Options Considered:** Streamlit, React, Vue.js
**Selected Option:** Streamlit
**Reason:** Streamlit allows for rapid prototyping of data and AI applications directly in Python, accelerating the development cycle without requiring a separate frontend context.
**Pros:** Fast development, all-Python stack, excellent for AI demos.
**Cons:** Limited customization compared to full SPA frameworks.
**Status:** Accepted

## Decision 004: PDF Parsing Library
**Problem:** Select a library for extracting text and metadata from legal PDFs.
**Options Considered:** PyMuPDF, pdfplumber, PyPDF2
**Selected Option:** PyMuPDF
**Reason:** PyMuPDF offers superior speed and accuracy for text extraction, which is critical for processing dense legal documents.
**Pros:** High performance, accurate text extraction.
**Cons:** Complex API.
**Status:** Accepted

## Decision 005: Keyword Search Engine
**Problem:** Select a database for lexical/keyword search.
**Options Considered:** Elasticsearch, OpenSearch, Solr
**Selected Option:** Elasticsearch
**Reason:** Elasticsearch is the industry standard for full-text search, offering powerful querying capabilities, robust scalability, and extensive documentation.
**Pros:** Highly scalable, rich query DSL.
**Cons:** Resource intensive.
**Status:** Accepted

## Decision 006: Vector Database
**Problem:** Select a database for storing and searching dense vectors.
**Options Considered:** Qdrant, Milvus, Pinecone
**Selected Option:** Qdrant
**Reason:** Qdrant is open-source, highly performant (written in Rust), and easily deployable locally via Docker without relying on managed cloud services during development.
**Pros:** High performance, easy local deployment, rich filtering API.
**Cons:** Newer ecosystem compared to Pinecone.
**Status:** Accepted

## Decision 007: Relational Database
**Problem:** Select a primary datastore for application state and metadata.
**Options Considered:** PostgreSQL, MySQL, SQLite
**Selected Option:** PostgreSQL
**Reason:** PostgreSQL is the most advanced open-source relational database, offering excellent data integrity, JSON support, and scalability.
**Pros:** ACID compliant, rich feature set, industry standard.
**Cons:** Requires dedicated infrastructure (vs SQLite).
**Status:** Accepted

## Decision 008: Graph Database (Optional)
**Problem:** Select a graph database for mapping complex legal relationships.
**Options Considered:** Neo4j, Nebula Graph
**Selected Option:** Neo4j (Optional)
**Reason:** Neo4j is the market leader for graph databases, providing Cypher query language which is intuitive for traversing complex legal networks.
**Pros:** Powerful graph traversal, established ecosystem.
**Cons:** Steep learning curve, resource intensive.
**Status:** Accepted

## Decision 009: Deployment Strategy
**Problem:** Standardize the deployment and runtime environment.
**Options Considered:** Docker, Bare Metal, Serverless
**Selected Option:** Docker
**Reason:** Docker ensures environment consistency across development, testing, and production. It simplifies the orchestration of multiple services (API, Elasticsearch, Qdrant, Postgres).
**Pros:** Portability, consistency, easy orchestration via Docker Compose.
**Cons:** Slight learning curve for container networking.
**Status:** Accepted

## Decision 010: Corpus Downloader — Concurrency Model
**Problem:** Choose a concurrency strategy for downloading 100 PDF documents.
**Options Considered:** ThreadPoolExecutor, asyncio + aiohttp, multiprocessing
**Selected Option:** ThreadPoolExecutor
**Reason:** The workload is I/O-bound (network downloads). ThreadPoolExecutor is simpler to reason about, debug, and maintain than async. For 100 documents the overhead difference is negligible. multiprocessing would waste resources on process creation for I/O-bound work.
**Pros:** Simple, debuggable, sufficient for scale, stdlib-only.
**Cons:** GIL prevents true parallelism (irrelevant for I/O-bound tasks).
**Status:** Accepted

## Decision 011: Corpus Downloader — Retry Strategy
**Problem:** Choose where to implement retry logic (urllib3 automatic retries vs manual orchestrator retries).
**Options Considered:** urllib3.Retry on the session adapter, manual retry loop in the orchestrator
**Selected Option:** Manual retry loop in the orchestrator (main.py)
**Reason:** Manual retries give full control over logging each attempt, counting attempts accurately, applying exponential backoff, and deciding which error classes (download errors, validation failures) warrant a retry.
**Pros:** Full visibility, accurate counting, configurable backoff, retry on validation failures.
**Cons:** More code than urllib3 automatic retries.
**Status:** Accepted

## Decision 012: Corpus Downloader — Configuration Management
**Problem:** Choose a configuration approach for the download pipeline.
**Options Considered:** argparse CLI flags, raw environment variables, pydantic-settings
**Selected Option:** pydantic-settings with `.env` file support
**Reason:** pydantic-settings provides type validation, default values, and `.env` file loading in a single class. It is already the project standard (PROJECT_GUIDE.md specifies pydantic-settings). CLI flags are limited to `--test-mode` to avoid parameter explosion.
**Pros:** Type-safe, self-documenting, consistent with project standards.
**Cons:** Adds a dependency (already in the project stack).
**Status:** Accepted

## Decision 013: Semantic Legal Chunking over Fixed-Size Splitters
**Problem:** We need to fragment legal text into chunks small enough for embedding models (e.g., 512-8192 tokens) while preserving enough context for an LLM to accurately answer complex queries.
**Options Considered:** LangChain RecursiveCharacterTextSplitter, Fixed-size sliding windows, Custom semantic chunker.
**Selected Option:** Custom, category-aware hierarchical semantic chunker.
**Reason:** Standard overlapping splitters artificially destroy legal context by cutting mid-sentence or mid-statute. By snapping strictly to legal section boundaries, retrieving a specific chunk via vector search guarantees retrieving an entire atomic legal thought.
**Pros:** Perfect citation boundaries, zero lost context, highly compatible with downstream LLMs.
**Cons:** Chunks vary wildly in size depending on the statute.
**Status:** Accepted

## Decision 014: Chunk Quality Assessment (QA) Strategy
**Problem:** Before investing in expensive Embedding generation, we need to guarantee that the generated semantic chunks are actually suitable for an LLM (neither too small to lack context, nor too large to fit in context windows).
**Options Considered:** Proceed directly to embeddings, or build a standalone QA module.
**Selected Option:** Build a standalone Chunk QA & Validation module.
**Reason:** The QA module revealed a score of 66/100. It proved that while our semantic parent-child hierarchy is structurally flawless (0 orphans, 0 missing citations), our raw semantic chunking produces 18,665 tiny chunks and 1,271 oversized chunks due to the variance in legal writing styles.
**Pros:** Caught context-window issues *before* wasting API credits/compute on embeddings.
**Cons:** Requires an additional step to implement chunk coalescing and sub-splitting in the future.
**Status:** Accepted

## Decision 015: Provider-Agnostic Embedding Architecture
**Problem:** We need to generate embeddings but AI models change rapidly. Hardcoding an API client (like OpenAI) or a local model framework (like `sentence-transformers`) creates technical debt and vendor lock-in.
**Options Considered:** Hardcoding `sentence-transformers`, using LangChain wrappers, custom Strategy pattern.
**Selected Option:** Custom `BaseEmbeddingProvider` interface (Strategy Pattern).
**Reason:** LangChain adds excessive dependencies and black-box abstractions. By defining our own simple `embed_batch()` interface, we can seamlessly inject `OpenAIProvider`, `SentenceTransformerProvider`, or a deterministic `MockProvider` (used for rapid test integration).
**Pros:** Ultimate flexibility, zero vendor lock-in, incredibly easy to unit test using the Mock provider.
**Cons:** We have to maintain the minimal interface ourselves.
**Status:** Accepted

## Decision 016: Elasticsearch Indexing Strategy
**Problem:** We need a robust exact-match and keyword engine to pair with dense vectors for our Hybrid Search architecture.
**Options Considered:** Postgres Full-Text Search, Elasticsearch, Typesense.
**Selected Option:** Elasticsearch with `legal_english_analyzer`.
**Reason:** Elasticsearch provides the most robust scalable inverted index. By configuring a custom analyzer (`standard` tokenizer, `lowercase`, `english_stop`, `snowball_stemmer`), we normalize legal jargon (e.g. "taxation" to "tax"). We map critical metadata like `category` and `citation` as strictly typed `keyword` fields to guarantee fast, exact boolean filtering.
**Pros:** Industry standard for lexical search, perfect synergy with Qdrant for Reciprocal Rank Fusion.
**Cons:** High memory footprint compared to Postgres FTS.
**Status:** Accepted

## Decision 017: Synthetic Elasticsearch Benchmark & QA
**Problem:** To validate Elasticsearch mapping and analyzer configurations before production without human-labeled datasets (qrels).
**Options Considered:** Manual ad-hoc querying, hiring subject matter experts to build a gold-standard dataset, Synthetic Benchmarking via chunk sampling.
**Selected Option:** Synthetic Benchmarking via Chunk Sampling.
**Reason:** By sampling random chunks from the exact distribution, we can dynamically build 100 queries representing 5 types (citations, keywords, phrases, boolean, metadata filtered). The chunk the query was derived from acts as the Ground Truth. This guarantees we can mathematically calculate Recall@5 and Precision@5 instantly on every pipeline run.
**Pros:** Fully automated QA, 0 data-labeling costs, regression detection.
**Cons:** Synthetic queries aren't always completely representative of human typing errors (though the legal analyzer handles word-stemming).
**Status:** Accepted

## Decision 018: Post-QA Error Analysis Classification
**Problem:** A QA score of 38.4/100 is unacceptable, but raw metrics don't tell us *how* to fix the index.
**Options Considered:** Manual review of all failed queries, Automated Heuristic Categorization.
**Selected Option:** Automated Heuristic Categorization.
**Reason:** By categorizing the 60 failed queries into 9 strict buckets (e.g., "Analyzer/tokenization issue", "Metadata filtering issue"), we can quantifiably prioritize architectural changes. 26% of failures were analyzer-based, proving the need for synonym graphs, while 20% were genuine retrieval failures, proving the absolute necessity of our upcoming Hybrid Search (Qdrant) phase.
**Pros:** Actionable, data-driven architecture improvements.
**Cons:** Synthetic classification has a margin of error.
**Status:** Accepted

## Decision 019: Qdrant Payload Pre-Filtering Strategy
**Problem:** Vector databases suffer performance degradation when searching across the entire billion-vector space just to throw away 99% of results that don't match a user's category filter (e.g. "Only Acts").
**Options Considered:** Post-Filtering (filtering after retrieval), Pre-Filtering (filtering before retrieval).
**Selected Option:** Pre-Filtering via Payload Indexing.
**Reason:** We have explicitly instructed Qdrant to create keyword payload indices on `category`, `parent_document_id`, and `citation`. When a Hybrid Search query includes these filters, Qdrant will instantly narrow the vector space using the HNSW graph bounds *before* computing expensive Cosine similarities.
**Pros:** Massive retrieval speedup, guarantees exact metadata matches.
**Cons:** Slightly increased RAM footprint in the Qdrant cluster.
**Status:** Accepted

## Decision 020: Qdrant Synthetic Semantic QA
**Problem:** Need to mathematically prove the dense vector retrieval quality (Recall@5, NDCG, MRR) before integrating with the LLM or Elasticsearch.
**Options Considered:** Wait for human user testing, Synthetic Semantic QA via Vector Self-Retrieval.
**Selected Option:** Synthetic Semantic QA via Vector Self-Retrieval.
**Reason:** By sampling 100 actual chunk embeddings and re-querying the Qdrant cluster for those exact vectors (applying Payload Pre-Filtering in some cases), we simulate the dense retrieval bounds. This confirms the collection schema, cosine metric scaling, and payload integrity without requiring a massive labeled dataset.
**Pros:** Instant regression testing, verifies vector dimensions and payload indices.
**Cons:** Simulates perfect query translation (since the query vector *is* the document vector), artificially inflating the simulated MRR to 1.0. 
**Status:** Accepted

## Decision 021: Reciprocal Rank Fusion (RRF) for Hybrid Retrieval
**Problem:** Lexical Search (BM25) generates unbounded absolute scores (e.g., 15.4, 12.1). Semantic Search (Cosine Similarity) generates bounded scores between -1 and 1. We cannot mathematically sum or compare these scores directly.
**Options Considered:** Score Normalization (Min-Max), Weighted Combination (Alpha tuning), Reciprocal Rank Fusion (RRF).
**Selected Option:** Reciprocal Rank Fusion (RRF).
**Reason:** RRF is highly robust and requires zero hyperparameter tuning (other than the standard constant `k=60`). It ignores the absolute score and instead fuses results based on the *rank* returned by each engine (`1 / (k + rank)`). This perfectly balances exact keyword matches from Elasticsearch (e.g., "Section 162") with broad conceptual matches from Qdrant.
**Pros:** Mathematically sound, parameter-free, highly proven in production retrieval systems.
**Cons:** We lose the absolute confidence score (e.g. knowing if the top hit was actually a weak match).
**Status:** Accepted

## Decision 022: Isolated Prompt Builder Architecture
**Problem:** We need to ensure that the generative LLM strictly follows rules regarding hallucination and legal citations without leaking business logic or mixing concerns in the retriever module.
**Options Considered:** Hardcode prompts in the retrieval module, Create an isolated Prompt Builder module.
**Selected Option:** Isolated Prompt Builder module (`answer_engine`).
**Reason:** By separating the prompt building logic from the LLM execution and Retrieval logic, we can independently unit-test the prompt generation. We can parse the token bounds, dynamically inject chunks until limits are reached, and run validation functions ensuring that "NEVER invent facts" and the JSON schema are mathematically present in the payload *before* spending tokens on an LLM API call.
**Pros:** Highly testable, strict token management, strict guardrail enforcement.
**Cons:** Adds a small processing overhead between retrieval and generation.
**Status:** Accepted

## Decision 023: LLM Provider Abstraction & Strict JSON Parsing
**Problem:** We must avoid vendor lock-in with LLM APIs while guaranteeing that the RAG pipeline does not crash if the LLM hallucinates markdown or malformed JSON.
**Options Considered:** Direct OpenAI API integration, Strategy Pattern Abstraction with strict schema validation.
**Selected Option:** Strategy Pattern Abstraction with strict schema validation.
**Reason:** By creating `BaseLLMProvider` and implementing `MockProvider`, `OpenAIProvider`, and `GeminiProvider`, the rest of the application remains vendor-agnostic. Furthermore, the `response_parser` safely strips markdown code-blocks (```json) that LLMs often incorrectly inject, and `response_validator` acts as a hard stop if required fields (citations, confidence) are omitted by the LLM. 
**Pros:** Zero vendor lock-in, highly resilient to LLM formatting errors, easy to unit test via the Mock Provider.
**Cons:** We must maintain multiple provider implementations.
**Status:** Accepted

## Decision 024: Citation Verification & Evidence Validation
**Problem:** Even with strict Prompt Engineering, LLMs will occasionally hallucinate citations, misattribute page numbers, or make logical leaps not explicitly stated in the context (unsupported claims).
**Options Considered:** Instruct the LLM to self-reflect, Implement deterministic Citation Mapping & Heuristic Evidence Checks.
**Selected Option:** Implement deterministic Citation Mapping & Heuristic Evidence Checks (`citation_engine`).
**Reason:** The LLM cannot reliably grade its own hallucinations. By abstracting the verification layer, we can run deterministic `string`/`regex` checks on `document_title`, `citation`, and `page_bounds` against the actual retrieved payload. Furthermore, we run basic heuristic text matching to flag claims (like "must/shall/require") that lack a verified citation backing.
**Pros:** 100% mathematically guarantees that cited documents and pages exist in the retrieved subset.
**Cons:** The "Evidence Verification" (semantic faithfulness) is currently heuristic and not a true NLI model evaluation.
**Status:** Accepted

## Decision 025: Faithfulness Validation
**Problem:** The Citation Engine verifies a citation exists, but it doesn't prove the cited text *supports* the claim. If the LLM says "You can deduct 100% of meals" and cites "IRC Section 162" (which says 50%), the citation exists but the claim is hallucinated.
**Options Considered:** Prompt the LLM to self-correct, Post-process with an independent NLI checker.
**Selected Option:** Post-process with an independent NLI checker (`faithfulness_validator`).
**Reason:** We break the LLM answer into atomic claims, fetch the exact text of the cited chunks, and run a dedicated `BaseFaithfulnessChecker` (Strategy Pattern) to determine if the chunk entails, contradicts, or provides insufficient evidence for the claim. This cross-encoder architecture mathematically bounds hallucinations.
**Pros:** Strictly isolates generation from evaluation. Prevents convincing but contradictory legal answers.
**Cons:** Splitting claims deterministically is hard without NLP tools; running a separate NLI model adds latency.
**Status:** Accepted

## Decision 026: Golden Set Evaluation Dataset
**Problem:** We need a standardized, balanced, and deterministic way to evaluate changes to the RAG architecture (chunking logic, retrieval weights, LLM prompts) without relying on ad-hoc manual testing.
**Options Considered:** Manually author 100 queries, Synthetically generate queries from actual indexed chunks.
**Selected Option:** Synthetically generate queries from actual indexed chunks (`golden_set_generator.py`).
**Reason:** By randomly sampling exactly 20 chunks from each of the 5 legal categories (100 total) that exist in `data/optimized_chunks`, we guarantee that the expected documents, chunk IDs, and page bounds actually exist in the database. 
**Pros:** 100% ground-truth guarantee. Perfectly balanced category distribution.
**Cons:** The generated user queries are currently templated rather than organic natural language.
**Status:** Accepted

## Decision 027: Evaluation Framework
**Problem:** We need a way to orchestrate the Golden Set queries against the Answer Engine to compute final metrics (NDCG, Recall, MRR, Faithfulness, Citation Accuracy) and generate visualizations.
**Options Considered:** Ragas / TruLens (third party libraries), Custom Deterministic Evaluator.
**Selected Option:** Custom Deterministic Evaluator.
**Reason:** Third-party evaluation frameworks use LLMs-as-a-judge, which is fundamentally non-deterministic and can cost hundreds of dollars per benchmark run. By using our own mathematical deterministic verification system (NDCG based on Golden chunk IDs, Regex-based Citation Verification, and Cross-Encoder mock for Faithfulness), we get instant, free, and mathematically rigorous trace results. We bypass GUI constraints and generate `matplotlib` charts and markdown reports directly.
**Pros:** Highly testable, zero LLM cost during evaluation, deterministic metrics.
**Cons:** We don't get the "nuance" of LLM-as-a-judge for subjective answers.
**Status:** Accepted

## Decision 028: FastAPI Service Layer
**Problem:** The Legal RAG Engine needs to be exposed via a production-grade REST API for upstream integration.
**Options Considered:** Flask, Django, FastAPI.
**Selected Option:** FastAPI.
**Reason:** FastAPI provides out-of-the-box data validation using Pydantic, automatic OpenAPI/Swagger generation, and built-in async support. It enforces strong typing which matches our internal architecture strictly. We built a structured layer with routers, dependency injected services, and middleware for timing/logging.
**Pros:** Type safety, fast execution, self-documenting APIs.
**Cons:** Minimal learning curve for developers unfamiliar with async/await in Python.
**Status:** Accepted

## Decision 029: Streamlit Presentation Layer
**Problem:** The Legal RAG Engine needs a modern, enterprise-grade user interface for end users to perform semantic search and view citations.
**Options Considered:** React/Next.js, Streamlit, Gradio.
**Selected Option:** Streamlit.
**Reason:** Streamlit allows for rapid prototyping using Python while still providing the capability to inject custom CSS for an enterprise feel. By building the UI as a completely independent "thin client" that queries the FastAPI backend, we avoid the typical Streamlit pitfall of duplicating backend processing logic in the frontend. We structured it using component-based architecture (`ui/components/`) to maintain clean separation.
**Pros:** Extremely fast development time, maintains entire codebase in Python, natively handles complex data layouts (JSON traces, markdown rendering).
**Cons:** State management is inherently tricky across reruns, requiring careful session state handling.
**Status:** Accepted

## Decision 030: Containerization Strategy
**Problem:** The Legal RAG Platform needs to be easily deployable in an enterprise environment without developers needing to manually manage pip virtual environments and conflicting dependencies.
**Options Considered:** Ansible scripts, Docker & Docker Compose, Kubernetes Helm Charts.
**Selected Option:** Docker & Docker Compose.
**Reason:** Docker Compose is the universal standard for "one-click" local replication of microservices. We designed the cluster with explicitly orchestrated dependencies (`ui` depends on `api` passing its healthcheck) and enforced multi-stage builds on `python:3.10-slim` images to heavily reduce final artifact size. We mapped all host volumes correctly so logs and evaluation reports persist back to the host filesystem.
**Pros:** Instant onboarding, guaranteed reproducibility across OS platforms, prevents dependency drift.
**Cons:** Minimal performance overhead mapping network bridges locally.
**Status:** Accepted

## Decision 031: Production Deployment Strategy
**Problem:** The Legal RAG Platform needs a defined strategy for public cloud deployment that prevents tight coupling to a single cloud provider (AWS/GCP) while supporting distinct scaling metrics for the UI and Backend.
**Options Considered:** Single monolithic VM deployment, Kubernetes Cluster, Split-Tier PaaS.
**Selected Option:** Split-Tier PaaS (Streamlit Community Cloud + Render/Fly.io).
**Reason:** By fully separating the frontend (`ui/`) and backend (`api/`) and strictly coupling them via environment variables and standard HTTP protocols, we can leverage specialized managed services. Streamlit Cloud perfectly optimizes the UI framework, while standard Docker runners (Render/Fly.io) handle the FastAPI throughput. We injected standard `CORSMiddleware` into the backend to facilitate cross-origin requests natively.
**Pros:** Extreme scale-out potential, free tier compatible, specialized runtimes.
**Cons:** Requires managing CORS and two discrete sets of environment variables.
**Status:** Accepted

## Decision 032: System Architecture Documentation
**Problem:** A highly sophisticated multi-stage RAG pipeline requires comprehensive documentation to onboard new engineers and communicate the data flow (especially the split between offline ingestion and online retrieval).
**Options Considered:** Text-only READMEs, Mermaid.js markdown injections, Standalone standard graphics (`.drawio`, `.svg`, `.png`).
**Selected Option:** Standalone standard graphics alongside a detailed `architecture.md`.
**Reason:** Enterprise environments require documentation that can be easily embedded into slide decks (PNG), natively rendered in browsers/GitHub (SVG), and modified in structural editors (DrawIO). We developed a Python pipeline using `matplotlib` to programmatically render the architectural bounds, guaranteeing crisp scaling while separating the Offline Corpus preparation from the Online Hybrid Retrieval pathway.
**Pros:** Multi-format accessibility, visually segments complex sub-engines (like Faithfulness Validation).
**Cons:** Architectural diagrams must be manually updated if the pipeline order changes.
**Status:** Accepted
