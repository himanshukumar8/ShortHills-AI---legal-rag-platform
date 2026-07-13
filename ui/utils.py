def format_latency(seconds: float) -> str:
    """Format latency into a readable string."""
    if seconds < 1.0:
        return f"{seconds * 1000:.0f} ms"
    return f"{seconds:.2f} s"

def get_badge_class(status: str) -> str:
    """Map verification status to CSS badge classes."""
    status = status.upper()
    if status == "VERIFIED":
        return "badge-green"
    elif status == "UNVERIFIED" or status == "PARTIAL":
        return "badge-yellow"
    else:
        return "badge-red"
