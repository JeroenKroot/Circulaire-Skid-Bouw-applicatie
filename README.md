# LBK Prefab App

Streamlit-webapp voor het samenstellen van een prefab LBK-aansluitset (module 5 conform ISSO 44) met automatische berekening van:

- verkoopprijs
- totale CO2-uitstoot
- stuklijst
- materialenpaspoort

## Installatie

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -e .[dev]
```

## Starten

```bash
streamlit run app.py
```

## Brondata

Plaats de bronbestanden in:

- `data/source/input app.xlsx`
- of `data/source/input app.csv`

Bij de eerste start worden componenten en prototype-prijsregels automatisch in SQLite geladen.

## Belangrijke aannames

- CO2 wordt berekend als `Co2 eq kg × Gewicht [kg] × aantal`.
- Verkoopprijs = materiaalinkoop + montagekosten + 15% toeslag + 5% marge.
- Montagekosten gebruiken standaard een uurtarief van €80/uur.
- Prijsregels in v0.1 zijn prototype-aannames en moeten later worden vervangen door interne prijsdata of een ERP-koppeling.

## Tests uitvoeren

```bash
pytest
```
