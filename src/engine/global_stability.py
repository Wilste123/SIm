from __future__ import annotations

from typing import Any


def assess_lateral_stability(model: dict[str, Any], scenario: dict[str, Any]) -> dict[str, Any]:
    findings: list[str] = []
    recommendations: list[str] = []

    windscenario = model.get("assumptions", {}).get("vindscenario", "normal")
    remove_ids = set(scenario.get("remove_support_ids") or [])
    support_lines = model.get("support_lines", [])
    building = model.get("building", {})

    removed_lines = [line for line in support_lines if line.get("id") in remove_ids]
    removed_wall_like = [line for line in removed_lines if line.get("type") in {"yttervegg", "innervegg"}]

    if removed_wall_like:
        findings.append("Fjernet element kan også bidra til horisontal avstivning.")
        recommendations.append("Undersøk om veggen fungerer som avstivende skive eller del av vindavstivning.")

    active_wall_lines = [
        line
        for line in support_lines
        if line.get("status") != "fjernes" and line.get("id") not in remove_ids and line.get("type") in {"yttervegg", "innervegg"}
    ]
    open_length_limit = max(float(building.get("lengde_m", 0.0)) * 0.55, 8.0)
    for wall in active_wall_lines:
        line_length = ((wall.get("x_end_m", 0.0) - wall.get("x_start_m", 0.0)) ** 2 + (wall.get("y_end_m", 0.0) - wall.get("y_start_m", 0.0)) ** 2) ** 0.5
        if line_length > open_length_limit:
            findings.append("Bygget har lange åpne veggflater som kan gi svakere sideveis stabilitet.")
            recommendations.append("Vurder kryssavstivning eller ekstra stive veggskiver.")
            break

    if windscenario in {"høy", "storm"} and remove_ids:
        findings.append("Vindscenario er høyt, og endring i bærende system øker usikkerheten for sideveis stabilitet.")
        recommendations.append("Ved høy vind/storm bør avstivning kontrolleres faglig før tiltak.")

    if not findings:
        return {
            "risk_level": "green",
            "findings": ["Ingen tydelig indikasjon på redusert horisontal stabilitet i denne forenklede vurderingen."],
            "recommendations": ["Bekreft likevel avstivningsprinsipp før inngrep."],
        }

    if windscenario == "storm" or len(findings) >= 2:
        level = "red"
    else:
        level = "yellow"

    return {
        "risk_level": level,
        "findings": findings,
        "recommendations": recommendations,
    }
