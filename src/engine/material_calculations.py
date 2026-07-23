from __future__ import annotations

import pandas as pd


def build_materials_dataframe(wall_data: dict, wall_result: dict, prices: dict) -> pd.DataFrame:
    dimension = wall_data["stud_dimension"]
    price = float(prices.get(dimension, 0.0))
    rows = [
        {
            "dimensjon": dimension,
            "type del": "Ordinær stender",
            "antall": wall_result["regular_stud_count"],
            "lengde per stk": wall_data["wall_height_m"],
        },
        {
            "dimensjon": dimension,
            "type del": "Ekstra stender",
            "antall": wall_result["extra_stud_count"],
            "lengde per stk": wall_data["wall_height_m"],
        },
        {
            "dimensjon": dimension,
            "type del": "Toppsvill",
            "antall": wall_data["top_plates"],
            "lengde per stk": wall_data["wall_width_m"],
        },
        {
            "dimensjon": dimension,
            "type del": "Bunnsvill",
            "antall": wall_data["bottom_plates"],
            "lengde per stk": wall_data["wall_width_m"],
        },
    ]

    for header in wall_result["headers"]:
        rows.append(
            {
                "dimensjon": dimension,
                "type del": f"Overdekning {header['kind']}",
                "antall": 1,
                "lengde per stk": round(header["x1"] - header["x0"], 3),
            }
        )

    df = pd.DataFrame(rows)
    df["total lengde"] = df["antall"] * df["lengde per stk"]
    df["pris per meter"] = price
    df["estimert kostnad"] = df["total lengde"] * df["pris per meter"]
    return df


def summarize_materials(material_df: pd.DataFrame, waste_factor_percent: float) -> dict:
    total_length_m = float(material_df["total lengde"].sum()) if not material_df.empty else 0.0
    total_cost = float(material_df["estimert kostnad"].sum()) if not material_df.empty else 0.0
    cost_with_waste = total_cost * (1.0 + waste_factor_percent / 100.0)
    return {
        "total_length_m": total_length_m,
        "total_cost": total_cost,
        "cost_with_waste": cost_with_waste,
    }
