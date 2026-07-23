from __future__ import annotations

from src.engine.weather_simulation import WEATHER_SCENARIOS


def assess_risk(
    wall_data: dict,
    wall_result: dict,
    beam_data: dict,
    beam_result: dict,
    scenario_name: str,
) -> dict:
    scenario = WEATHER_SCENARIOS[scenario_name]
    utilization = beam_result["utilization_ratio"]
    opening_penalty = int(wall_data.get("has_door", False)) + int(wall_data.get("has_window", False))
    spacing_penalty = 0.15 if wall_data["stud_spacing_mm"] >= 600 else 0.0
    scenario_penalty = max(scenario["load_factor"] - 1.0, 0.0)
    score = utilization + opening_penalty * 0.1 + spacing_penalty + scenario_penalty

    recommendations = list(scenario["recommendations"])
    if wall_result["extra_stud_count"] == 0 and opening_penalty:
        recommendations.append("legg til ekstra stendere rundt åpninger")
    if utilization > 0.85:
        recommendations.append("bruk større dimensjon eller reduser spennvidde")

    if score <= 0.95:
        return {
            "level": "green",
            "title": "Grønn vurdering",
            "message": "Ser greit ut for en forenklet vurdering.",
            "recommendations": recommendations,
        }
    if score <= 1.35:
        return {
            "level": "yellow",
            "title": "Gul vurdering",
            "message": "Bør kontrolleres nærmere. Vurder ekstra avstivning eller større dimensjon.",
            "recommendations": recommendations,
        }
    return {
        "level": "red",
        "title": "Rød vurdering",
        "message": "Ikke anbefalt uten faglig kontroll. Beregningen indikerer høy belastning eller stor nedbøyning.",
        "recommendations": recommendations,
    }
