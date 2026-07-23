from __future__ import annotations

import plotly.graph_objects as go

from src.visuals.color_theme import COLORS



def create_system_risk_figure(risk: dict, lateral: dict) -> go.Figure:
    risk_map = {"green": 1, "yellow": 2, "red": 3}
    overall = risk.get("risk_level", "yellow")
    lateral_level = lateral.get("risk_level", "yellow")

    overall_value = risk_map.get(overall, 2)
    lateral_value = risk_map.get(lateral_level, 2)

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=["Total konsekvens", "Horisontal stabilitet"],
            y=[overall_value, lateral_value],
            marker_color=[
                COLORS["success"] if overall == "green" else COLORS["warning"] if overall == "yellow" else COLORS["danger"],
                COLORS["success"] if lateral_level == "green" else COLORS["warning"] if lateral_level == "yellow" else COLORS["danger"],
            ],
            text=[overall.upper(), lateral_level.upper()],
            textposition="outside",
        )
    )
    fig.update_layout(
        title="Forenklet risikonivå",
        yaxis=dict(
            tickmode="array",
            tickvals=[1, 2, 3],
            ticktext=["Grønn", "Gul", "Rød"],
            range=[0.5, 3.5],
        ),
        plot_bgcolor=COLORS["background"],
        paper_bgcolor=COLORS["background"],
        showlegend=False,
        margin={"l": 20, "r": 20, "t": 50, "b": 20},
    )
    return fig
