from __future__ import annotations

from collections import defaultdict
from typing import Any


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
    if area_m2 > 0:
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
