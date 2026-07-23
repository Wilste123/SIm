from __future__ import annotations

from typing import List

from src.data.default_prices import DEFAULT_PRICES_PER_METER
from src.data.materials import WOOD_DIMENSIONS
from src.engine.geometry import Opening, clamp


def _collect_openings(wall_data: dict) -> List[Opening]:
    openings: List[Opening] = []
    if wall_data.get("has_door"):
        openings.append(
            Opening(
                kind="door",
                left_m=clamp(wall_data["door_left_m"], 0.0, wall_data["wall_width_m"]),
                width_m=wall_data["door_width_m"],
                bottom_m=0.0,
                height_m=min(wall_data["door_height_m"], wall_data["wall_height_m"]),
            )
        )
    if wall_data.get("has_window"):
        openings.append(
            Opening(
                kind="window",
                left_m=clamp(wall_data["window_left_m"], 0.0, wall_data["wall_width_m"]),
                width_m=wall_data["window_width_m"],
                bottom_m=clamp(wall_data["window_bottom_m"], 0.0, wall_data["wall_height_m"]),
                height_m=wall_data["window_height_m"],
            )
        )
    return openings


def generate_wall_layout(wall_data: dict) -> dict:
    wall_width_m = wall_data["wall_width_m"]
    wall_height_m = wall_data["wall_height_m"]
    stud_spacing_m = wall_data["stud_spacing_mm"] / 1000.0
    stud_dimension = wall_data["stud_dimension"]
    stud_width_m = WOOD_DIMENSIONS[stud_dimension]["width_mm"] / 1000.0
    price_per_meter = DEFAULT_PRICES_PER_METER.get(stud_dimension, 0.0)

    openings = _collect_openings(wall_data)
    regular_studs = []
    x = 0.0
    while x <= wall_width_m + 1e-9:
        center_x = x + stud_width_m / 2
        blocked = any(opening.left_m < center_x < opening.right_m for opening in openings)
        if not blocked:
            regular_studs.append(round(min(x, max(wall_width_m - stud_width_m, 0.0)), 3))
        x += stud_spacing_m
    regular_studs.extend([0.0, round(max(wall_width_m - stud_width_m, 0.0), 3)])
    regular_studs = sorted({round(pos, 3) for pos in regular_studs})

    extra_studs = []
    headers = []
    for opening in openings:
        left_outer = round(max(opening.left_m - stud_width_m, 0.0), 3)
        left_inner = round(opening.left_m, 3)
        right_inner = round(min(opening.right_m - stud_width_m, wall_width_m - stud_width_m), 3)
        right_outer = round(min(opening.right_m, wall_width_m - stud_width_m), 3)
        extra_studs.extend([left_outer, left_inner, right_inner, right_outer])
        headers.append(
            {
                "kind": opening.kind,
                "x0": opening.left_m,
                "x1": min(opening.right_m, wall_width_m),
                "y0": min(opening.top_m, wall_height_m - stud_width_m),
                "y1": min(opening.top_m + stud_width_m, wall_height_m),
            }
        )
    extra_studs = sorted({pos for pos in extra_studs if 0.0 <= pos <= wall_width_m - stud_width_m + 1e-9})

    top_plate_length_m = wall_width_m * wall_data["top_plates"]
    bottom_plate_length_m = wall_width_m * wall_data["bottom_plates"]
    total_timber_m = (
        len(regular_studs) * wall_height_m
        + len(extra_studs) * wall_height_m
        + top_plate_length_m
        + bottom_plate_length_m
        + sum(header["x1"] - header["x0"] for header in headers)
    )

    return {
        "stud_width_m": stud_width_m,
        "openings": openings,
        "headers": headers,
        "regular_studs": regular_studs,
        "extra_studs": extra_studs,
        "regular_stud_count": len(regular_studs),
        "extra_stud_count": len(extra_studs),
        "top_plate_length_m": top_plate_length_m,
        "bottom_plate_length_m": bottom_plate_length_m,
        "total_timber_m": total_timber_m,
        "estimated_cost": total_timber_m * price_per_meter,
    }
