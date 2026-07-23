from __future__ import annotations

import streamlit as st


TAKTYPE_OPTIONS = ["saltak", "pulttak", "flatt tak"]
MATERIALTYPE_OPTIONS = ["tre", "stål", "blandet", "ukjent"]
VINDSCENARIO_OPTIONS = ["lav", "normal", "høy", "storm"]
TAK_BAERES_AV_OPTIONS = ["yttervegger", "innervegg", "søyler", "kombinasjon"]
GULV_BAERES_AV_OPTIONS = ["yttervegger", "innervegg", "søyler", "ukjent"]


def render_model_3d_inputs() -> dict:
    """Viser inputskjema for 3D-låvemodell og returnerer inputverdier som dict.

    Alle standardverdier er merket som antakelser og skal ikke brukes som
    endelig prosjekteringsgrunnlag.
    """
    st.markdown("#### Bygningsmål")
    st.caption("Standardverdier under er antakelser – juster etter faktisk bygg.")

    g1, g2, g3 = st.columns(3)
    lengde_m = g1.number_input(
        "Lengde (m)", min_value=4.0, value=18.0, step=0.5, key="3d_lengde"
    )
    bredde_m = g2.number_input(
        "Bredde (m)", min_value=4.0, value=10.0, step=0.5, key="3d_bredde"
    )
    antall_etasjer = int(g3.number_input(
        "Antall etasjer", min_value=1, value=1, step=1, key="3d_etasjer"
    ))

    g4, g5, g6, g7 = st.columns(4)
    gesimshoyde_m = g4.number_input(
        "Gesimshøyde (m)", min_value=2.0, value=3.2, step=0.1, key="3d_gesims"
    )
    monehoyde_m = g5.number_input(
        "Mønehøyde (m)",
        min_value=gesimshoyde_m + 0.1,
        value=max(5.0, gesimshoyde_m + 0.1),
        step=0.1,
        key="3d_mone",
    )
    taktype = g6.selectbox("Taktype", TAKTYPE_OPTIONS, index=0, key="3d_taktype")
    takvinkel_grader = g7.number_input(
        "Takvinkel (°)", min_value=0.0, max_value=60.0, value=27.0, step=1.0,
        key="3d_takvinkel",
    )
    materialtype = st.selectbox(
        "Konstruksjonstype/materiale", MATERIALTYPE_OPTIONS, index=0, key="3d_material"
    )

    st.markdown("#### Bæresystem")
    b1, b2, b3 = st.columns(3)
    yttervegger_baerende = b1.checkbox(
        "Yttervegger bærende", value=True, key="3d_ytter_baer"
    )
    har_innervegg = b2.checkbox(
        "Innvendig bærevegg", value=False, key="3d_har_innervegg"
    )
    har_soylerekke = b3.checkbox(
        "Har søylerekke", value=False, key="3d_har_soyler"
    )

    innervegg_y = bredde_m / 2.0
    if har_innervegg:
        b4, b5 = st.columns(2)
        innervegg_y = b4.number_input(
            "Innv. bærevegg fra venstre (m)",
            min_value=0.3,
            max_value=max(bredde_m - 0.3, 0.3),
            value=bredde_m / 2.0,
            step=0.1,
            key="3d_innervegg_y",
        )

    antall_soyler = 4
    soylerekke_y = bredde_m / 2.0
    if har_soylerekke:
        c1, c2 = st.columns(2)
        antall_soyler = int(c1.number_input(
            "Antall søyler", min_value=1, value=4, step=1, key="3d_antall_soyler"
        ))
        soylerekke_y = c2.number_input(
            "Søylerekke fra venstre (m)",
            min_value=0.2,
            max_value=max(bredde_m - 0.2, 0.2),
            value=bredde_m / 2.0,
            step=0.1,
            key="3d_soyle_y",
        )

    d1, d2 = st.columns(2)
    har_langs_drager = d1.checkbox(
        "Langsgående drager", value=False, key="3d_langs_drager"
    )
    har_tverr_dragere = d2.checkbox(
        "Tverrgående dragere", value=False, key="3d_tverr_dragere"
    )

    tak_baeres_av = st.multiselect(
        "Taket bæres av",
        TAK_BAERES_AV_OPTIONS,
        default=["yttervegger"],
        key="3d_tak_baeresav",
    )
    gulv_baeres_av = st.multiselect(
        "Gulvet bæres av",
        GULV_BAERES_AV_OPTIONS,
        default=["yttervegger"],
        key="3d_gulv_baeresav",
    )

    st.markdown("#### Lastmodell")
    l1, l2, l3, l4 = st.columns(4)
    egenlast_tak = l1.number_input(
        "Egenlast tak (kN/m²)", min_value=0.1, value=0.8, step=0.1, key="3d_egenlast"
    )
    snolast = l2.number_input(
        "Snølast (kN/m²)", min_value=0.0, value=1.5, step=0.1, key="3d_snolast"
    )
    gulvlast = l3.number_input(
        "Nyttelast gulv (kN/m²)", min_value=0.0, value=2.0, step=0.1, key="3d_gulvlast"
    )
    lagerlast = l4.number_input(
        "Lagerlast (kN/m²)", min_value=0.0, value=1.0, step=0.1, key="3d_lagerlast"
    )

    l5, l6 = st.columns(2)
    vindscenario = l5.selectbox(
        "Vindscenario", VINDSCENARIO_OPTIONS, index=1, key="3d_vind"
    )
    usikkerhetsfaktor = l6.slider(
        "Usikkerhetsfaktor", min_value=1.0, max_value=2.0, value=1.2, step=0.05,
        key="3d_usikkerhet",
    )

    return {
        "lengde_m": lengde_m,
        "bredde_m": bredde_m,
        "gesimshoyde_m": gesimshoyde_m,
        "monehoyde_m": monehoyde_m,
        "taktype": taktype,
        "takvinkel_grader": takvinkel_grader,
        "antall_etasjer": antall_etasjer,
        "materialtype": materialtype,
        "yttervegger_baerende": yttervegger_baerende,
        "har_innvendig_baerevegg": har_innervegg,
        "innvendig_baerevegg_plassering_m": innervegg_y,
        "har_soylerekke": har_soylerekke,
        "antall_soyler": antall_soyler,
        "soylerekke_plassering_m": soylerekke_y,
        "har_langsgaende_drager": har_langs_drager,
        "har_tverrgaende_dragere": har_tverr_dragere,
        "tak_baeres_av": tak_baeres_av,
        "gulv_baeres_av": gulv_baeres_av,
        "egenlast_tak_kn_m2": egenlast_tak,
        "snolast_kn_m2": snolast,
        "gulvlast_kn_m2": gulvlast,
        "lagerlast_kn_m2": lagerlast,
        "vindscenario": vindscenario,
        "usikkerhetsfaktor": usikkerhetsfaktor,
    }
