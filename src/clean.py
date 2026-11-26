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

    # D1: Namibia's code is "NA" so we don't let pandas read it as missing
    df = pd.read_csv(RAW_PATH, keep_default_na=False, na_values=[""])
    rows_before = len(df)
    note(f"D1  Read raw data: {rows_before} rows. 'NA' kept as text "
         f"(Namibia cca2 = {df.loc[df['name_common'] == 'Namibia', 'cca2'].iloc[0]}).")

    # D2: remove extra spaces so values like "Asia " and "Asia" match
    for col in df.columns:
        if is_text(df[col]):
            df[col] = df[col].str.strip()
    note("D2  Stripped leading/trailing spaces from all text columns.")

    # D3: remove duplicates by name (not cca3 because some have no code)
    dupes = df.duplicated(subset="name_common").sum()
    df = df.drop_duplicates(subset="name_common")
    note(f"D3  Duplicate countries removed: {dupes}.")

    # D4: keep countries with no ISO code but flag them, they are still real places
    df["has_iso_code"] = df["cca3"].notna()
    no_code = df.loc[~df["has_iso_code"], "name_common"].tolist()
    note(f"D4  Kept and flagged {len(no_code)} entities without ISO codes: {no_code}.")

    # D5: Antarctic has no subregion so we just use "Antarctic"
    mask = df["subregion"].isna() & (df["region"] == "Antarctic")
    df.loc[mask, "subregion"] = "Antarctic"
    note(f"D5  Filled subregion = 'Antarctic' for {mask.sum()} Antarctic entities.")

    # D6: make this subregion name match the style of the others
    df["subregion"] = df["subregion"].replace({"Southeast Europe": "South-Eastern Europe"})
    note("D6  Renamed 'Southeast Europe' -> 'South-Eastern Europe' for consistency.")

    # D7: empty borders = islands with no neighbours, not missing data
    df["has_land_borders"] = df["n_borders"] > 0
    islands = df["borders"].isna().sum()
    df["borders"] = df["borders"].fillna("None")
    note(f"D7  {islands} entities with no land borders: borders = 'None', flag has_land_borders.")

    # D8: some places really have no capital (like Antarctica)
    df["has_capital"] = df["capital"].notna()
    note(f"D8  {(~df['has_capital']).sum()} entities have no capital: "
         f"{df.loc[~df['has_capital'], 'name_common'].tolist()}.")
    df["capital"] = df["capital"].fillna("No capital")

    # D9: no language or currency only happens for uninhabited places
    for col in ["languages", "currency_codes", "currency_names"]:
        n = df[col].isna().sum()
        df[col] = df[col].fillna("None")
        note(f"D9  {col}: filled {n} missing with 'None'.")

    # D10: population 0 is real (nobody lives there) so we keep it and flag it
    df["is_uninhabited"] = df["population"] == 0
    note(f"D10 Flagged {df['is_uninhabited'].sum()} uninhabited entities: "
         f"{df.loc[df['is_uninhabited'], 'name_common'].tolist()}.")

    # D11: label each row as sovereign state, territory or partially recognised
    df["entity_type"] = np.select(
        [~df["has_iso_code"], df["sovereign"] == True],
        ["Partially recognised", "Sovereign state"],
        default="Territory",
    )
    note("D11 entity_type counts: " + df["entity_type"].value_counts().to_dict().__str__())

    # D12: outliers like China and India are real so we flag them instead of deleting
    df["density"] = (df["population"] / df["area_km2"]).round(2)
    for col in ["population", "area_km2", "density"]:
        q1, q3 = df[col].quantile([0.25, 0.75])
        high = q3 + 1.5 * (q3 - q1)
        df[f"is_outlier_{col}"] = df[col] > high
        note(f"D12 {col}: {df[f'is_outlier_{col}'].sum()} outliers flagged (kept).")

    # D13: log columns make the charts easier to read (log of 0 is left empty)
    df["log10_population"] = np.log10(df["population"].where(df["population"] > 0)).round(3)
    df["log10_area"] = np.log10(df["area_km2"].where(df["area_km2"] > 0)).round(3)
    note("D13 Added log10_population and log10_area.")

    # final check of what is still missing
    note("")
    note(f"Rows before: {rows_before}   Rows after: {len(df)}")
    remaining = df.isna().sum()
    remaining = remaining[remaining > 0]
    note("Remaining missing values (expected: only codes for no-ISO entities, "
         "and log10_population for uninhabited):")
    note(remaining.to_string() if len(remaining) else "None")

    # save the clean data and the log
    df = df.sort_values("name_common").reset_index(drop=True)
    out_path = os.path.join(CLEAN_DIR, "countries_clean.csv")
    df.to_csv(out_path, index=False, encoding="utf-8")
    note(f"\nSaved clean dataset -> {out_path}  ({df.shape[0]} rows x {df.shape[1]} columns)")

    with open(os.path.join(REPORT_DIR, "cleaning_log.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(log))
    print("Saved -> reports/cleaning_log.txt")


if __name__ == "__main__":
    main()