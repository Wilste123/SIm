from __future__ import annotations

from typing import Any

import plotly.graph_objects as go
from plotly.subplots import make_subplots

from src.visuals.color_theme import COLORS


def _draw_model(fig: go.Figure, model: dict[str, Any], col: int, title: str, removed_ids: set[str]) -> None:
    fig.add_annotation(text=title, xref=f"x{col}", yref=f"y{col}", x=0.5, y=1.06, showarrow=False)

    building = model.get("building", {})
    width = float(building.get("bredde_m", 0.0))
    length = float(building.get("lengde_m", 0.0))

    fig.add_shape(
        type="rect",
        x0=0.0,
        y0=0.0,
        x1=length,
        y1=width,
        line={"color": COLORS["secondary"], "width": 2},
        fillcolor="rgba(0,0,0,0)",
        row=1,
        col=col,
    )

    for line in model.get("support_lines", []):
        support_id = line.get("id")
        status = line.get("status", "eksisterende")
        color = COLORS["primary"]
        dash = "solid"

        if support_id in removed_ids or status == "fjernes":
            color = COLORS["danger"]
            dash = "dash"
        elif status in {"ny", "forsterkes"} or line.get("type") == "drager":
            color = "#2563EB"

        fig.add_trace(
            go.Scatter(
                x=[line.get("x_start_m", 0.0), line.get("x_end_m", 0.0)],
                y=[line.get("y_start_m", 0.0), line.get("y_end_m", 0.0)],
                mode="lines",
                line={"color": color, "width": 3, "dash": dash},
                name=line.get("navn", support_id),
                showlegend=False,
            ),
            row=1,
            col=col,
        )

    for point in model.get("point_supports", []):
        support_id = point.get("id")
        status = point.get("status", "eksisterende")
        color = COLORS["accent"]
        symbol = "circle"
        if support_id in removed_ids or status == "fjernes":
            color = COLORS["danger"]
            symbol = "x"

        fig.add_trace(
            go.Scatter(
                x=[point.get("x_m", 0.0)],
                y=[point.get("y_m", 0.0)],
                mode="markers+text",
                marker={"size": 10, "color": color, "symbol": symbol},
                text=[point.get("navn", support_id)],
                textposition="top center",
                name=point.get("navn", support_id),
                showlegend=False,
            ),
            row=1,
            col=col,
        )


def create_barn_plan_figure(before_model: dict[str, Any], after_model: dict[str, Any], scenario: dict[str, Any], risk_level: str) -> go.Figure:
    fig = make_subplots(rows=1, cols=2, subplot_titles=("Før", "Etter"))
    removed_ids = set(scenario.get("remove_support_ids") or [])

    _draw_model(fig, before_model, col=1, title="Eksisterende bæresystem", removed_ids=removed_ids)
    _draw_model(fig, after_model, col=2, title="Etter endring", removed_ids=removed_ids)

    color = COLORS["success"] if risk_level == "green" else COLORS["warning"] if risk_level == "yellow" else COLORS["danger"]
    fig.add_annotation(
        text=f"Risiko: {risk_level.upper()}",
        xref="paper",
        yref="paper",
        x=0.5,
        y=1.14,
        showarrow=False,
        font={"color": color, "size": 14},
    )

    fig.update_xaxes(title_text="Lengde (m)", row=1, col=1)
    fig.update_xaxes(title_text="Lengde (m)", row=1, col=2)
    fig.update_yaxes(title_text="Bredde (m)", row=1, col=1, scaleanchor="x", scaleratio=1)
    fig.update_yaxes(title_text="Bredde (m)", row=1, col=2, scaleanchor="x2", scaleratio=1)
    fig.update_layout(
        plot_bgcolor=COLORS["background"],
        paper_bgcolor=COLORS["background"],
        margin={"l": 20, "r": 20, "t": 90, "b": 30},
        height=520,
    )
    return fig
