class EvaluationError(Exception):
    """Base class for evaluation exceptions."""
    pass

class BenchmarkExecutionError(EvaluationError):
    """Raised when the benchmark query execution fails completely."""
    pass

class ReportGenerationError(EvaluationError):
    """Raised when generating the final reports fails."""
    pass
