# Legal RAG Platform Architecture

The ShorthillsAI Legal RAG platform is an enterprise-grade retrieval-augmented generation system designed for highly accurate legal search and question answering. The architecture is explicitly designed into two distinct operational pipelines: the **Offline Document Processing Pipeline** and the **Online Query Pipeline**.

## 1. Technology Stack
- **Languages**: Python 3.10
- **Frontend**: Streamlit
- **Backend API**: FastAPI
- **Lexical Search Engine**: Elasticsearch (BM25)
- **Vector Search Engine**: Qdrant (Dense Vector)
- **Deployment**: Docker & Docker Compose

## 2. Offline Document Processing Pipeline
The offline pipeline is responsible for ingesting raw legal documents and converting them into highly retrievable semantic chunks.

### Data Flow
1. **Downloader**: Fetches the raw PDFs (e.g., IRS Publications, Court Judgments, Treasury Regulations).
2. **Parser**: Extracts the text from PDFs, normalizing layouts and preserving hierarchical headers.
3. **Normalizer**: Cleans the text, standardizing legal citations, removing whitespace artifacts, and mapping out structural boundaries.
4. **Semantic Chunker**: Divides the text into overlapping segments, strictly respecting section boundaries (e.g., ensuring an entire sub-paragraph stays within a single chunk).
5. **Chunk Optimizer**: Pre-calculates token constraints and metadata bindings.
6. **Embeddings**: Uses `legal-bert-base-uncased` to generate dense vector embeddings of the chunks.
7. **Indexing**: 
   - The raw text and structural metadata are indexed into **Elasticsearch** for rapid lexical search.
   - The dense vectors and core metadata are indexed into **Qdrant** for semantic search.

## 3. Online Query Pipeline
The online pipeline is responsible for serving user queries in real-time, executing the hybrid retrieval, generating answers, and validating the results strictly against the retrieved corpus.

### Data Flow
1. **User**: Enters a legal question into the **Streamlit UI**.
2. **Streamlit UI**: Forwards the query securely to the **FastAPI Backend** via REST `POST /query`.
3. **Hybrid Retrieval**: The backend parses the query and executes two parallel searches:
   - **Elasticsearch (BM25)**: Finds exact keyword matches and specific statute numbers.
   - **Qdrant (Dense Vector)**: Finds semantically similar passages using vector distance.
4. **Reciprocal Rank Fusion (RRF)**: Merges the two candidate sets, ranking the most consistently relevant chunks to the top.
5. **Prompt Builder**: Injects the fused chunks into a strict legal RAG prompt format, enforcing citation requirements.
6. **LLM Provider**: Generates the answer based *only* on the provided context (Mock LLM, OpenAI, or Anthropic).
7. **Citation Verification Engine**: Validates that every generated citation points to an actual retrieved document and page.
8. **Faithfulness Validation**: Extracts logical claims from the answer and checks them against the context to prevent hallucination.
9. **Final Answer**: Transmitted back to the Streamlit UI containing the text, confidence scores, and verification badges.

## Why Hybrid Retrieval?
Hybrid Retrieval is the cornerstone of this platform. Legal queries uniquely demand both semantic understanding and exact keyword precision:
- If a user asks *"What are the rules for independent contractors?"*, dense vectors (Qdrant) excel at finding conceptual matches even if different terminology is used.
- If a user asks *"Show me IRS Publication 15 Section 2"*, lexical search (Elasticsearch) excels at instantly finding exact string matches for statutes and citations.
By utilizing Reciprocal Rank Fusion, the system mathematically guarantees that chunks scoring highly in *both* conceptual relevance and keyword matching are prioritized, effectively eliminating the blind spots present in pure-vector or pure-keyword architectures.
