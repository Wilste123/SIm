from __future__ import annotations

from typing import Any

from src.engine.structural_elements import BarnModel3D, StructuralElement

WALL_THICKNESS = 0.3
COL_SIZE = 0.2
BEAM_WIDTH = 0.2
BEAM_HEIGHT = 0.3
RIDGE_BEAM_SIZE = 0.15
LOAD_ARROW_GRID = 3  # grid NxN for load arrows
LOAD_ARROW_HEIGHT_OFFSET = 0.8  # above ridge


def generate_barn_3d_model(inputs: dict[str, Any]) -> BarnModel3D:
    """Genererer en parametrisk 3D-modell av en låve basert på input-verdier.

    Returnerer en BarnModel3D med StructuralElement-objekter som representerer
    de viktigste konstruksjonsdelene. Alle resultater er forenklede estimater.
    """
    L = float(inputs.get("lengde_m", 18.0))
    W = float(inputs.get("bredde_m", 10.0))
    eaves_h = float(inputs.get("gesimshoyde_m", 3.2))
    ridge_h = float(inputs.get("monehoyde_m", 5.0))
    ridge_h = max(ridge_h, eaves_h + 0.1)
    roof_type = str(inputs.get("taktype", "saltak"))
    roof_angle = float(inputs.get("takvinkel_grader", 27.0))
    floors = int(inputs.get("antall_etasjer", 1))
    material = str(inputs.get("materialtype", "tre"))

    yttervegger_baerende = bool(inputs.get("yttervegger_baerende", True))
    har_innervegg = bool(inputs.get("har_innvendig_baerevegg", False))
    innervegg_y = float(inputs.get("innvendig_baerevegg_plassering_m", W / 2.0))
    innervegg_y = max(WALL_THICKNESS, min(innervegg_y, W - WALL_THICKNESS))

    har_soylerekke = bool(inputs.get("har_soylerekke", False))
    antall_soyler = max(1, int(inputs.get("antall_soyler", 4)))
    soylerekke_y = float(inputs.get("soylerekke_plassering_m", W / 2.0))
    soylerekke_y = max(COL_SIZE, min(soylerekke_y, W - COL_SIZE))

    har_langs_drager = bool(inputs.get("har_langsgaende_drager", False))
    har_tverr_dragere = bool(inputs.get("har_tverrgaende_dragere", False))

    egenlast = float(inputs.get("egenlast_tak_kn_m2", 0.8))
    snolast = float(inputs.get("snolast_kn_m2", 1.5))

    assumptions = [
        "Forenklet 3D-modell – ikke godkjent prosjekteringsgrunnlag.",
        f"Veggtykkelse antatt {WALL_THICKNESS} m.",
        "Lastpiler viser prinsippretning, ikke skalerte verdier.",
        "Materialegenskaper er ikke validert mot Eurokode.",
    ]

    elements: list[StructuralElement] = []

    # ── Fundament/gulvplate ──────────────────────────────────────────────────
    elements.append(StructuralElement(
        id="fundament",
        name="Gulvplate / fundament",
        element_type="foundation",
        x=0.0, y=0.0, z=-0.2,
        length=L, width=W, height=0.2,
        material="betong",
        is_bearing=True,
        carries_floor=True,
        provides_lateral_stability=True,
    ))

    # ── Yttervegger ─────────────────────────────────────────────────────────
    outer_wall_defs = [
        ("yttervegg_n", "Yttervegg nord", 0.0, 0.0, L, WALL_THICKNESS),
        ("yttervegg_s", "Yttervegg sør",  0.0, W - WALL_THICKNESS, L, WALL_THICKNESS),
        ("yttervegg_v", "Yttervegg vest", 0.0, 0.0, WALL_THICKNESS, W),
        ("yttervegg_o", "Yttervegg øst",  L - WALL_THICKNESS, 0.0, WALL_THICKNESS, W),
    ]
    for eid, ename, ex, ey, elen, ewid in outer_wall_defs:
        elements.append(StructuralElement(
            id=eid, name=ename,
            element_type="outer_wall",
            x=ex, y=ey, z=0.0,
            length=elen, width=ewid, height=eaves_h,
            material=material,
            is_bearing=yttervegger_baerende,
            carries_roof=yttervegger_baerende,
            carries_floor=yttervegger_baerende and floors > 1,
            provides_lateral_stability=True,
        ))

    # ── Innvendig bærevegg ───────────────────────────────────────────────────
    if har_innervegg:
        half_t = WALL_THICKNESS / 2.0
        elements.append(StructuralElement(
            id="innervegg_1",
            name="Innvendig bærevegg",
            element_type="inner_bearing_wall",
            x=0.0, y=innervegg_y - half_t, z=0.0,
            length=L, width=WALL_THICKNESS, height=eaves_h,
            material=material,
            is_bearing=True,
            carries_roof=True,
            carries_floor=floors > 1,
            provides_lateral_stability=True,
        ))

    # ── Søyler / stolperekke ─────────────────────────────────────────────────
    if har_soylerekke:
        half_c = COL_SIZE / 2.0
        for idx in range(antall_soyler):
            frac = (idx + 1) / (antall_soyler + 1)
            cx = L * frac
            elements.append(StructuralElement(
                id=f"soyle_{idx + 1}",
                name=f"Søyle {idx + 1}",
                element_type="column",
                x=cx - half_c, y=soylerekke_y - half_c, z=0.0,
                length=COL_SIZE, width=COL_SIZE, height=eaves_h,
                material=material,
                is_bearing=True,
                carries_roof=True,
                carries_floor=floors > 1,
            ))

    # ── Langsgående drager ───────────────────────────────────────────────────
    if har_langs_drager:
        drager_y = soylerekke_y if har_soylerekke else (innervegg_y if har_innervegg else W / 2.0)
        elements.append(StructuralElement(
            id="drager_langs",
            name="Langsgående drager",
            element_type="beam",
            x=0.0, y=drager_y - BEAM_WIDTH / 2.0, z=eaves_h - BEAM_HEIGHT,
            length=L, width=BEAM_WIDTH, height=BEAM_HEIGHT,
            material=material,
            is_bearing=True,
            carries_roof=True,
        ))

    # ── Tverrgående dragere ──────────────────────────────────────────────────
    if har_tverr_dragere:
        n_tverr = max(2, int(L / 4.0))
        for idx in range(n_tverr):
            frac = (idx + 1) / (n_tverr + 1)
            bx = L * frac - BEAM_WIDTH / 2.0
            elements.append(StructuralElement(
                id=f"drager_tverr_{idx + 1}",
                name=f"Tverrgående drager {idx + 1}",
                element_type="beam",
                x=bx, y=0.0, z=eaves_h - BEAM_HEIGHT,
                length=BEAM_WIDTH, width=W, height=BEAM_HEIGHT,
                material=material,
                is_bearing=True,
                carries_roof=True,
            ))

    # ── Takflater ─────────────────────────────────────────────────────────────
    if roof_type == "saltak":
        elements.append(StructuralElement(
            id="tak_venstre",
            name="Takflate venstre",
            element_type="roof_surface",
            x=0.0, y=0.0, z=eaves_h,
            length=L, width=W / 2.0, height=ridge_h - eaves_h,
            material="tre",
            carries_roof=False,
        ))
        elements.append(StructuralElement(
            id="tak_hoyre",
            name="Takflate høyre",
            element_type="roof_surface",
            x=0.0, y=W / 2.0, z=ridge_h,
            length=L, width=W / 2.0, height=-(ridge_h - eaves_h),
            material="tre",
            carries_roof=False,
        ))
        # Mønelinje
        elements.append(StructuralElement(
            id="mone",
            name="Mønelinje",
            element_type="ridge_beam",
            x=0.0, y=W / 2.0 - RIDGE_BEAM_SIZE / 2.0, z=ridge_h - RIDGE_BEAM_SIZE,
            length=L, width=RIDGE_BEAM_SIZE, height=RIDGE_BEAM_SIZE,
            material=material,
            is_bearing=True,
            carries_roof=True,
        ))
    elif roof_type == "pulttak":
        elements.append(StructuralElement(
            id="tak_pulttak",
            name="Takflate pulttak",
            element_type="roof_surface",
            x=0.0, y=0.0, z=eaves_h,
            length=L, width=W, height=ridge_h - eaves_h,
            material="tre",
        ))
    else:  # flatt tak
        elements.append(StructuralElement(
            id="tak_flatt",
            name="Takflate (flatt)",
            element_type="roof_surface",
            x=0.0, y=0.0, z=ridge_h,
            length=L, width=W, height=0.0,
            material="tre",
        ))

    # ── Lastpiler ─────────────────────────────────────────────────────────────
    arrow_z = ridge_h + LOAD_ARROW_HEIGHT_OFFSET
    n = LOAD_ARROW_GRID
    for ix in range(n):
        for iy in range(n):
            ax = L * (ix + 1) / (n + 1)
            ay = W * (iy + 1) / (n + 1)
            elements.append(StructuralElement(
                id=f"last_pil_{ix}_{iy}",
                name="Lastpil (tak/snø)",
                element_type="load_arrow",
                x=ax, y=ay, z=arrow_z,
                length=0.0, width=0.0, height=LOAD_ARROW_HEIGHT_OFFSET + 0.5,
                load_kn=(egenlast + snolast) * (L / (n + 1)) * (W / (n + 1)),
            ))

    return BarnModel3D(
        length_m=L,
        width_m=W,
        eaves_height_m=eaves_h,
        ridge_height_m=ridge_h,
        roof_type=roof_type,
        roof_angle_deg=roof_angle,
        floors=floors,
        elements=elements,
        assumptions=assumptions,
    )
