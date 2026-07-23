from __future__ import annotations

import json
from dataclasses import asdict
from typing import Any

from src.engine.structural_elements import BarnModel3D

DISCLAIMER_3D = (
    "Dette er en forenklet 3D-visualisering og konsekvensanalyse. "
    "Den erstatter ikke prosjektering eller vurdering fra byggingeniør. "
    "Ved fjerning eller endring av bærende konstruksjoner må løsningen "
    "kontrolleres av kvalifisert fagperson. Appen dimensjonerer ikke "
    "konstruksjoner etter Eurokode og skal ikke brukes som endelig dokumentasjon."
)


def _model_to_dict(model: BarnModel3D) -> dict[str, Any]:
    """Konverterer BarnModel3D til serialiserbar dict."""
    d = asdict(model)
    return d


def export_3d_analysis_to_json(
    model_before: BarnModel3D,
    model_after: BarnModel3D,
    scenario: dict[str, Any],
    analysis: dict[str, Any],
    lateral_stability: dict[str, Any],
) -> str:
    """Eksporterer 3D-analyse til JSON-streng.

    Inkluderer modell før og etter, scenario, last- og risikoanalyse,
    horisontal stabilitet og ansvarsfraskrivelse.
    """
    payload: dict[str, Any] = {
        "disclaimer": DISCLAIMER_3D,
        "model_before": _model_to_dict(model_before),
        "model_after": _model_to_dict(model_after),
        "scenario": scenario,
        "load_analysis": {
            "total_loads_before": analysis.get("total_loads_before", {}),
            "total_loads_after": analysis.get("total_loads_after", {}),
            "before_distribution": analysis.get("before_loads", {}),
            "after_distribution": analysis.get("after_loads", {}),
            "load_increase_detail": analysis.get("load_increase_detail", {}),
            "unresolved_load_paths": analysis.get("unresolved_load_paths", []),
            "max_increase_percent": analysis.get("max_increase_percent", 0.0),
        },
        "risk_analysis": {
            "risk_level": analysis.get("risk_level", "green"),
            "summary": analysis.get("summary", ""),
            "critical_elements": analysis.get("critical_elements", []),
            "recommendations": analysis.get("recommendations", []),
            "requires_engineer": analysis.get("requires_engineer", False),
            "requires_temporary_support": analysis.get("requires_temporary_support", False),
        },
        "lateral_stability": lateral_stability,
        "assumptions": model_before.assumptions,
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)
