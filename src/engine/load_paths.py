from __future__ import annotations

from collections import defaultdict
from typing import Any


# Minste effektive areal (0.5 m²) for å unngå ekstrem/intetsigende lastintensitet ved svært små modellgeometrier.
MIN_EFFECTIVE_AREA_M2 = 0.5


def calculate_total_area_load(area_m2: float, load_kn_per_m2: float) -> float:
    return max(area_m2, 0.0) * max(load_kn_per_m2, 0.0)


def distribute_load_to_supports(total_load_kn: float, support_ids: list[str]) -> dict[str, float]:
    if total_load_kn <= 0 or not support_ids:
        return {}
    share = total_load_kn / len(support_ids)
    return {support_id: share for support_id in support_ids}


def _line_center_x(line: dict[str, Any]) -> float:
    return (float(line["x_start_m"]) + float(line["x_end_m"])) / 2.0


def estimate_tributary_width(building_width_m: float, support_lines: list[dict[str, Any]]) -> dict[str, float]:
    if not support_lines:
        return {}
    sorted_lines = sorted(support_lines, key=_line_center_x)
    centers = [_line_center_x(line) for line in sorted_lines]
    boundaries = [0.0]
    for index in range(len(centers) - 1):
        boundaries.append((centers[index] + centers[index + 1]) / 2.0)
    boundaries.append(max(building_width_m, 0.0))

    tributary_widths: dict[str, float] = {}
    for index, line in enumerate(sorted_lines):
        left = boundaries[index]
        right = boundaries[index + 1]
        tributary_widths[line["id"]] = max(right - left, 0.0)
    return tributary_widths


def calculate_line_load_kn_per_m(area_load_kn_m2: float, tributary_width_m: float) -> float:
    return max(area_load_kn_m2, 0.0) * max(tributary_width_m, 0.0)


def _active_support_ids(model: dict[str, Any]) -> set[str]:
    line_ids = {line["id"] for line in model.get("support_lines", []) if line.get("status") != "fjernes"}
    point_ids = {point["id"] for point in model.get("point_supports", []) if point.get("status") != "fjernes"}
    return line_ids | point_ids


def detect_unresolved_load_paths(model: dict[str, Any]) -> list[str]:
    unresolved: list[str] = []
    active_ids = _active_support_ids(model)

    for area in model.get("load_areas", []):
        supports = area.get("supported_by") or []
        if not supports:
            unresolved.append(f"{area.get('navn', area.get('id', 'lastflate'))} mangler støtte")
            continue

        available_supports = [support_id for support_id in supports if support_id in active_ids]
        if not available_supports:
            unresolved.append(
                f"{area.get('navn', area.get('id', 'lastflate'))} mangler tydelig lastvei til eksisterende støtte"
            )

    return unresolved


def build_load_distribution(model: dict[str, Any], uncertainty_factor: float = 1.0) -> dict[str, Any]:
    """Fordeler areallaster forenklet på støtte-IDer med lik andel per lastflate.

    uncertainty_factor skalerer laster konservativt (>=1.0). Returnerer totaler, reaksjoner, linjelast og uavklarte lastveier.
    """
    totals_by_type: dict[str, float] = defaultdict(float)
    support_totals: dict[str, float] = defaultdict(float)

    factor = max(float(uncertainty_factor), 1.0)
    for area in model.get("load_areas", []):
        load = calculate_total_area_load(area.get("area_m2", 0.0), area.get("load_kn_per_m2", 0.0)) * factor
        totals_by_type[area.get("load_type", "annet")] += load
        for support_id, support_load in distribute_load_to_supports(load, area.get("supported_by") or []).items():
            support_totals[support_id] += support_load

    line_by_id = {line["id"]: line for line in model.get("support_lines", [])}
    point_by_id = {point["id"]: point for point in model.get("point_supports", [])}

    line_reactions: dict[str, float] = {}
    point_reactions: dict[str, float] = {}
    for support_id, reaction in support_totals.items():
        if support_id in line_by_id and line_by_id[support_id].get("status") != "fjernes":
            line_reactions[support_id] = reaction
        if support_id in point_by_id and point_by_id[support_id].get("status") != "fjernes":
            point_reactions[support_id] = reaction

    tributary = estimate_tributary_width(
        model.get("building", {}).get("bredde_m", 0.0),
        [line for line in model.get("support_lines", []) if line.get("status") != "fjernes"],
    )

    line_loads_kn_per_m: dict[str, float] = {}
    area_total_kn_m2 = 0.0
    area_m2 = model.get("building", {}).get("lengde_m", 0.0) * model.get("building", {}).get("bredde_m", 0.0)
    if area_m2 >= MIN_EFFECTIVE_AREA_M2:
        area_total_kn_m2 = sum(totals_by_type.values()) / area_m2

    for support_id, width in tributary.items():
        line_loads_kn_per_m[support_id] = calculate_line_load_kn_per_m(area_total_kn_m2, width)

    return {
        "totals_by_type": dict(totals_by_type),
        "total_load_kn": sum(totals_by_type.values()),
        "line_reactions_kn": line_reactions,
        "point_reactions_kn": point_reactions,
        "line_loads_kn_per_m": line_loads_kn_per_m,
        "unresolved_load_paths": detect_unresolved_load_paths(model),
    }


