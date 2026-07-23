from __future__ import annotations

import plotly.graph_objects as go

from src.engine.structural_elements import BarnModel3D, StructuralElement

# ─── Farger per elementtype ───────────────────────────────────────────────────
_TYPE_COLORS: dict[str, str] = {
    "foundation":          "#b0a090",
    "floor_surface":       "#d8c8a8",
    "outer_wall":          "#8ab4cc",
    "inner_bearing_wall":  "#4a8a30",
    "non_bearing_wall":    "#cccccc",
    "column":              "#8b6010",
    "column_row":          "#8b6010",
    "beam":                "#c8900a",
    "roof_beam":           "#c0965a",
    "floor_beam":          "#c0965a",
    "roof_surface":        "#c8b888",
    "ridge_beam":          "#6a3a20",
    "load_arrow":          "orange",
}

_STATUS_COLORS: dict[str, str] = {
    "selected":   "#FFD700",
    "removed":    "#FF4444",
    "new":        "#3388FF",
    "reinforced": "#44BB44",
    "warning":    "#FFB340",
    "critical":   "#FF2020",
}

_TYPE_OPACITIES: dict[str, float] = {
    "outer_wall":    0.30,
    "roof_surface":  0.35,
    "foundation":    0.70,
    "floor_surface": 0.50,
}
_DEFAULT_OPACITY = 0.85
_REMOVED_OPACITY = 0.25

# ─── Box-triangulation indekser (konstant) ────────────────────────────────────
_BOX_I = [0, 0, 7, 7, 0, 0, 2, 2, 0, 0, 1, 1]
_BOX_J = [1, 2, 5, 6, 4, 5, 6, 7, 3, 7, 5, 6]
_BOX_K = [2, 3, 4, 5, 5, 1, 7, 3, 7, 4, 6, 2]


def get_element_color(elem: StructuralElement, selected_element_id: str | None = None) -> str:
    """Returnerer farge for et element basert på status og type."""
    if elem.id == selected_element_id:
        return _STATUS_COLORS["selected"]
    if elem.status in _STATUS_COLORS:
        return _STATUS_COLORS[elem.status]
    return _TYPE_COLORS.get(elem.element_type, "#aaaaaa")


def _get_opacity(elem: StructuralElement) -> float:
    if elem.status == "removed":
        return _REMOVED_OPACITY
    return _TYPE_OPACITIES.get(elem.element_type, _DEFAULT_OPACITY)


def add_box_3d(
    fig: go.Figure,
    elem: StructuralElement,
    color: str,
    opacity: float = 0.85,
) -> None:
    """Legger til en 3D-boks i figuren for et StructuralElement."""
    x0, y0, z0 = elem.x, elem.y, elem.z
    dx, dy, dz = max(elem.length, 0.01), max(elem.width, 0.01), max(elem.height, 0.01)

    x_v = [x0,    x0+dx, x0+dx, x0,    x0,    x0+dx, x0+dx, x0]
    y_v = [y0,    y0,    y0+dy, y0+dy, y0,    y0,    y0+dy, y0+dy]
    z_v = [z0,    z0,    z0,    z0,    z0+dz, z0+dz, z0+dz, z0+dz]

    fig.add_trace(go.Mesh3d(
        x=x_v, y=y_v, z=z_v,
        i=_BOX_I, j=_BOX_J, k=_BOX_K,
        color=color,
        opacity=opacity,
        name=elem.name,
        showlegend=False,
        hovertext=f"{elem.name}<br>Type: {elem.element_type}<br>Status: {elem.status}",
        hoverinfo="text",
    ))


