from __future__ import annotations


def apply_load_factor(base_load: float, load_factor: float) -> float:
    return base_load * load_factor


def combine_loads(*loads: float) -> float:
    return sum(loads)
