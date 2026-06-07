"""Pydantic models for trend analysis responses."""

from typing import Optional

from pydantic import BaseModel, Field


class MetricTrend(BaseModel):
    metric: str
    current: Optional[float] = None
    previous: Optional[float] = None
    change: Optional[float] = None
    direction: str  # improving / stable / declining / insufficient_data / unknown
    higher_is_better: bool


class TrendSummaryResponse(BaseModel):
    days_analyzed: int
    health_data_points: int
    emotion_data_points: int
    overall_direction: str
    metrics: list[MetricTrend]