# ─── 3D lastanalyse ───────────────────────────────────────────────────────────

from src.engine.structural_elements import BarnModel3D, StructuralElement  # noqa: E402


def calculate_total_loads(model: BarnModel3D, inputs: dict) -> dict:
    """Beregner totale laster for tak og gulv basert på input. Forenklet estimat."""
    factor = max(float(inputs.get("usikkerhetsfaktor", 1.2)), 1.0)
    tak_areal = model.length_m * model.width_m
    gulv_areal = tak_areal * model.floors

    total_taklast = tak_areal * (
        float(inputs.get("egenlast_tak_kn_m2", 0.8))
        + float(inputs.get("snolast_kn_m2", 1.5))
    ) * factor

    total_gulvlast = gulv_areal * (
        float(inputs.get("gulvlast_kn_m2", 2.0))
        + float(inputs.get("lagerlast_kn_m2", 1.0))
    ) * factor

    return {
        "tak_areal_m2": tak_areal,
        "gulv_areal_m2": gulv_areal,
        "total_taklast_kn": total_taklast,
        "total_gulvlast_kn": total_gulvlast,
        "usikkerhetsfaktor": factor,
        "forenklet_estimat": True,
    }


def distribute_loads_to_bearing_elements(model: BarnModel3D, total_loads: dict) -> dict:
    """Fordeler tak- og gulvlast jevnt på aktive bærende elementer."""
    roof_supports = [
        e for e in model.elements
        if e.carries_roof and e.status != "removed"
    ]
    floor_supports = [
        e for e in model.elements
        if e.carries_floor and e.status != "removed"
    ]

    total_tak = total_loads.get("total_taklast_kn", 0.0)
    total_gulv = total_loads.get("total_gulvlast_kn", 0.0)

    tak_per = total_tak / len(roof_supports) if roof_supports else 0.0
    gulv_per = total_gulv / len(floor_supports) if floor_supports else 0.0

    loads: dict[str, float] = {}
    for elem in model.elements:
        if elem.status == "removed":
            continue
        v = 0.0
        if elem.carries_roof:
            v += tak_per
        if elem.carries_floor:
            v += gulv_per
        if v > 0:
            loads[elem.id] = round(v, 2)

    return loads


def detect_unresolved_load_paths_3d(model: BarnModel3D) -> list[str]:
    """Sjekker om taklast og gulvlast har aktive bærelinjer. Forenklet kontroll."""
    unresolved: list[str] = []

    roof_supports = [
        e for e in model.elements
        if e.carries_roof and e.status != "removed"
    ]
    floor_supports = [
        e for e in model.elements
        if e.carries_floor and e.status != "removed"
    ]

    if not roof_supports:
        unresolved.append("Taklast mangler tydelig lastvei – ingen aktiv bærelinje/søyle bærer tak.")
    if model.floors > 1 and not floor_supports:
        unresolved.append("Gulvlast i etasje mangler lastvei – ingen aktiv bærelinje/søyle bærer gulv.")

    return unresolved


def calculate_load_increase(before_loads: dict, after_loads: dict) -> dict:
    """Beregner prosentvis lastøkning per element. Forenklet estimat."""
    increases: dict[str, dict] = {}
    all_ids = set(before_loads) | set(after_loads)
    for eid in all_ids:
        before = before_loads.get(eid, 0.0)
        after = after_loads.get(eid, 0.0)
        if before > 0:
            pct = (after - before) / before * 100.0
            label = f"{pct:+.1f} %"
        elif after > 0:
            pct = float("inf")
            label = "ny last"
        else:
            pct = 0.0
            label = "0 %"
        increases[eid] = {
            "before_kn": round(before, 2),
            "after_kn": round(after, 2),
            "increase_percent": round(pct, 1) if pct != float("inf") else 9999.0,
            "label": label,
        }
    return increases


def analyze_load_paths_before_after(
    model_before: BarnModel3D,
    model_after: BarnModel3D,
    inputs: dict,
) -> dict:
    """Analyserer lastveier før og etter endring. Returnerer forenklet oversikt."""
    total_loads_before = calculate_total_loads(model_before, inputs)
    total_loads_after = calculate_total_loads(model_after, inputs)

    before_dist = distribute_loads_to_bearing_elements(model_before, total_loads_before)
    after_dist = distribute_loads_to_bearing_elements(model_after, total_loads_after)

    load_increases = calculate_load_increase(before_dist, after_dist)
    unresolved = detect_unresolved_load_paths_3d(model_after)

    max_increase = max(
        (v["increase_percent"] for v in load_increases.values() if v["increase_percent"] != 9999.0),
        default=0.0,
    )

    return {
        "total_loads_before": total_loads_before,
        "total_loads_after": total_loads_after,
        "before_distribution": before_dist,
        "after_distribution": after_dist,
        "load_increases": load_increases,
        "unresolved_load_paths": unresolved,
        "max_increase_percent": max_increase,
    }
