from __future__ import annotations

from src.data.materials import MATERIAL_TYPES, WOOD_DIMENSIONS


def kg_to_newton(load_kg: float) -> float:
    return load_kg * 9.81


def kn_to_n(load_kn: float) -> float:
    return load_kn * 1000.0


def mm_to_m(value_mm: float) -> float:
    return value_mm / 1000.0


def calculate_beam_moment_uniform_load(q_n_per_m: float, span_m: float) -> float:
    return q_n_per_m * span_m**2 / 8.0


def calculate_beam_shear_uniform_load(q_n_per_m: float, span_m: float) -> float:
    return q_n_per_m * span_m / 2.0


def calculate_beam_moment_point_load(point_load_n: float, span_m: float) -> float:
    return point_load_n * span_m / 4.0


def calculate_beam_shear_point_load(point_load_n: float) -> float:
    return point_load_n / 2.0


def calculate_deflection_uniform_load(q_n_per_m: float, span_m: float, e_pa: float, inertia_m4: float) -> float:
    return 5.0 * q_n_per_m * span_m**4 / (384.0 * e_pa * inertia_m4)


def calculate_deflection_point_load(point_load_n: float, span_m: float, e_pa: float, inertia_m4: float) -> float:
    return point_load_n * span_m**3 / (48.0 * e_pa * inertia_m4)


def get_section_properties(dimension: str) -> dict:
    dims = WOOD_DIMENSIONS[dimension]
    width_m = dims["width_mm"] / 1000.0
    height_m = dims["height_mm"] / 1000.0
    inertia_m4 = width_m * height_m**3 / 12.0
    section_modulus_m3 = width_m * height_m**2 / 6.0
    return {
        "width_m": width_m,
        "height_m": height_m,
        "inertia_m4": inertia_m4,
        "section_modulus_m3": section_modulus_m3,
    }


def _parse_deflection_limit(deflection_limit: str) -> float:
    denominator = float(deflection_limit.split("/")[-1])
    return denominator


def analyze_beam(beam_data: dict) -> dict:
    span_m = beam_data["span_m"]
    beam_count = max(int(beam_data["beam_count"]), 1)
    material = MATERIAL_TYPES[beam_data["material_type"]]
    section = get_section_properties(beam_data["beam_dimension"])
    limit_denominator = _parse_deflection_limit(beam_data["deflection_limit"])
    allowed_deflection_m = span_m / limit_denominator

    if beam_data["load_type"] == "punktlast midt på":
        point_load_n = kg_to_newton(beam_data["load_kg"]) / beam_count
        moment_nm = calculate_beam_moment_point_load(point_load_n, span_m)
        shear_n = calculate_beam_shear_point_load(point_load_n)
        deflection_m = calculate_deflection_point_load(
            point_load_n, span_m, material["e_modulus_pa"], section["inertia_m4"]
        )
    else:
        q_n_per_m = kn_to_n(beam_data["load_kn_per_m"]) / beam_count
        moment_nm = calculate_beam_moment_uniform_load(q_n_per_m, span_m)
        shear_n = calculate_beam_shear_uniform_load(q_n_per_m, span_m)
        deflection_m = calculate_deflection_uniform_load(
            q_n_per_m, span_m, material["e_modulus_pa"], section["inertia_m4"]
        )

    bending_stress_pa = moment_nm / section["section_modulus_m3"]
    utilization_ratio = max(
        bending_stress_pa / material["bending_strength_pa"],
        deflection_m / allowed_deflection_m if allowed_deflection_m else 0.0,
    )

    if utilization_ratio <= 0.7:
        summary = "Ser greit ut for en forenklet vurdering. Kontroller likevel detaljer før bygging."
    elif utilization_ratio <= 1.0:
        summary = "Bør vurderes nærmere. Vurder større dimensjon, kortere spenn eller flere bjelker."
    else:
        summary = "Ikke anbefalt uten faglig kontroll. Beregningen indikerer høy belastning eller stor nedbøyning."

    return {
        "moment_kNm": moment_nm / 1000.0,
        "shear_kN": shear_n / 1000.0,
        "deflection_mm": deflection_m * 1000.0,
        "allowed_deflection_mm": allowed_deflection_m * 1000.0,
        "utilization_ratio": utilization_ratio,
        "bending_stress_mpa": bending_stress_pa / 1_000_000.0,
        "summary": summary,
    }
