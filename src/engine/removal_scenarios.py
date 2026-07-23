from __future__ import annotations

from copy import deepcopy
from typing import Any

from src.engine.load_paths import build_load_distribution
from src.engine.support_reactions import calculate_reaction_increase
from src.engine.structural_elements import BarnModel3D, StructuralElement


MAX_CONSERVATIVE_SPAN_M = 7.0


def apply_removal_scenario(model: dict[str, Any], scenario: dict[str, Any]) -> dict[str, Any]:
    after = deepcopy(model)
    remove_ids = set(scenario.get("remove_support_ids") or [])

    for line in after.get("support_lines", []):
        if line.get("id") in remove_ids:
            line["status"] = "fjernes"
    for point in after.get("point_supports", []):
        if point.get("id") in remove_ids:
            point["status"] = "fjernes"

    if scenario.get("proposed_replacement") in {"drager", "limtredrager", "ståldrager", "trebjelke"}:
        span = float(scenario.get("replacement_beam_span_m", 0.0) or 0.0)
        building = after.get("building", {})
        beam_y = float(building.get("bredde_m", 0.0)) / 2.0
        after.setdefault("support_lines", []).append(
            {
                "id": "ny_drager",
                "navn": "Ny foreslått drager",
                "type": "drager",
                "x_start_m": 0.0,
                "y_start_m": beam_y,
                "x_end_m": min(span or float(building.get("lengde_m", 0.0)), float(building.get("lengde_m", 0.0))),
                "y_end_m": beam_y,
                "etasje": 1,
                "baerer_tak": True,
                "baerer_bjelkelag": True,
                "antatt_baereevne_kn": None,
                "status": "ny",
                "length_m": span,
            }
        )

    return after


def estimate_new_span_after_removal(model: dict[str, Any], removed_support_id: str) -> float:
    support_lines = model.get("support_lines", [])
    removed = next((line for line in support_lines if line.get("id") == removed_support_id), None)
    if removed:
        same_axis = [
            line
            for line in support_lines
            if line.get("id") != removed_support_id and line.get("status") != "fjernes" and line.get("type") == removed.get("type")
        ]
        if not same_axis:
            dx = abs(removed.get("x_end_m", 0.0) - removed.get("x_start_m", 0.0))
            dy = abs(removed.get("y_end_m", 0.0) - removed.get("y_start_m", 0.0))
            if dx >= dy:
                return float(model.get("building", {}).get("bredde_m", 0.0))
            return float(model.get("building", {}).get("lengde_m", 0.0))
        removed_center = (removed.get("y_start_m", 0.0) + removed.get("y_end_m", 0.0)) / 2.0
        distances = [
            abs(((line.get("y_start_m", 0.0) + line.get("y_end_m", 0.0)) / 2.0) - removed_center)
            for line in same_axis
        ]
        if not distances:
            return 0.0
        return min(distances) * 2.0

    point_supports = model.get("point_supports", [])
    removed_point = next((point for point in point_supports if point.get("id") == removed_support_id), None)
    if removed_point:
        active_points = [point for point in point_supports if point.get("id") != removed_support_id and point.get("status") != "fjernes"]
        if not active_points:
            return max(model.get("building", {}).get("lengde_m", 0.0), 0.0)
        nearest = min(abs(point.get("x_m", 0.0) - removed_point.get("x_m", 0.0)) for point in active_points)
        return nearest * 2.0

    return 0.0


def _support_map(model: dict[str, Any]) -> dict[str, dict[str, Any]]:
    supports: dict[str, dict[str, Any]] = {}
    supports.update({line["id"]: line for line in model.get("support_lines", [])})
    supports.update({point["id"]: point for point in model.get("point_supports", [])})
    return supports


