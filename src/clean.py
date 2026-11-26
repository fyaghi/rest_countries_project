"""
clean.py - Milestone 1, Step 3: Data Cleaning
Reads the raw flattened dataset, applies documented cleaning decisions,
and saves a clean dataset plus a cleaning log.

Run from the project root:  python src/clean.py
Outputs:
    data/clean/countries_clean.csv
    reports/cleaning_log.txt
"""

import os

import numpy as np
import pandas as pd

RAW_PATH = os.path.join("data", "raw", "countries_flat.csv")
CLEAN_DIR = os.path.join("data", "clean")
REPORT_DIR = "reports"

log = []


def note(msg):
    print(msg)
    log.append(msg)


def is_text(series):
    return pd.api.types.is_string_dtype(series) or series.dtype == object


def main():
    os.makedirs(CLEAN_DIR, exist_ok=True)
    os.makedirs(REPORT_DIR, exist_ok=True)

    # DECISION 1: Read "NA" as text, not as missing.
    # Why: Namibia's ISO code is "NA". pandas treats "NA" as missing by default,
    # which wrongly made Namibia's cca2 empty. Only truly empty cells are missing.
    df = pd.read_csv(RAW_PATH, keep_default_na=False, na_values=[""])
    rows_before = len(df)
    note(f"D1  Read raw data: {rows_before} rows. 'NA' kept as text "
         f"(Namibia cca2 = {df.loc[df['name_common'] == 'Namibia', 'cca2'].iloc[0]}).")

    # DECISION 2: Strip extra spaces from all text columns.
    # Why: hidden spaces break grouping and joins (e.g. 'Asia ' vs 'Asia').
    for col in df.columns:
        if is_text(df[col]):
            df[col] = df[col].str.strip()
    note("D2  Stripped leading/trailing spaces from all text columns.")

    # DECISION 3: Remove duplicate countries (by common name).
    # Why: each country must appear once. cca3 cannot be used because some
    # entities have no code (see D4).
    dupes = df.duplicated(subset="name_common").sum()
    df = df.drop_duplicates(subset="name_common")
    note(f"D3  Duplicate countries removed: {dupes}.")

    # DECISION 4: KEEP partially recognised states with no ISO code, and FLAG them.
    # Why: they are real entities with population and area, so dropping them
    # loses data. We cannot invent ISO codes, so codes stay empty.
    df["has_iso_code"] = df["cca3"].notna()
    no_code = df.loc[~df["has_iso_code"], "name_common"].tolist()
    note(f"D4  Kept and flagged {len(no_code)} entities without ISO codes: {no_code}.")

    # DECISION 5: Fill missing subregion for the Antarctic region with 'Antarctic'.
    # Why: the Antarctic region has no subregions, so the value is not unknown,
    # it simply equals the region.
    mask = df["subregion"].isna() & (df["region"] == "Antarctic")
    df.loc[mask, "subregion"] = "Antarctic"
    note(f"D5  Filled subregion = 'Antarctic' for {mask.sum()} Antarctic entities.")

    # DECISION 6: Standardise inconsistent subregion names.
    # Why: 'Southeast Europe' uses a different style than 'South-Eastern Asia'.
    df["subregion"] = df["subregion"].replace({"Southeast Europe": "South-Eastern Europe"})
    note("D6  Renamed 'Southeast Europe' -> 'South-Eastern Europe' for consistency.")

    # DECISION 7: Empty borders mean 'no land borders' (islands), not missing data.
    # Why: n_borders is already 0 for these rows. We fill text with 'None'
    # and add a clear flag.
    df["has_land_borders"] = df["n_borders"] > 0
    islands = df["borders"].isna().sum()
    df["borders"] = df["borders"].fillna("None")
    note(f"D7  {islands} entities with no land borders: borders = 'None', flag has_land_borders.")

    # DECISION 8: Missing capital -> 'No capital' + flag.
    # Why: Antarctica and uninhabited islands genuinely have no capital.
    df["has_capital"] = df["capital"].notna()
    note(f"D8  {(~df['has_capital']).sum()} entities have no capital: "
         f"{df.loc[~df['has_capital'], 'name_common'].tolist()}.")
    df["capital"] = df["capital"].fillna("No capital")

    # DECISION 9: Missing languages / currencies -> 'None'.
    # Why: they occur only for uninhabited places; the counts are already 0.
    for col in ["languages", "currency_codes", "currency_names"]:
        n = df[col].isna().sum()
        df[col] = df[col].fillna("None")
        note(f"D9  {col}: filled {n} missing with 'None'.")

    # DECISION 10: Population = 0 is KEPT (true value) and FLAGGED as uninhabited.
    # Why: these islands really have no permanent population. Imputing a number
    # would be false. They are excluded only from log-scale charts.
    df["is_uninhabited"] = df["population"] == 0
    note(f"D10 Flagged {df['is_uninhabited'].sum()} uninhabited entities: "
         f"{df.loc[df['is_uninhabited'], 'name_common'].tolist()}.")

    # DECISION 11: Classify each entity.
    # Why: the API mixes sovereign states, territories and partially recognised
    # states. Analysis can then filter to the right group.
    df["entity_type"] = np.select(
        [~df["has_iso_code"], df["sovereign"] == True],
        ["Partially recognised", "Sovereign state"],
        default="Territory",
    )
    note("D11 entity_type counts: " + df["entity_type"].value_counts().to_dict().__str__())

    # DECISION 12: Outliers are KEPT and FLAGGED (IQR method), not removed.
    # Why: India, China, Russia, Monaco etc. are real values, not errors.
    df["density"] = (df["population"] / df["area_km2"]).round(2)
    for col in ["population", "area_km2", "density"]:
        q1, q3 = df[col].quantile([0.25, 0.75])
        high = q3 + 1.5 * (q3 - q1)
        df[f"is_outlier_{col}"] = df[col] > high
        note(f"D12 {col}: {df[f'is_outlier_{col}'].sum()} outliers flagged (kept).")

    # DECISION 13: Add log10 columns for skewed variables.
    # Why: population and area are heavily right-skewed (mean >> median),
    # so log scale makes charts readable. log of 0 is undefined -> left empty.
    df["log10_population"] = np.log10(df["population"].where(df["population"] > 0)).round(3)
    df["log10_area"] = np.log10(df["area_km2"].where(df["area_km2"] > 0)).round(3)
    note("D13 Added log10_population and log10_area.")

     # FINAL CHECKS
    note("")
    note(f"Rows before: {rows_before}   Rows after: {len(df)}")
    remaining = df.isna().sum()
    remaining = remaining[remaining > 0]
    note("Remaining missing values (expected: only codes for no-ISO entities, "
         "and log10_population for uninhabited):")
    note(remaining.to_string() if len(remaining) else "None")

    df = df.sort_values("name_common").reset_index(drop=True)
    out_path = os.path.join(CLEAN_DIR, "countries_clean.csv")
    df.to_csv(out_path, index=False, encoding="utf-8")
    note(f"\nSaved clean dataset -> {out_path}  ({df.shape[0]} rows x {df.shape[1]} columns)")

    with open(os.path.join(REPORT_DIR, "cleaning_log.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(log))
    print("Saved -> reports/cleaning_log.txt")


if __name__ == "__main__":
    main()