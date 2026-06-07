"""Pydantic models for report API."""

from typing import Optional

from pydantic import BaseModel, Field


class GenerateReportRequest(BaseModel):
    language: str = Field(default="English")
    style: str = Field(default="balanced", pattern="^(balanced|coaching|clinical)$")
    days: int = Field(default=7, ge=1, le=90)
    health_record_id: Optional[int] = None
    emotion_record_id: Optional[int] = None


class ReportSection(BaseModel):
    title: str
    content: str


class ReportContent(BaseModel):
    summary: str
    sections: list[ReportSection]


class TokenUsage(BaseModel):
    total: int
    cost_estimate: float


class GenerateReportResponse(BaseModel):
    id: int
    created_at: str
    language: str
    style: str
    provider: str
    model: str
    is_cached: bool
    is_fallback: bool
    report: ReportContent
    token_usage: TokenUsage


class ReportSummary(BaseModel):
    id: int
    created_at: str
    language: str
    style: str
    provider: str
    is_cached: bool
    is_fallback: bool
    summary: str

    model_config = {"from_attributes": True}


class ReportListResponse(BaseModel):
    items: list[ReportSummary]
    total: int
    limit: int
    offset: int
