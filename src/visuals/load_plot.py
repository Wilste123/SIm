from __future__ import annotations

import plotly.graph_objects as go

from src.visuals.color_theme import COLORS


def create_load_scenario_figure(scenario_name: str, scenario: dict) -> go.Figure:
    load_factor = scenario["load_factor"]
    color = COLORS["success"] if load_factor <= 1.0 else COLORS["warning"] if load_factor < 1.5 else COLORS["danger"]
    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=[scenario_name],
            y=[load_factor],
            marker_color=color,
            text=[f"{load_factor:.2f}x"],
            textposition="outside",
        )
    )
    fig.update_layout(
        title="Forenklet lastindikator",
        yaxis_title="Lastfaktor",
        xaxis_title="Scenario",
        plot_bgcolor=COLORS["background"],
        paper_bgcolor=COLORS["background"],
        showlegend=False,
        margin={"l": 20, "r": 20, "t": 50, "b": 20},
    )
    return fig
