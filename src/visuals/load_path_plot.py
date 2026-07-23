from __future__ import annotations

import plotly.graph_objects as go

from src.visuals.color_theme import COLORS


def create_load_path_figure(before_distribution: dict, after_distribution: dict) -> go.Figure:
    before_supports = {
        **before_distribution.get("line_reactions_kn", {}),
        **before_distribution.get("point_reactions_kn", {}),
    }
    after_supports = {
        **after_distribution.get("line_reactions_kn", {}),
        **after_distribution.get("point_reactions_kn", {}),
    }
    support_ids = sorted(set(before_supports) | set(after_supports))

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=support_ids,
            y=[before_supports.get(support_id, 0.0) for support_id in support_ids],
            name="Før endring",
            marker_color=COLORS["secondary"],
        )
    )
    fig.add_trace(
        go.Bar(
            x=support_ids,
            y=[after_supports.get(support_id, 0.0) for support_id in support_ids],
            name="Etter endring",
            marker_color=COLORS["accent"],
        )
    )

    fig.update_layout(
        barmode="group",
        title="Forenklet lastfordeling på støtter (kN)",
        xaxis_title="Støtte",
        yaxis_title="Reaksjonslast (kN)",
        plot_bgcolor=COLORS["background"],
        paper_bgcolor=COLORS["background"],
        margin={"l": 20, "r": 20, "t": 50, "b": 20},
    )
    return fig
