from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


# Andel av bygningslengden brukt som enkel representasjon av stolpesegment i plan.
# 0.08 gir korte segmenter som viser stolpelinje-posisjon visuelt uten å dominere planfiguren i MVP.
COLUMN_SEGMENT_FRACTION = 0.08


@dataclass
class BuildingModel:
    lengde_m: float
    bredde_m: float
    monehoyde_m: float
    gesimshoyde_m: float
    antall_etasjer: int
    taktype: str
    takvinkel_grader: float
    konstruksjonstype: str
    grunnplan: str = "rektangulært"


@dataclass
class SupportLine:
    id: str
    navn: str
    type: str
    x_start_m: float
    y_start_m: float
    x_end_m: float
    y_end_m: float
    etasje: int
    baerer_tak: bool
    baerer_bjelkelag: bool
    antatt_baereevne_kn: float | None = None
    status: str = "eksisterende"


@dataclass
class PointSupport:
    id: str
    navn: str
    x_m: float
    y_m: float
    etasje: int
    dimensjon: str
    materiale: str
    status: str = "eksisterende"


@dataclass
class LoadArea:
    id: str
    navn: str
    area_m2: float
    load_type: str
    load_kn_per_m2: float
    supported_by: list[str]


@dataclass
class RemovalScenario:
    scenario_name: str
    remove_support_ids: list[str]
    proposed_replacement: str
    replacement_beam_span_m: float
    temporary_support_needed: bool
    notes: str = ""


def _support_line_length(line: SupportLine) -> float:
    dx = line.x_end_m - line.x_start_m
    dy = line.y_end_m - line.y_start_m
    return (dx**2 + dy**2) ** 0.5


def _make_outer_walls(building: BuildingModel, antall_etasjer: int, baerende_yttervegger: bool) -> list[SupportLine]:
    return [
        SupportLine(
            id="ytter_nord",
            navn="Yttervegg nord",
            type="yttervegg",
            x_start_m=0.0,
            y_start_m=0.0,
            x_end_m=building.lengde_m,
            y_end_m=0.0,
            etasje=antall_etasjer,
            baerer_tak=baerende_yttervegger,
            baerer_bjelkelag=baerende_yttervegger,
        ),
        SupportLine(
            id="ytter_sor",
            navn="Yttervegg sør",
            type="yttervegg",
            x_start_m=0.0,
            y_start_m=building.bredde_m,
            x_end_m=building.lengde_m,
            y_end_m=building.bredde_m,
            etasje=antall_etasjer,
            baerer_tak=baerende_yttervegger,
            baerer_bjelkelag=baerende_yttervegger,
        ),
        SupportLine(
            id="ytter_vest",
            navn="Yttervegg vest",
            type="yttervegg",
            x_start_m=0.0,
            y_start_m=0.0,
            x_end_m=0.0,
            y_end_m=building.bredde_m,
            etasje=antall_etasjer,
            baerer_tak=baerende_yttervegger,
            baerer_bjelkelag=baerende_yttervegger,
        ),
        SupportLine(
            id="ytter_ost",
            navn="Yttervegg øst",
            type="yttervegg",
            x_start_m=building.lengde_m,
            y_start_m=0.0,
            x_end_m=building.lengde_m,
            y_end_m=building.bredde_m,
            etasje=antall_etasjer,
            baerer_tak=baerende_yttervegger,
            baerer_bjelkelag=baerende_yttervegger,
        ),
    ]


def _normalize_supports(raw_supports: list[dict[str, Any]], building: BuildingModel, etasje: int) -> list[SupportLine]:
    normalized: list[SupportLine] = []
    for index, support in enumerate(raw_supports, start=1):
        normalized.append(
            SupportLine(
                id=support.get("id") or f"manuell_{index}",
                navn=support.get("navn") or f"Manuell bærelinje {index}",
                type=support.get("type", "ukjent"),
                x_start_m=max(0.0, min(float(support.get("x_start_m", 0.0)), building.lengde_m)),
                y_start_m=max(0.0, min(float(support.get("y_start_m", 0.0)), building.bredde_m)),
                x_end_m=max(0.0, min(float(support.get("x_end_m", building.lengde_m)), building.lengde_m)),
                y_end_m=max(0.0, min(float(support.get("y_end_m", building.bredde_m)), building.bredde_m)),
                etasje=etasje,
                baerer_tak=bool(support.get("baerer_tak", True)),
                baerer_bjelkelag=bool(support.get("baerer_bjelkelag", False)),
                antatt_baereevne_kn=support.get("antatt_baereevne_kn"),
                status=support.get("status", "eksisterende"),
            )
        )
    return normalized


