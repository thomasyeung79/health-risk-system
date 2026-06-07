"""Shared Pydantic models for common API patterns."""

from pydantic import BaseModel


class StatusResponse(BaseModel):
    """Simple status response for health checks."""
    status: str
    version: str


class PaginationParams:
    """FastAPI dependency for pagination query parameters."""
    def __init__(self, limit: int = 10, offset: int = 0):
        self.limit = max(1, min(limit, 100))
        self.offset = max(0, offset)
