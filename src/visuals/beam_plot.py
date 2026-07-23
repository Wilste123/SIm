from __future__ import annotations

import plotly.graph_objects as go

from src.visuals.color_theme import COLORS


def create_beam_figure(span_m: float, utilization_ratio: float) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=[0, span_m], y=[0, 0], mode="lines", line={"color": COLORS["secondary"], "width": 8}))
    color = COLORS["success"] if utilization_ratio <= 0.7 else COLORS["warning"] if utilization_ratio <= 1.0 else COLORS["danger"]
    fig.add_trace(go.Scatter(x=[span_m / 2], y=[0.1], mode="markers", marker={"size": 16, "color": color}))
    fig.update_layout(
        title="Forenklet bjelkevisning",
        xaxis_title="Spenn (m)",
        yaxis_visible=False,
        plot_bgcolor=COLORS["background"],
        paper_bgcolor=COLORS["background"],
        showlegend=False,
        margin={"l": 20, "r": 20, "t": 50, "b": 20},
    )
    return fig