def build_structural_model(
    building_input: dict[str, Any],
    system_input: dict[str, Any],
    load_input: dict[str, Any],
) -> dict[str, Any]:
    """Bygger en forenklet bygningsmodell med bærelinjer, punktstøtter og lastflater for låveanalyse.

    Returnerer en serialiserbar dict med nøkler: building, support_lines, point_supports, load_areas og assumptions.
    """
    building = BuildingModel(
        lengde_m=float(building_input["lengde_m"]),
        bredde_m=float(building_input["bredde_m"]),
        monehoyde_m=float(building_input["monehoyde_m"]),
        gesimshoyde_m=float(building_input["gesimshoyde_m"]),
        antall_etasjer=int(building_input["antall_etasjer"]),
        taktype=building_input["taktype"],
        takvinkel_grader=float(building_input["takvinkel_grader"]),
        konstruksjonstype=building_input["konstruksjonstype"],
        grunnplan=building_input.get("grunnplan", "rektangulært"),
    )

    supports = _make_outer_walls(
        building,
        antall_etasjer=building.antall_etasjer,
        baerende_yttervegger=bool(system_input.get("yttervegger_baerende", True)),
    )

    if system_input.get("har_innvendig_baerevegg"):
        innervegg_y_pos = max(0.0, min(float(system_input.get("innervegg_posisjon_m", building.bredde_m / 2.0)), building.bredde_m))
        supports.append(
            SupportLine(
                id="innervegg_1",
                navn="Innvendig bærevegg",
                type="innervegg",
                x_start_m=0.0,
                y_start_m=innervegg_y_pos,
                x_end_m=building.lengde_m,
                y_end_m=innervegg_y_pos,
                etasje=building.antall_etasjer,
                baerer_tak=True,
                baerer_bjelkelag=True,
            )
        )

    if system_input.get("har_stolperekker"):
        antall_stolper = max(1, int(system_input.get("antall_stolper", 2)))
        row_y = max(0.1, min(float(system_input.get("stolperekke_posisjon_m", building.bredde_m / 2.0)), building.bredde_m - 0.1))
        for idx in range(antall_stolper):
            fraction = (idx + 1) / (antall_stolper + 1)
            supports.append(
                SupportLine(
                    id=f"stolperekke_lin_{idx+1}",
                    navn=f"Stolperekke segment {idx+1}",
                    type="søylerekke",
                    x_start_m=building.lengde_m * max(0.0, fraction - COLUMN_SEGMENT_FRACTION),
                    y_start_m=row_y,
                    x_end_m=building.lengde_m * min(1.0, fraction + COLUMN_SEGMENT_FRACTION),
                    y_end_m=row_y,
                    etasje=1,
                    baerer_tak=True,
                    baerer_bjelkelag=building.antall_etasjer > 1,
                )
            )

    supports.extend(_normalize_supports(system_input.get("manuelle_baerelinjer", []), building, building.antall_etasjer))

    point_supports: list[PointSupport] = []
    if system_input.get("har_stolper"):
        antall_punkt = max(1, int(system_input.get("antall_stolper", 2)))
        punkt_y = max(0.1, min(float(system_input.get("stolperekke_posisjon_m", building.bredde_m / 2.0)), building.bredde_m - 0.1))
        for idx in range(antall_punkt):
            fraction = (idx + 1) / (antall_punkt + 1)
            point_supports.append(
                PointSupport(
                    id=f"stolpe_{idx+1}",
                    navn=f"Stolpe {idx+1}",
                    x_m=building.lengde_m * fraction,
                    y_m=punkt_y,
                    etasje=1,
                    dimensjon=system_input.get("stolpe_dimensjon", "98x98"),
                    materiale=system_input.get("stolpe_materiale", "tre"),
                )
            )

    all_support_ids = [support.id for support in supports] + [point.id for point in point_supports]
    roof_supports = system_input.get("tak_baeres_av") or ["yttervegger"]
    chosen_supports = []
    if "yttervegger" in roof_supports:
        chosen_supports.extend([support.id for support in supports if support.type == "yttervegg"])
    if "innervegg" in roof_supports:
        chosen_supports.extend([support.id for support in supports if support.type == "innervegg"])
    if "stolper" in roof_supports:
        chosen_supports.extend([point.id for point in point_supports])
    if not chosen_supports:
        chosen_supports = all_support_ids

    floor_supports = [support.id for support in supports if support.baerer_bjelkelag]
    if not floor_supports:
        floor_supports = [support.id for support in supports]

    area = building.lengde_m * building.bredde_m
    load_areas = [
        LoadArea(
            id="tak_egenlast",
            navn="Tak egenlast",
            area_m2=area,
            load_type="tak",
            load_kn_per_m2=float(load_input["egenlast_tak_kn_m2"]),
            supported_by=chosen_supports,
        ),
        LoadArea(
            id="snolast",
            navn="Snølast",
            area_m2=area,
            load_type="snø",
            load_kn_per_m2=float(load_input["snolast_kn_m2"]),
            supported_by=chosen_supports,
        ),
        LoadArea(
            id="gulvlast",
            navn="Nyttelast gulv",
            area_m2=area,
            load_type="gulv",
            load_kn_per_m2=float(load_input["nyttelast_gulv_kn_m2"]),
            supported_by=floor_supports,
        ),
        LoadArea(
            id="lagerlast",
            navn="Lagerlast",
            area_m2=area,
            load_type="lager",
            load_kn_per_m2=float(load_input["lagerlast_kn_m2"]),
            supported_by=floor_supports,
        ),
    ]

    return {
        "building": asdict(building),
        "support_lines": [asdict(line) | {"length_m": _support_line_length(line)} for line in supports],
        "point_supports": [asdict(point) for point in point_supports],
        "load_areas": [asdict(load_area) for load_area in load_areas],
        "assumptions": {
            "vindscenario": load_input.get("vindscenario", "normal"),
            "usikkerhetsfaktor": float(load_input.get("usikkerhetsfaktor", 1.2)),
            "forenklet_estimat": True,
        },
    }


