from __future__ import annotations

import plotly.graph_objects as go

from src.visuals.color_theme import COLORS


def create_wall_figure(wall_data: dict, wall_result: dict) -> go.Figure:
    fig = go.Figure()
    wall_width_m = wall_data["wall_width_m"]
    wall_height_m = wall_data["wall_height_m"]
    stud_width_m = wall_result["stud_width_m"]

    fig.add_shape(
        type="rect",
        x0=0,
        y0=0,
        x1=wall_width_m,
        y1=wall_height_m,
        line={"color": COLORS["secondary"], "width": 3},
        fillcolor=COLORS["background"],
    )

    for x in wall_result["regular_studs"]:
        fig.add_shape(
            type="rect",
            x0=x,
            y0=0,
            x1=x + stud_width_m,
            y1=wall_height_m,
            line={"color": COLORS["primary"], "width": 1},
            fillcolor=COLORS["primary"],
            opacity=0.7,
        )

    for x in wall_result["extra_studs"]:
        fig.add_shape(
            type="rect",
            x0=x,
            y0=0,
            x1=x + stud_width_m,
            y1=wall_height_m,
            line={"color": COLORS["accent"], "width": 1},
            fillcolor=COLORS["accent"],
            opacity=0.7,
        )

    for opening in wall_result["openings"]:
        fig.add_shape(
            type="rect",
            x0=opening.left_m,
            y0=opening.bottom_m,
            x1=opening.right_m,
            y1=min(opening.top_m, wall_height_m),
            line={"color": COLORS["opening"], "width": 2},
            fillcolor=COLORS["opening"],
            opacity=0.45,
        )

    for header in wall_result["headers"]:
        fig.add_shape(
            type="rect",
            x0=header["x0"],
            y0=header["y0"],
            x1=header["x1"],
            y1=header["y1"],
            line={"color": COLORS["danger"], "width": 1},
            fillcolor=COLORS["danger"],
            opacity=0.6,
        )

    fig.update_layout(
        title="Forenklet veggtegning",
        xaxis_title="Bredde (m)",
        yaxis_title="Høyde (m)",
        plot_bgcolor=COLORS["background"],
        paper_bgcolor=COLORS["background"],
        showlegend=False,
        margin={"l": 20, "r": 20, "t": 50, "b": 20},
    )
    fig.update_xaxes(range=[-0.05, wall_width_m + 0.05], constrain="domain")
    fig.update_yaxes(range=[0, wall_height_m + 0.05], scaleanchor="x", scaleratio=1)
    return fig
