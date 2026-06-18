# Global CO2 Dashboard

Power BI-style Streamlit dashboard for a Data Visualization course project using the Our World in Data CO2 dataset.

## Dataset

Place the OWID file at:

```bash
data/raw/owid-co2-data.csv
```

The project separates true country rows from aggregate rows such as `World`, `Asia`, `Europe`, `European Union`, and OWID rows whose `iso_code` starts with `OWID_`. Aggregate rows are never used in country rankings.

## Install

```bash
pip install -r requirements.txt
```

## Build Data

```bash
python -m src.data.build_datasets
```

This writes cleaned and dashboard-ready CSVs into `data/processed/` and `data/aggregated/`.

## Run Dashboard

```bash
streamlit run streamlit_app/app.py
```

If processed files are missing, the app attempts to build them automatically from the raw CSV.

## Dashboard Pages

1. **Global Snapshot**: current global emissions, choropleth map, regional treemap, top emitters, KPI cards, and generated insights.
2. **Historical Evolution**: annotated global time series, cumulative responsibility ranking, and regional small multiples.
3. **Current Trend Analysis**: growth-versus-emissions bubble scatter, fastest increasing and declining countries, and fuel-source decomposition.

## Key Metrics

- Annual CO2 emissions
- CO2 per capita
- Cumulative CO2
- Share of world CO2
- Five-year CAGR and absolute change
- Fuel-source shares for coal, oil, gas, cement, flaring, and land-use change

## Visualization Principles

The dashboard prioritizes position and length encodings, sorted horizontal bars, annotated time series, small multiples instead of crowded line charts, and treemaps only for hierarchical part-to-whole composition. It avoids pie charts, 3D charts, and decorative visuals without analytical value.

## Folder Structure

- `src/data/`: loading, cleaning, feature engineering, and dataset builds
- `src/analysis/`: reusable KPI, ranking, trend, fuel, and insight functions
- `src/visualization/`: Plotly chart and map builders
- `src/utils/`: paths, constants, formatting, helpers
- `streamlit_app/`: Streamlit entry point, pages, components, and CSS

## Limitations

Region assignment is inferred for country rows and includes explicit mappings for common emitters, with unmatched countries labeled `Unknown`. Optional OWID columns are handled safely; charts degrade gracefully when a metric is absent.