def assess_removal_risk(before_model: dict[str, Any], after_model: dict[str, Any], scenario: dict[str, Any]) -> dict[str, Any]:
    """Vurderer forenklet konsekvens ved fjerning av støtte.

    Returnerer risk_level (green/yellow/red), funn, anbefalinger og støttebehov for midlertidig understøtting.
    """
    before_dist = before_model.get("load_distribution") or build_load_distribution(
        before_model, before_model.get("assumptions", {}).get("usikkerhetsfaktor", 1.0)
    )
    after_dist = after_model.get("load_distribution") or build_load_distribution(
        after_model, after_model.get("assumptions", {}).get("usikkerhetsfaktor", 1.0)
    )

    reaction_changes = calculate_reaction_increase(
        {**before_dist.get("line_reactions_kn", {}), **before_dist.get("point_reactions_kn", {})},
        {**after_dist.get("line_reactions_kn", {}), **after_dist.get("point_reactions_kn", {})},
    )

    critical_findings: list[str] = []
    recommendations: list[str] = []

    remove_ids = scenario.get("remove_support_ids") or []
    supports = _support_map(before_model)
    bearing_removed = any(
        support_id in supports
        and (
            supports[support_id].get("baerer_tak")
            or supports[support_id].get("baerer_bjelkelag")
            or supports[support_id].get("type") in {"søylerekke", "innervegg", "yttervegg", "drager"}
        )
        for support_id in remove_ids
    )

    level = "green"
    replacement = (scenario.get("proposed_replacement") or "ingen").lower()

    if bearing_removed and replacement in {"ingen", "ukjent", ""}:
        level = "red"
        critical_findings.append("Bærende linje/punkt fjernes uten tydelig erstatning.")
        recommendations.append("Ikke fjern bærende konstruksjon uten prosjektert erstatningsløsning.")

    unresolved = after_dist.get("unresolved_load_paths", [])
    if unresolved:
        level = "red"
        critical_findings.append("Taklast eller gulvlast mangler tydelig lastvei etter endring.")
        recommendations.append("Avklar komplett lastvei fra tak/gulv ned til fundament før tiltak.")

    if not before_model.get("load_areas") or not before_model.get("support_lines"):
        level = "red"
        critical_findings.append("Mangler datagrunnlag. Resultatet er kun en grov indikasjon.")

    max_increase = max((change["increase_percent"] for change in reaction_changes.values()), default=0.0)
    if max_increase > 50.0:
        level = "red"
        critical_findings.append("Lastøkning på gjenværende støtte er over 50 %.")
        recommendations.append("Kontroller punktlaster og understøtting før riving/ombygging.")
    elif max_increase >= 15.0 and level != "red":
        level = "yellow"
        critical_findings.append("Lastøkning på gjenværende støtte er mellom 15 % og 50 %.")

    spans = [estimate_new_span_after_removal(before_model, support_id) for support_id in remove_ids]
    new_span = max(spans, default=0.0)
    # Konservativ spenn-grense i MVP for å flagge mulig kritisk endring tidlig.
    if new_span > MAX_CONSERVATIVE_SPAN_M:
        level = "red"
        critical_findings.append("Nytt estimert spenn overstiger konservativ anbefalt grense.")
        recommendations.append("Vurder ny drager/støtte med faglig dimensjonering.")
    elif new_span >= 5.0 and level == "green":
        level = "yellow"
        critical_findings.append("Nytt spenn er moderat/stort og bør kontrolleres faglig.")

    removed_point = any(supports.get(support_id, {}).get("type") in {"søylerekke", "drager"} for support_id in remove_ids)
    if removed_point and replacement in {"ingen", "ukjent", ""}:
        level = "red"
        critical_findings.append("Søyle/stolpe som kan bære drager fjernes uten ny understøttelse.")

    if replacement in {"drager", "limtredrager", "ståldrager", "trebjelke"} and level == "green":
        level = "yellow"
        critical_findings.append("Bærelinje erstattes med drager, men dimensjon er ikke validert i detalj.")

    if before_model.get("building", {}).get("konstruksjonstype") == "ukjent" and level == "green":
        level = "yellow"
        critical_findings.append("Konstruksjonstype er ukjent, som gir høyere usikkerhet i vurderingen.")

    if scenario.get("scenario_name") == "lag større åpning i bærevegg" and level == "green":
        level = "yellow"
        critical_findings.append("Åpning i bærevegg kan gi økt lokal risiko og bør kontrolleres.")

    if not critical_findings:
        critical_findings.append("Endringen ser begrenset ut i denne forenklede vurderingen.")

    if not recommendations:
        recommendations = [
            "Dokumenter eksisterende konstruksjon før tiltak.",
            "Kontroller løsning med kvalifisert byggingeniør ved usikkerhet.",
        ]

    requires_temp = bool(bearing_removed and level in {"yellow", "red"})
    if requires_temp:
        recommendations.append("Etabler midlertidig understøtting før demontering av bærende element.")

    title_map = {
        "green": "Grønn indikasjon",
        "yellow": "Gul indikasjon",
        "red": "Rød indikasjon",
    }

    summary_map = {
        "green": "Forenklet analyse indikerer lav konsekvens, men tiltak bør fortsatt kontrolleres.",
        "yellow": "Forenklet analyse indikerer mulig risiko. Løsning bør kontrolleres faglig.",
        "red": "Forenklet analyse indikerer høy risiko. Tiltak krever faglig vurdering før gjennomføring.",
    }

    return {
        "risk_level": level,
        "title": title_map[level],
        "summary": summary_map[level],
        "critical_findings": critical_findings,
        "recommendations": recommendations,
        "requires_engineer": level in {"yellow", "red"},
        "requires_temporary_support": requires_temp,
        "reaction_increase": reaction_changes,
        "new_span_m": new_span,
        "unresolved_load_paths": unresolved,
    }


