from __future__ import annotations

import plotly.graph_objects as go


def create_load_path_3d_figure(load_analysis: dict) -> go.Figure:
    """Viser et enkelt søylediagram med lastfordeling før og etter.

    Dette er en forenklet indikasjon på endring i lastfordeling.
    """
    before = load_analysis.get("before_distribution", {})
    after = load_analysis.get("after_distribution", {})

    all_ids = sorted(set(before) | set(after))
    if not all_ids:
        fig = go.Figure()
        fig.update_layout(title="Ingen lastdata å vise")
        return fig

    fig = go.Figure()
    fig.add_trace(go.Bar(
        name="Før endring",
        x=all_ids,
        y=[before.get(eid, 0.0) for eid in all_ids],
        marker_color="#4488cc",
    ))
    fig.add_trace(go.Bar(
        name="Etter endring",
        x=all_ids,
        y=[after.get(eid, 0.0) for eid in all_ids],
        marker_color="#cc4444",
    ))
    fig.update_layout(
        title="Forenklet lastfordeling per element (kN) – indikasjon",
        barmode="group",
        xaxis_title="Element-ID",
        yaxis_title="Last (kN)",
        legend=dict(orientation="h"),
        height=350,
    )
    return fig
