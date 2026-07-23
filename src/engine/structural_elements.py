from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


VALID_ELEMENT_TYPES = {
    "foundation",
    "floor_surface",
    "outer_wall",
    "inner_bearing_wall",
    "non_bearing_wall",
    "column",
    "column_row",
    "beam",
    "roof_beam",
    "floor_beam",
    "roof_surface",
    "ridge_beam",
    "load_arrow",
}

VALID_STATUSES = {
    "existing",
    "selected",
    "removed",
    "new",
    "reinforced",
    "warning",
    "critical",
}


@dataclass
class StructuralElement:
    id: str
    name: str
    element_type: str
    x: float
    y: float
    z: float
    length: float
    width: float
    height: float
    rotation_z: float = 0.0
    material: str = "tre"
    is_bearing: bool = False
    carries_roof: bool = False
    carries_floor: bool = False
    provides_lateral_stability: bool = False
    status: str = "existing"
    load_kn: float = 0.0
    connected_to: List[str] = field(default_factory=list)


@dataclass
class BarnModel3D:
    length_m: float
    width_m: float
    eaves_height_m: float
    ridge_height_m: float
    roof_type: str
    roof_angle_deg: float
    floors: int
    elements: List[StructuralElement] = field(default_factory=list)
    removed_elements: List[str] = field(default_factory=list)
    new_elements: List[StructuralElement] = field(default_factory=list)
    assumptions: List[str] = field(default_factory=list)
