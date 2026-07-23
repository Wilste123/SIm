from __future__ import annotations

WEATHER_SCENARIOS = {
    "Normal belastning": {
        "description": "Normal brukssituasjon med forenklet standard lastforutsetning.",
        "load_factor": 1.0,
        "risk_color": "green",
        "recommendations": ["kontroller utførelse", "sikre god innfesting"],
    },
    "Mye snø": {
        "description": "Forenklet scenario med markant økning i tak- og flatebelastning fra snø.",
        "load_factor": 1.25,
        "risk_color": "yellow",
        "recommendations": ["vurder større dimensjon", "reduser spennvidde", "kontroller snøopplag"],
    },
    "Våt snø": {
        "description": "Våt snø kan gi høyere egenvekt og mer vedvarende belastning.",
        "load_factor": 1.4,
        "risk_color": "yellow",
        "recommendations": ["legg til ekstra stendere", "vurder ekstra stolpe", "følg med på nedbøyning"],
    },
    "Sterk vind": {
        "description": "Sterk vind påvirker særlig avstivning, innfesting og sideveis stabilitet.",
        "load_factor": 1.2,
        "risk_color": "yellow",
        "recommendations": ["legg til kryssavstivning", "kontroller innfesting", "vurder vindtetting"],
    },
    "Storm": {
        "description": "Storm gir høye horisontale laster og krever ekstra oppmerksomhet rundt stabilitet.",
        "load_factor": 1.5,
        "risk_color": "red",
        "recommendations": ["kontroller innfesting", "legg til kryssavstivning", "kontakt byggingeniør ved usikkerhet"],
    },
    "Skjev last": {
        "description": "Skjev last kan gi ujevn lastfordeling og uventede lokale påkjenninger.",
        "load_factor": 1.3,
        "risk_color": "yellow",
        "recommendations": ["jevne ut lastfordeling", "legg inn ekstra stolpe", "vurder flere bjelker"],
    },
    "Snø + vind": {
        "description": "Kombinert scenario med både vertikal og horisontal påvirkning.",
        "load_factor": 1.55,
        "risk_color": "red",
        "recommendations": ["bruk større dimensjon", "kontroller innfesting", "kontakt byggingeniør ved usikkerhet"],
    },
}
