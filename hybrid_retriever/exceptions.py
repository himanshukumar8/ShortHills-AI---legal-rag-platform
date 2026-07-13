class HybridRetrievalError(Exception):
    pass

class EmbeddingGenerationError(HybridRetrievalError):
    pass

class SearchExecutionError(HybridRetrievalError):
    pass

class ValidationFailedError(HybridRetrievalError):
    pass
