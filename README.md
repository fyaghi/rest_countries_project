# REST Countries Project – Milestone 1

**Data Acquisition, Profiling & Cleaning**
Data Engineering Lab – Princess Sumaya University for Technology

## Team
| Name | Student ID |
|------|-----------|
| Yahia Fawwaz | 20250581 |
| Feras Yaghi| 20250578 |
| Joud Himo| 20250400 |

## Overview
We extracted all countries from the REST Countries API, flattened the nested JSON
fields (languages, currencies, borders, capitals) into a table, profiled the raw
data for quality issues, cleaned it with a documented and reproducible script,
and produced 6 exploratory visualizations.

> **Note:** The original v3.1 API was retired during the project, so the
> extraction uses the new **v5 API** (`api.restcountries.com/countries/v5`),
> which needs a free API key and returns paginated results (100 per page).

## Repository structure
```
data/
  raw/countries_raw.json      raw API records (254 entities)
  raw/countries_flat.csv      flattened, uncleaned table
  clean/countries_clean.csv   cleaned dataset (254 rows x 32 columns)
src/
  extract.py      download + flatten
  profiling.py    data quality report
  clean.py        cleaning with documented decisions (D1–D13)
  visualize.py    6 charts
reports/
  profiling_summary.txt, missing_values.csv, outliers.csv
  cleaning_log.txt
  figures/        chart1 … chart6 (PNG)
ai-logs/milestone1/   AI usage disclosure
```

## How to reproduce
1. Install the requirements:
   ```
   pip install requests pandas matplotlib plotly
   ```
2. Get a free API key at restcountries.com and save it in a file called
   `api_key.txt` in the project root. This file is in `.gitignore` and is never uploaded.
3. Run the pipeline in order from the project root:
   ```
   python src/extract.py
   python src/profiling.py
   python src/clean.py
   python src/visualize.py
   ```

## Key cleaning decisions (full list in `src/clean.py` and `reports/cleaning_log.txt`)
- Read `"NA"` as text, so Namibia's ISO code is not mistaken for a missing value.
- Partially recognised states with no ISO code (Abkhazia, Northern Cyprus,
  Somaliland, South Ossetia) are **kept and flagged**, not dropped.
- Empty borders mean "no land borders" (islands), not missing data.
- Uninhabited islands (population 0) are kept and flagged as `is_uninhabited`.
- Outliers (e.g. China, India, Russia, Monaco) are real values, so they are **flagged, not removed**.
- Added `entity_type`, `density`, `log10_population` and `log10_area`.