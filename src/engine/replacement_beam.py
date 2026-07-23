from __future__ import annotations

from src.engine.beam_calculations import analyze_beam


def evaluate_replacement_beam(
    span_m: float,
    dragerdimensjon: str,
    materiale: str,
    line_load_kn_per_m: float,
    antall_understottelser: int,
) -> dict:
    effective_span = span_m / max(1, antall_understottelser - 1) if antall_understottelser > 1 else span_m
    beam_result = analyze_beam(
        {
            "span_m": max(effective_span, 0.5),
            "beam_dimension": dragerdimensjon,
            "material_type": materiale,
            "load_type": "jevnt fordelt last",
            "load_kg": 0.0,
            "load_kn_per_m": max(line_load_kn_per_m, 0.0),
            "beam_count": 1,
            "center_spacing_mm": 600,
            "deflection_limit": "L/300",
        }
    )

    utilization = beam_result["utilization_ratio"]
    if utilization <= 0.7:
        risk = "green"
    elif utilization <= 1.0:
        risk = "yellow"
    else:
        risk = "red"

    return {
        "effective_span_m": effective_span,
        "risk_level": risk,
        "forenklet_estimat": True,
        **beam_result,
    }
