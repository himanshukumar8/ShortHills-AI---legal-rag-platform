from __future__ import annotations

"""Elasticsearch mapping and analyzer schema for Legal Corpus."""

INDEX_SETTINGS = {
    "analysis": {
        "analyzer": {
            "legal_english_analyzer": {
                "type": "custom",
                "tokenizer": "standard",
                "filter": [
                    "lowercase",
                    "english_stop",
                    "snowball_stemmer"
                ]
            }
        },
        "filter": {
            "english_stop": {
                "type": "stop",
                "stopwords": "_english_"
            },
            "snowball_stemmer": {
                "type": "snowball",
                "language": "English"
            }
        }
    }
}

INDEX_MAPPING = {
    "properties": {
        "chunk_id": {"type": "keyword"},
        "document_id": {"type": "keyword"},
        "category": {"type": "keyword"},
        "text": {
            "type": "text",
            "analyzer": "legal_english_analyzer"
        },
        "citation": {
            "type": "keyword",
            "copy_to": "citation_text" # For partial search
        },
        "citation_text": {
            "type": "text",
            "analyzer": "whitespace"
        },
        "cross_references": {"type": "keyword"},
        "page_start": {"type": "integer"},
        "page_end": {"type": "integer"},
        "hierarchy_level": {"type": "integer"}
    }
}
