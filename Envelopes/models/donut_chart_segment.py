from dataclasses import dataclass


@dataclass(slots=True)
class DonutChartSegment:
    """Represents one segment of a donut chart."""

    value: int

    color: str