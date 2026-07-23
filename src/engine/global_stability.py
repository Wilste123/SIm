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


# ─── 3D horisontal stabilitet ─────────────────────────────────────────────────

from src.engine.structural_elements import BarnModel3D  # noqa: E402

WALL_TYPES_3D = {"outer_wall", "inner_bearing_wall", "non_bearing_wall"}


def assess_3d_lateral_stability(
    model_before: BarnModel3D,
    model_after: BarnModel3D,
    scenario: dict,
    inputs: dict,
) -> dict:
    """Vurderer forenklet horisontal stabilitet i 3D-modellen etter endring.

    Returnerer risikonivå, funn og anbefalinger. Alle resultater er
    forenklede estimater og skal ikke brukes som prosjekteringsgrunnlag.
    """
    findings: list[str] = []
    recommendations: list[str] = []

    selected_id = scenario.get("selected_element_id")
    action = scenario.get("action", "behold")
    vindscenario = inputs.get("vindscenario", "normal")

    # Finn fjernet element
    removed_elem = None
    if selected_id and action == "fjern":
        for elem in model_before.elements:
            if elem.id == selected_id:
                removed_elem = elem
                break

    if removed_elem is not None:
        if removed_elem.provides_lateral_stability:
            findings.append(
                f"Fjernet element «{removed_elem.name}» bidrar til horisontal avstivning."
            )
            recommendations.append("Undersøk om veggen fungerer som avstivende skive.")

        if removed_elem.element_type in WALL_TYPES_3D:
            findings.append("Fjerning av vegg kan redusere byggets sideveis stivhet.")
            recommendations.append(
                "Kontroller innfesting mot tak/gulv og vurder kryssavstivning."
            )

    # Kontroller gjenværende avstivende vegger
    active_walls = [
        e for e in model_after.elements
        if e.element_type in WALL_TYPES_3D and e.status != "removed"
    ]
    long_open_limit = max(model_after.length_m * 0.55, 8.0)
    for wall in active_walls:
        if wall.length >= long_open_limit or wall.width >= long_open_limit:
            findings.append("Bygget har lange åpne veggflater som kan gi redusert sideveis stabilitet.")
            recommendations.append("Vurder kryssavstivning eller ekstra stive veggskiver.")
            break

    # Søylerekker uten tverravstivning
    col_elements = [
        e for e in model_after.elements
        if e.element_type in {"column", "column_row"} and e.status != "removed"
    ]
    lateral_walls = [
        e for e in model_after.elements
        if e.provides_lateral_stability and e.element_type in WALL_TYPES_3D and e.status != "removed"
    ]
    if col_elements and not lateral_walls:
        findings.append("Søyler mangler tverravstivende vegger – mulig redusert stabilitet.")
        recommendations.append("Kontroller tverravstivning av søylerekke.")

    # Vind
    if vindscenario in {"høy", "storm"} and (action == "fjern" or findings):
        findings.append(
            f"Vindscenario er «{vindscenario}» – økt usikkerhet for sideveis stabilitet."
        )
        recommendations.append(
            "Ved høy vind/storm bør horisontal avstivning kontrolleres faglig før tiltak."
        )

    if not findings:
        return {
            "risk_level": "green",
            "findings": ["Ingen tydelig indikasjon på redusert horisontal stabilitet."],
            "recommendations": ["Bekreft likevel avstivningsprinsipp med fagperson før inngrep."],
        }

    if vindscenario == "storm" or len(findings) >= 3 or (removed_elem and removed_elem.provides_lateral_stability):
        level = "red"
    else:
        level = "yellow"

    recommendations.append("Dokumenter eksisterende konstruksjon med bilder før tiltak.")

    return {
        "risk_level": level,
        "findings": findings,
        "recommendations": list(dict.fromkeys(recommendations)),
    }