# ─── 3D endringsanalyse ───────────────────────────────────────────────────────

from src.engine.structural_elements import BarnModel3D  # noqa: E402
from src.engine.load_paths import analyze_load_paths_before_after  # noqa: E402
from src.engine.global_stability import assess_3d_lateral_stability  # noqa: E402


def generate_3d_recommendations(
    analysis: dict,
    lateral_stability: dict,
    scenario: dict,
) -> list[str]:
    """Genererer anbefalte tiltak basert på analyse og scenario."""
    recs: list[str] = []
    action = scenario.get("action", "behold")
    risk = analysis.get("risk_level", "green")

    if risk == "red":
        recs.append("⛔ Stopp og innhent vurdering fra byggingeniør før tiltak.")
    if action == "fjern":
        recs.append("Ikke fjern bærende konstruksjon uten prosjektert erstatningsløsning.")
        recs.append("Bruk midlertidig understøtting før demontering av bærende element.")
        recs.append("Kontroller om veggen/stolpen bærer tak, bjelkelag eller drager.")
    if action == "erstatt med drager":
        recs.append("Dimensjoner erstatningsdrager med fagperson.")
        recs.append("Kontroller fundament under nye søyler.")
    if analysis.get("unresolved_load_paths"):
        recs.append("Avklar komplett lastvei fra tak/gulv ned til fundament.")
    if analysis.get("max_increase_percent", 0) > 15:
        recs.append("Kontroller punktlaster og understøtting ved lastøkning på gjenværende elementer.")
    recs.append("Kontroller horisontal avstivning.")
    recs.append("Undersøk om fjernet element fungerer som avstivende skive.")
    recs.append("Dokumenter eksisterende konstruksjon med bilder før tiltak.")
    recs.extend(lateral_stability.get("recommendations", []))
    return list(dict.fromkeys(recs))  # deduplicate preserving order


