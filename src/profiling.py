import os
import pandas as pd

RAW_PATH = os.path.join("data", "raw", "countries_flat.csv")
REPORT_DIR = "reports"

lines = []

def report(text=""):
    print(text)
    lines.append(str(text))

def section(title):
    report("")
    report("=" * 60)
    report(title)
    report("=" * 60)

def iqr_outliers(df, column):
    q1 = df[column].quantile(0.25)
    q3 = df[column].quantile(0.75)
    iqr = q3 - q1
    low = q1 - 1.5 * iqr
    high = q3 + 1.5 * iqr
    mask = (df[column] < low) | (df[column] > high)
    return df[mask], low, high

def main():
    os.makedirs(REPORT_DIR, exist_ok=True)
    df = pd.read_csv(RAW_PATH)

    section("1. DATASET SHAPE")
    report(f"Rows: {df.shape[0]}   Columns: {df.shape[1]}")

    section("2. DATA TYPES")
    report(df.dtypes.to_string())

    section("3. MISSING VALUES")
    missing = pd.DataFrame({
        "missing_count": df.isna().sum(),
        "missing_pct": (df.isna().mean() * 100).round(2),
    }).sort_values("missing_count", ascending=False)
    report(missing.to_string())
    missing.to_csv(os.path.join(REPORT_DIR, "missing_values.csv"))

    report("\nCountries with no capital:")
    report(df.loc[df["capital"].isna(), "name_common"].tolist())
    report("\nCountries with no currency:")
    report(df.loc[df["currency_codes"].isna(), "name_common"].tolist())
    report("\nCountries with no language:")
    report(df.loc[df["languages"].isna(), "name_common"].tolist())

    section("4. SUMMARY STATISTICS (population, area)")
    report(df[["population", "area_km2"]].describe().round(2).to_string())

    section("5. COUNTRIES PER REGION")
    report(df["region"].value_counts(dropna=False).to_string())
    section("5b. COUNTRIES PER SUBREGION")
    report(df["subregion"].value_counts(dropna=False).to_string())

    section("6. DUPLICATES")
    report(f"Duplicate cca3 codes: {df['cca3'].duplicated().sum()}")
    report(f"Duplicate common names: {df['name_common'].duplicated().sum()}")
    report(f"Fully duplicated rows: {df.duplicated().sum()}")

    section("7. SUSPICIOUS VALUES")
    report(f"Population = 0: {(df['population'] == 0).sum()}")
    report(f"Area <= 0: {(df['area_km2'] <= 0).sum()}")
    report(f"Not sovereign (territories etc.): {(df['sovereign'] == False).sum()}")
    report(f"Not UN members: {(df['un_member'] == False).sum()}")
    report(f"No land borders (borders empty): {df['borders'].isna().sum()}")
    report("\nSmallest 5 populations:")
    report(df.nsmallest(5, "population")[["name_common", "population"]].to_string(index=False))

    section("8. OUTLIERS (IQR method, 1.5 x IQR)")
    df["density"] = df["population"] / df["area_km2"]
    all_outliers = []
    for col in ["population", "area_km2", "density"]:
        out, low, high = iqr_outliers(df, col)
        report(f"\n{col}: {len(out)} outliers (normal range {low:,.0f} to {high:,.0f})")
        top = out.sort_values(col, ascending=False).head(5)
        report(top[["name_common", col]].to_string(index=False))
        temp = out[["name_common", col]].copy()
        temp["outlier_in"] = col
        all_outliers.append(temp)
    pd.concat(all_outliers).to_csv(os.path.join(REPORT_DIR, "outliers.csv"), index=False)

    with open(os.path.join(REPORT_DIR, "profiling_summary.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print("\nSaved -> reports/profiling_summary.txt, missing_values.csv, outliers.csv")

if __name__ == "__main__":
    main()