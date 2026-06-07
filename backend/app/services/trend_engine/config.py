"""Metric definitions and threshold configuration."""

from dataclasses import dataclass


@dataclass
class MetricDef:
    """Definition of a single trendable metric."""
    key: str
    label_en: str
    higher_is_better: bool
    threshold: float
    source: str  # 'health' or 'emotion'
    field: str  # column name in the DB model


METRICS: dict[str, MetricDef] = {
    "health_score": MetricDef(
        key="health_score",
        label_en="Health Score",
        higher_is_better=True,
        threshold=5.0,
        source="health",
        field="health_score",
    ),
    "stress": MetricDef(
        key="stress",
        label_en="Stress",
        higher_is_better=False,
        threshold=1.5,
        source="emotion",
        field="stress",
    ),
    "energy": MetricDef(
        key="energy",
        label_en="Energy",
        higher_is_better=True,
        threshold=1.5,
        source="emotion",
        field="energy",
    ),
    "sleep_score": MetricDef(
        key="sleep_score",
        label_en="Sleep Score",
        higher_is_better=False,
        threshold=1.0,
        source="health",
        field="sleep_score",
    ),
}


def get_metric(key: str) -> MetricDef | None:
    return METRICS.get(key)
