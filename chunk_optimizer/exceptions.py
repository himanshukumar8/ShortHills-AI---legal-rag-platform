from __future__ import annotations

class OptimizerError(Exception):
    def __init__(self, message: str, document_id: str | None = None) -> None:
        self.message = message
        self.document_id = document_id
        doc_prefix = f"[{document_id}] " if document_id else ""
        super().__init__(f"{doc_prefix}{message}")