def analyze_3d_change_before_after(
    model_before: BarnModel3D,
    model_after: BarnModel3D,
    scenario: dict,
    inputs: dict,
) -> dict:
    """Analyserer konsekvens av 3D-endringsscenario.

    Returnerer forenklet risikovurdering, lastanalyse, horisontal stabilitet
    og anbefalinger. Alle resultater er forenklede estimater og skal ikke
    brukes som endelig prosjekteringsgrunnlag.
    """
    load_analysis = analyze_load_paths_before_after(model_before, model_after, inputs)
    lateral = assess_3d_lateral_stability(model_before, model_after, scenario, inputs)

    selected_id = scenario.get("selected_element_id")
    action = scenario.get("action", "behold")

    selected_elem = next((e for e in model_before.elements if e.id == selected_id), None)
    unresolved = load_analysis.get("unresolved_load_paths", [])
    max_increase = load_analysis.get("max_increase_percent", 0.0)

    critical_elements: list[str] = []
    level = "green"

    # Rød risiko-kriterier
    if action == "fjern" and selected_elem and selected_elem.is_bearing:
        repl = (scenario.get("action") == "erstatt med drager")
        if not repl:
            level = "red"
            critical_elements.append(f"Bærende element «{selected_elem.name}» fjernes uten erstatning.")

    if unresolved:
        level = "red"
        for finding in unresolved:
            critical_elements.append(finding)

    if max_increase > 50.0:
        level = "red"
        critical_elements.append(f"Lastøkning på gjenværende element er {max_increase:.0f} % (over 50 %).")

    if lateral.get("risk_level") == "red" and level != "red":
        level = "red"

    # Gul risiko-kriterier
    if level != "red":
        if action == "erstatt med drager":
            level = "yellow"
            critical_elements.append("Erstatningsdrager er ikke dimensjonert i detalj.")
        elif max_increase > 15.0:
            level = "yellow"
            critical_elements.append(f"Lastøkning på gjenværende element er {max_increase:.0f} % (15–50 %).")
        elif lateral.get("risk_level") == "yellow":
            level = "yellow"
        elif selected_elem and selected_elem.is_bearing and action == "fjern":
            level = "yellow"
        elif inputs.get("materialtype", "tre") == "ukjent":
            level = "yellow"
            critical_elements.append("Materialtype er ukjent – høyere usikkerhet.")

    if not critical_elements and action == "behold":
        critical_elements.append("Ingen endring valgt – elementet er uendret.")
    elif not critical_elements and level == "green":
        critical_elements.append("Endringen ser begrenset ut i denne forenklede vurderingen.")

    summary_map = {
        "green": "Forenklet analyse indikerer lav konsekvens. Tiltak bør likevel kontrolleres.",
        "yellow": "Forenklet analyse indikerer mulig risiko. Løsning bør kontrolleres faglig.",
        "red": "Forenklet analyse indikerer høy risiko. Tiltak krever faglig vurdering.",
    }

    requires_temp = bool(
        action in {"fjern", "erstatt med drager"}
        and selected_elem
        and selected_elem.is_bearing
        and level in {"yellow", "red"}
    )

    recommendations = generate_3d_recommendations(
        {"risk_level": level, **load_analysis},
        lateral,
        scenario,
    )

    return {
        "risk_level": level,
        "summary": summary_map[level],
        "before_loads": load_analysis.get("before_distribution", {}),
        "after_loads": load_analysis.get("after_distribution", {}),
        "load_increase_percent": {
            eid: v["increase_percent"]
            for eid, v in load_analysis.get("load_increases", {}).items()
        },
        "load_increase_detail": load_analysis.get("load_increases", {}),
        "total_loads_before": load_analysis.get("total_loads_before", {}),
        "total_loads_after": load_analysis.get("total_loads_after", {}),
        "unresolved_load_paths": unresolved,
        "critical_elements": critical_elements,
        "recommendations": recommendations,
        "requires_engineer": level in {"yellow", "red"},
        "requires_temporary_support": requires_temp,
        "lateral_stability": lateral,
        "max_increase_percent": max_increase,
    }
