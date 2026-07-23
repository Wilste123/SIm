# LåveSim

LåveSim er en Streamlit-basert MVP for forenklet visualisering, materialberegning og enkel bærevurdering av små konstruksjoner som låver, uthus, boder, enkle vegger og bjelker.

> Dette verktøyet gir kun forenklede beregninger og visuelle estimater. Resultatene skal ikke brukes som endelig dokumentasjon for bærende konstruksjoner. Ved tiltak som påvirker bæreevne, stabilitet eller personsikkerhet må løsningen kontrolleres av kvalifisert fagperson/byggingeniør.

## Formål

Appen er laget som et praktisk hjelpemiddel for:

- prosjektoversikt
- vegg- og stenderoppsett
- materialliste og kostnadsestimat
- enkel bjelke- og lastvurdering
- pedagogiske last- og uværsscenarioer
- JSON-eksport av prosjektdata

## Installasjon

### macOS / Linux

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

### Windows

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

## Kjøring

```bash
streamlit run app.py
```

## Funksjoner

- Prosjektinformasjon på norsk
- Vegg/stendergenerator med dør- og vindusåpninger
- 2D Plotly-tegning av vegg
- Materialliste med svinn og kostnadsestimat
- Enkel bjelkekalkulator for punktlast og jevnt fordelt last
- Last- og uværsscenarioer med anbefalte tiltak
- Samlet grønn/gul/rød risikovurdering
- JSON-eksport for rapport og videre arbeid

## Begrensninger

- Alle beregninger er forenklede estimater
- Appen er ikke et godkjent prosjekteringsgrunnlag
- Eurokode etterleves ikke fullt ut
- PDF-rapport er foreløpig kun markert som TODO

## Planlagte forbedringer

- Enkel PDF-eksport
- Flere konstruksjonstyper og detaljerte lastmodeller
- Bedre håndtering av flere åpninger
- Prosjektlagring i database
- Mer avansert visualisering og rapportering
