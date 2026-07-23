from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Opening:
    kind: str
    left_m: float
    width_m: float
    bottom_m: float
    height_m: float

    @property
    def right_m(self) -> float:
        return self.left_m + self.width_m

    @property
    def top_m(self) -> float:
        return self.bottom_m + self.height_m


def mm_to_m(value_mm: float) -> float:
    return value_mm / 1000.0


def m_to_mm(value_m: float) -> float:
    return value_m * 1000.0


def clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(value, maximum))
