from __future__ import annotations

import streamlit as st


TAKTYPE_OPTIONS = ["saltak", "pulttak", "flatt tak"]
KONSTRUKSJONSTYPE_OPTIONS = ["tre", "stål", "blandet", "ukjent"]
BAERELINJE_TYPES = ["yttervegg", "innervegg", "søylerekke", "drager", "ukjent"]


def render_barn_system_inputs() -> dict:
    st.markdown("### Bygningsgeometri")
    g1, g2, g3 = st.columns(3)
    lengde_m = g1.number_input("Lengde (m)", min_value=4.0, value=18.0, step=0.5)
    bredde_m = g2.number_input("Bredde (m)", min_value=4.0, value=10.0, step=0.5)
    antall_etasjer = int(g3.number_input("Antall etasjer", min_value=1, value=1, step=1))

    g4, g5, g6, g7 = st.columns(4)
    gesimshoyde_m = g4.number_input("Høyde til gesims (m)", min_value=2.0, value=3.2, step=0.1)
    monehoyde_m = g5.number_input("Høyde til møne (m)", min_value=gesimshoyde_m + 0.1, value=max(5.0, gesimshoyde_m + 0.1), step=0.1)
    taktype = g6.selectbox("Taktype", TAKTYPE_OPTIONS, index=0)
    takvinkel_grader = g7.number_input("Takvinkel (grader)", min_value=0.0, max_value=60.0, value=27.0, step=1.0)

    if monehoyde_m <= gesimshoyde_m:
        st.warning("Mønehøyde bør være høyere enn gesimshøyde for valgt takgeometri.")

    konstruksjonstype = st.selectbox("Konstruksjonstype", KONSTRUKSJONSTYPE_OPTIONS, index=0)

    st.markdown("### Eksisterende bæresystem")
    b1, b2, b3 = st.columns(3)
    antall_langsgaende = int(b1.number_input("Antall langsgående bærelinjer", min_value=0, value=2, step=1))
    antall_tverrgaende = int(b2.number_input("Antall tverrgående bærelinjer", min_value=0, value=2, step=1))
    yttervegger_baerende = b3.checkbox("Yttervegger antas bærende", value=True)

    b4, b5, b6 = st.columns(3)
    har_innvendig_baerevegg = b4.checkbox("Har innvendig bærevegg", value=True)
    innervegg_posisjon_m = b5.number_input(
        "Plassering av innvendig bærevegg fra venstre side (m)",
        min_value=0.0,
        value=max(bredde_m / 2.0, 0.0),
        step=0.1,
    )
    har_stolperekker = b6.checkbox("Har stolperekker", value=False)

    b7, b8, b9 = st.columns(3)
    antall_stolper = int(b7.number_input("Antall stolper", min_value=0, value=4, step=1))
    stolperekke_posisjon_m = b8.number_input(
        "Plassering av stolperekke fra venstre side (m)", min_value=0.0, value=max(bredde_m / 2.0, 0.0), step=0.1
    )
    stolpe_dimensjon = b9.text_input("Stolpedimensjon", value="98x98")

    tak_baeres_av = st.multiselect(
        "Taket bæres av",
        options=["yttervegger", "innervegg", "stolper", "kombinasjon"],
        default=["yttervegger", "innervegg"],
    )

    st.markdown("### Manuelle bærelinjer")
    manuelle_antall = int(st.number_input("Antall manuelle bærelinjer", min_value=0, value=0, step=1))
    manuelle_baerelinjer: list[dict] = []
    for idx in range(manuelle_antall):
        st.markdown(f"**Bærelinje {idx + 1}**")
        c1, c2, c3 = st.columns(3)
        navn = c1.text_input(f"Navn #{idx + 1}", value=f"Manuell linje {idx + 1}")
        line_type = c2.selectbox(f"Type #{idx + 1}", BAERELINJE_TYPES, key=f"manual_type_{idx}")
        baerer_tak = c3.checkbox("Bærer tak", value=True, key=f"manual_roof_{idx}")

        c4, c5, c6 = st.columns(3)
        x_start_m = c4.number_input(f"Start X #{idx + 1}", min_value=0.0, value=0.0, step=0.1, key=f"manual_xs_{idx}")
        y_start_m = c5.number_input(f"Start Y #{idx + 1}", min_value=0.0, value=0.0, step=0.1, key=f"manual_ys_{idx}")
        x_end_m = c6.number_input(f"Slutt X #{idx + 1}", min_value=0.0, value=lengde_m, step=0.1, key=f"manual_xe_{idx}")
        y_end_m = st.number_input(f"Slutt Y #{idx + 1}", min_value=0.0, value=bredde_m, step=0.1, key=f"manual_ye_{idx}")
        baerer_bjelkelag = st.checkbox("Bærer bjelkelag", value=False, key=f"manual_floor_{idx}")

        manuelle_baerelinjer.append(
            {
                "id": f"manual_{idx+1}",
                "navn": navn,
                "type": line_type,
                "x_start_m": x_start_m,
                "y_start_m": y_start_m,
                "x_end_m": x_end_m,
                "y_end_m": y_end_m,
                "baerer_tak": baerer_tak,
                "baerer_bjelkelag": baerer_bjelkelag,
                "status": "eksisterende",
            }
        )

    return {
        "building": {
            "lengde_m": lengde_m,
            "bredde_m": bredde_m,
            "gesimshoyde_m": gesimshoyde_m,
            "monehoyde_m": monehoyde_m,
            "taktype": taktype,
            "takvinkel_grader": takvinkel_grader,
            "antall_etasjer": antall_etasjer,
            "konstruksjonstype": konstruksjonstype,
            "grunnplan": "rektangulært",
        },
        "system": {
            "antall_langsgaende": antall_langsgaende,
            "antall_tverrgaende": antall_tverrgaende,
            "har_innvendig_baerevegg": har_innvendig_baerevegg,
            "innervegg_posisjon_m": innervegg_posisjon_m,
            "har_stolperekker": har_stolperekker,
            "har_stolper": har_stolperekker and antall_stolper > 0,
            "antall_stolper": antall_stolper,
            "stolperekke_posisjon_m": stolperekke_posisjon_m,
            "stolpe_dimensjon": stolpe_dimensjon,
            "stolpe_materiale": "tre",
            "yttervegger_baerende": yttervegger_baerende,
            "tak_baeres_av": tak_baeres_av,
            "manuelle_baerelinjer": manuelle_baerelinjer,
        },
    }
