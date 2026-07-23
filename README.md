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
- **3D Låvemodell** med interaktiv endringsanalyse (se under)

## 3D Låvemodell

Fanen **3D Låvemodell** tilbyr en parametrisk 3D-visualisering av en låve og pedagogisk
konsekvensanalyse ved endring av bærende konstruksjoner.

### Hva modulen gjør

- Genererer en enkel 3D-modell av låven basert på brukerens mål og bæresystemvalg
- Viser yttervegger, innvendig bærevegg, søyler, dragere, takflater og lastpiler
- Lar brukeren velge et element fra en nedtrekksliste og simulere:
  - Fjerning
  - Forsterkning
  - Erstatning med drager
  - Tillegg av søyle
  - Marking som bærende/ikke bærende
- Viser modell **før og etter** endringen side om side
- Beregner forenklet lastfordeling og prosentvis lastøkning på gjenværende elementer
- Varsler om manglende lastveier
- Vurderer horisontal stabilitet forenklet
- Gir grønn/gul/rød risikoindikasjon med anbefalte tiltak
- Eksporterer analysen som JSON

### Slik brukes den

1. Åpne fanen **3D Låvemodell**
2. Fyll inn bygningsmål og bæresystem under "Bygningsmål og bæresystem"
3. Velg element fra nedtrekkslisten under "Velg element i modellen"
4. Velg handling (fjern, forsterk, erstatt med drager, osv.)
5. Se **Etter endring**-figuren for å observere konsekvensen
6. Les risikoindikasjon og anbefalte tiltak
7. Last ned analysen som JSON ved behov

### Begrensninger

- Forenklet pedagogisk analyse – **ikke godkjent prosjekteringsgrunnlag**
- Appen dimensjonerer ikke konstruksjoner etter Eurokode
- Lastberegninger er grove arealestimater, ikke FEM-analyse
- 3D-modellen er visuelt forenklet – veggtykkelser er ikke i full målestokk
- Klikk direkte på 3D-objekter for elementvalg er ikke implementert (bruker selectbox)
- **Ved fjerning eller endring av bærende konstruksjoner må løsningen alltid kontrolleres av kvalifisert fagperson/byggingeniør**

### TODO – Fase 2

- Custom React/Three.js Streamlit-komponent
- Klikk direkte på objekter i 3D
- Dra/flytte søyler og vegger
- Legge til drager med mus
- Sanntidsanalyse ved endringer
- Eksport til GLB/OBJ

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
