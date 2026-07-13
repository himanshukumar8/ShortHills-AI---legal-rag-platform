import os

class UIConfig:
    # API endpoints
    API_HOST = os.getenv("API_HOST", "http://localhost:8000")
    
    # Static Data
    APP_TITLE = "ShorthillsAI Legal RAG"
    APP_SUBTITLE = "Enterprise Legal AI Search"
    APP_VERSION = "1.0.0"
    
    # Simulated metadata for display
    TOTAL_DOCUMENTS = 21363
    TOTAL_CHUNKS = 85400
    EMBEDDING_MODEL = "legal-bert-base-uncased"
    LLM_PROVIDER = "GPT-4-Turbo"
    RETRIEVAL_MODE = "Hybrid (BM25 + Dense Vectors)"
    
    # Default example queries
    EXAMPLE_QUERIES = [
        "What expenses are deductible under Section 162?",
        "What is the standard deduction?",
        "Explain depreciation.",
        "What is IRS Publication 15?"
    ]
