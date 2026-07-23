from __future__ import annotations

from typing import Any

from src.engine.structural_elements import BarnModel3D, StructuralElement


def get_element_by_id(model: BarnModel3D, element_id: str) -> StructuralElement | None:
    """Returnerer element med gitt ID, eller None."""
    for elem in model.elements:
        if elem.id == element_id:
            return elem
    for elem in model.new_elements:
        if elem.id == element_id:
            return elem
    return None


def get_bearing_elements(model: BarnModel3D) -> list[StructuralElement]:
    """Returnerer alle bærende elementer som ikke er fjernet."""
    return [
        elem for elem in model.elements
        if elem.is_bearing and elem.status != "removed"
    ]


def get_active_roof_supports(model: BarnModel3D) -> list[StructuralElement]:
    """Returnerer aktive elementer som bærer tak."""
    return [
        elem for elem in model.elements
        if elem.carries_roof and elem.status != "removed"
    ]


def get_active_floor_supports(model: BarnModel3D) -> list[StructuralElement]:
    """Returnerer aktive elementer som bærer gulv/bjelkelag."""
    return [
        elem for elem in model.elements
        if elem.carries_floor and elem.status != "removed"
    ]


def get_lateral_stability_elements(model: BarnModel3D) -> list[StructuralElement]:
    """Returnerer elementer som bidrar til horisontal avstivning."""
    return [
        elem for elem in model.elements
        if elem.provides_lateral_stability and elem.status != "removed"
    ]


def build_element_label(elem: StructuralElement) -> str:
    """Lager leservennlig etikett for selectbox."""
    bearing_label = "bærende" if elem.is_bearing else "ikke bærende"
    return f"[{elem.id}] {elem.name} – {elem.element_type} – {bearing_label} – {elem.status}"


def list_selectable_elements(model: BarnModel3D) -> list[dict[str, Any]]:
    """Returnerer liste av elementer som kan velges av bruker (unntatt lastpiler)."""
    skip_types = {"load_arrow", "foundation", "floor_surface"}
    return [
        {
            "id": elem.id,
            "label": build_element_label(elem),
            "element": elem,
        }
        for elem in model.elements
        if elem.element_type not in skip_types
    ]
