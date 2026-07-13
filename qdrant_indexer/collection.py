from __future__ import annotations

import logging
from qdrant_indexer.client import BaseQdrantClient

logger = logging.getLogger(__name__)

def setup_collection(client: BaseQdrantClient, collection_name: str, dimension: int) -> None:
    """Sets up the collection based on the frozen Retrieval Architecture."""
    
    # Create the Vector Collection
    client.create_collection(
        collection_name=collection_name,
        vector_size=dimension,
        distance="Cosine"
    )
    
    # Create Payload Indices for highly efficient Pre-Filtering
    payload_fields = ["category", "parent_document_id", "citation"]
    
    for field in payload_fields:
        client.create_payload_index(
            collection_name=collection_name,
            field_name=field,
            field_schema="keyword"
        )
        
    logger.info(f"Qdrant collection '{collection_name}' successfully initialized with metadata indices.")