# ─── 3D endringsscenario ─────────────────────────────────────────────────────

def apply_change_scenario(model: BarnModel3D, scenario: dict[str, Any]) -> BarnModel3D:
    """Kopierer 3D-modellen og anvender valgt endringsscenario.

    Elementer slettes ikke fysisk – de får oppdatert status slik at de
    kan vises rødt/blått i 3D-visningen. Dette er et forenklet estimat.
    """
    from dataclasses import replace as dc_replace

    after = deepcopy(model)
    selected_id = scenario.get("selected_element_id")
    action = scenario.get("action", "behold")

    # Oppdater status på valgt element
    for idx, elem in enumerate(after.elements):
        if elem.id != selected_id:
            continue

        if action == "fjern":
            after.elements[idx] = dc_replace(elem, status="removed")
            if selected_id not in after.removed_elements:
                after.removed_elements.append(selected_id)

        elif action == "forsterk":
            after.elements[idx] = dc_replace(elem, status="reinforced")

        elif action == "erstatt med drager":
            after.elements[idx] = dc_replace(elem, status="removed")
            if selected_id not in after.removed_elements:
                after.removed_elements.append(selected_id)
            repl = scenario.get("replacement", {})
            new_beam = _make_replacement_beam(elem, repl, after)
            after.new_elements.append(new_beam)
            after.elements.append(new_beam)
            if repl.get("legg_til_soyle_under"):
                new_col = _make_support_column(elem, after)
                after.new_elements.append(new_col)
                after.elements.append(new_col)

        elif action == "legg til søyle under":
            new_col = _make_support_column(elem, after)
            after.new_elements.append(new_col)
            after.elements.append(new_col)

        elif action == "marker som bærende":
            after.elements[idx] = dc_replace(elem, is_bearing=True)

        elif action == "marker som ikke-bærende":
            after.elements[idx] = dc_replace(elem, is_bearing=False)

        break

    return after


def _make_replacement_beam(
    original: StructuralElement,
    repl: dict[str, Any],
    model: BarnModel3D,
) -> StructuralElement:
    """Lager ny drager-StructuralElement basert på erstatningsinput."""
    h_mm = float(repl.get("drager_hoyde_mm", 300))
    b_mm = float(repl.get("drager_bredde_mm", 90))
    mat = str(repl.get("drager_materiale", "limtre"))
    span = float(repl.get("spennvidde_m") or model.length_m)

    beam_h = h_mm / 1000.0
    beam_w = b_mm / 1000.0
    beam_z = original.z + original.height - beam_h

    return StructuralElement(
        id=f"ny_drager_{original.id}",
        name=f"Ny drager (erstatter {original.name})",
        element_type="beam",
        x=original.x,
        y=original.y + original.width / 2.0 - beam_w / 2.0,
        z=beam_z,
        length=min(span, model.length_m),
        width=beam_w,
        height=beam_h,
        material=mat,
        is_bearing=True,
        carries_roof=original.carries_roof,
        carries_floor=original.carries_floor,
        status="new",
    )


def _make_support_column(
    above_element: StructuralElement,
    model: BarnModel3D,
) -> StructuralElement:
    """Lager ny støttesøyle under et element."""
    col_size = 0.2
    cx = above_element.x + above_element.length / 2.0
    cy = above_element.y + above_element.width / 2.0
    return StructuralElement(
        id=f"ny_soyle_{above_element.id}",
        name=f"Ny søyle under {above_element.name}",
        element_type="column",
        x=cx - col_size / 2.0,
        y=cy - col_size / 2.0,
        z=0.0,
        length=col_size,
        width=col_size,
        height=above_element.z,
        material=above_element.material,
        is_bearing=True,
        carries_roof=above_element.carries_roof,
        carries_floor=above_element.carries_floor,
        status="new",
    )
