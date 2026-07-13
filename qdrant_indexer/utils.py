import uuid
import hashlib

def generate_uuid(string_id: str) -> str:
    """Generate a valid UUID from a string (Qdrant requires UUIDs or Ints)."""
    h = hashlib.md5(string_id.encode("utf-8")).hexdigest()
    return str(uuid.UUID(h))
