from __future__ import annotations

from typing import Dict

import streamlit as st


def render_sidebar_inputs(default_prices: Dict[str, float]) -> dict:
    st.sidebar.header("Innstillinger")
    st.sidebar.caption("Prisene kan redigeres og brukes direkte i materiallisten.")
    prices: Dict[str, float] = {}
    for dimension, price in default_prices.items():
        prices[dimension] = st.sidebar.number_input(
            f"Pris per meter for {dimension} (kr)",
            min_value=0.0,
            value=float(price),
            step=1.0,
        )
    waste_factor = st.sidebar.slider("Antatt svinn (%)", min_value=0, max_value=30, value=10)
    return {"prices": prices, "waste_factor": waste_factor}
