import pandas as pd

df = pd.read_csv("data/raw/countries_flat.csv",
                 keep_default_na=False, na_values=[""])

rows_before = len(df)

# Remove duplicates
df = df.drop_duplicates()

# Keep countries with missing ISO codes
df["has_iso_code"] = df["cca3"].notnull()

# Handle missing values
df["capital"] = df["capital"].fillna("Not listed")
df["subregion"] = df["subregion"].fillna("Not listed")

df["languages"] = df["languages"].fillna("Not listed")
df["currency_codes"] = df["currency_codes"].fillna("Not listed")
df["currency_names"] = df["currency_names"].fillna("Not listed")

# Handle countries with no land borders
df.loc[df["n_borders"] == 0, "borders"] = "No land borders"
df["borders"] = df["borders"].fillna("Not listed")

# Fix inconsistent subregion names
df["subregion"] = df["subregion"].replace(
    "Southeast Europe", "South-Eastern Europe")

# Calculate population density
df["density"] = df["population"] / df["area_km2"]

# Keep and flag outliers
for col in ["population", "area_km2", "density"]:
    Q1 = df[col].quantile(0.25)
    Q3 = df[col].quantile(0.75)

    IQR = Q3 - Q1

    lower = Q1 - 1.5 * IQR
    upper = Q3 + 1.5 * IQR

    df["is_outlier_" + col] = (df[col] < lower) | (df[col] > upper)

# Save cleaned data
df.to_csv("data/clean/countries_clean.csv", index=False)

# Document cleaning decisions
log = "Rows before cleaning: " + str(rows_before)
log += "\nRows after cleaning: " + str(len(df))
log += "\nDuplicates removed: " + str(rows_before - len(df))

log += "\nMissing ISO codes were kept and flagged."
log += "\nMissing text values were replaced with Not listed."
log += "\nCountries with no land borders were labelled."
log += "\nSubregion names were standardized."
log += "\nZero populations were kept because some territories are uninhabited."
log += "\nOutliers were flagged instead of removed because extreme values can be valid."

log += "\n\nRemaining missing values:\n" + str(df.isnull().sum())

print(log)
print(df.shape)

with open("reports/cleaning_log.txt", "w", encoding="utf-8") as f:
    f.write(log)