def _add_roof_surface(
    fig: go.Figure,
    elem: StructuralElement,
    color: str,
    opacity: float,
) -> None:
    """Tegner en skrå takflate som Mesh3d med 4 hjørner."""
    x0, y0, z0 = elem.x, elem.y, elem.z
    dx, dy, dz = elem.length, elem.width, elem.height

    # Hjørner: (x0,y0,z0), (x0+dx,y0,z0), (x0+dx,y0+dy,z0+dz), (x0,y0+dy,z0+dz)
    xv = [x0,    x0+dx, x0+dx, x0]
    yv = [y0,    y0,    y0+dy, y0+dy]
    zv = [z0,    z0,    z0+dz, z0+dz]

    fig.add_trace(go.Mesh3d(
        x=xv, y=yv, z=zv,
        i=[0, 0],
        j=[1, 2],
        k=[2, 3],
        color=color,
        opacity=opacity,
        name=elem.name,
        showlegend=False,
        hovertext=f"{elem.name}<br>Type: takflate<br>Status: {elem.status}",
        hoverinfo="text",
    ))


def add_line_3d(
    fig: go.Figure,
    x1: float, y1: float, z1: float,
    x2: float, y2: float, z2: float,
    color: str,
    width: int = 5,
    name: str = "",
) -> None:
    """Legger til en 3D-linje."""
    fig.add_trace(go.Scatter3d(
        x=[x1, x2], y=[y1, y2], z=[z1, z2],
        mode="lines",
        line=dict(color=color, width=width),
        name=name,
        showlegend=bool(name),
        hoverinfo="skip",
    ))


def add_arrow_3d(
    fig: go.Figure,
    x1: float, y1: float, z1: float,
    x2: float, y2: float, z2: float,
    color: str = "orange",
) -> None:
    """Tegner en pil som linje + cone."""
    add_line_3d(fig, x1, y1, z1, x2, y2, z2, color=color, width=3)


def add_label_3d(fig: go.Figure, x: float, y: float, z: float, text: str) -> None:
    """Legger til en tekstetikett i 3D-rommet."""
    fig.add_trace(go.Scatter3d(
        x=[x], y=[y], z=[z],
        mode="text",
        text=[text],
        textfont=dict(size=10, color="black"),
        showlegend=False,
        hoverinfo="skip",
    ))


def _add_load_arrows(fig: go.Figure, elements: list[StructuralElement]) -> None:
    """Tegner lastpiler samlet som Cone-trace."""
    if not elements:
        return
    xs = [e.x for e in elements]
    ys = [e.y for e in elements]
    zs = [e.z for e in elements]
    n = len(elements)
    fig.add_trace(go.Cone(
        x=xs, y=ys, z=zs,
        u=[0] * n, v=[0] * n, w=[-1.0] * n,
        colorscale=[[0, "orange"], [1, "darkorange"]],
        showscale=False,
        sizemode="absolute",
        sizeref=0.45,
        name="Lastpiler (tak/snø)",
        showlegend=True,
        hoverinfo="skip",
    ))


def plot_barn_3d(
    model: BarnModel3D,
    selected_element_id: str | None = None,
    title: str = "3D Låvemodell (forenklet visualisering)",
) -> go.Figure:
    """Genererer en interaktiv Plotly 3D-figur av BarnModel3D.

    Valgt element markeres gult. Fjernede elementer vises røde og transparente.
    Alle dimensjoner er i meter. Dette er en forenklet pedagogisk visualisering.
    """
    fig = go.Figure()

    load_arrows: list[StructuralElement] = []

    for elem in model.elements:
        if elem.element_type == "load_arrow":
            load_arrows.append(elem)
            continue

        color = get_element_color(elem, selected_element_id)
        opacity = _get_opacity(elem)

        if elem.element_type == "roof_surface":
            _add_roof_surface(fig, elem, color, opacity)
        else:
            add_box_3d(fig, elem, color, opacity)

    _add_load_arrows(fig, load_arrows)

    fig.update_layout(
        title=dict(text=title, font=dict(size=14)),
        scene=dict(
            xaxis_title="Lengde (m)",
            yaxis_title="Bredde (m)",
            zaxis_title="Høyde (m)",
            aspectmode="data",
            bgcolor="rgba(240,245,255,1)",
        ),
        showlegend=False,
        margin=dict(l=0, r=0, t=40, b=0),
        height=520,
    )
    return fig
