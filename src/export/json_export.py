from __future__ import annotations

import json
from typing import Any

import pandas as pd


def build_project_payload(
    project_data: dict,
    wall_data: dict,
    wall_result: dict,
    beam_data: dict,
    beam_result: dict,
    scenario_name: str,
    scenario: dict,
    risk: dict,
    material_df: pd.DataFrame,
    material_summary: dict,
    barn_analysis: dict[str, Any] | None = None,
) -> dict[str, Any]:
    wall_result_export = {
        key: value
        for key, value in wall_result.items()
        if key not in {"openings"}
    }
    wall_result_export["openings"] = [opening.__dict__ for opening in wall_result["openings"]]

    payload = {
        "project": project_data,
        "wall_input": wall_data,
        "wall_result": wall_result_export,
        "beam_input": beam_data,
        "beam_result": beam_result,
        "scenario_name": scenario_name,
        "scenario": scenario,
        "risk": risk,
        "material_list": material_df.to_dict(orient="records"),
        "material_summary": material_summary,
    }
    if barn_analysis is not None:
        payload["barn_system_analysis"] = barn_analysis
    return payload


def export_project_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2)
