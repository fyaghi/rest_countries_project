import pandas as pd

df = pd.read_csv("data/raw/countries_flat.csv",
                 keep_default_na=False, na_values=[""])

summary = "Dataset shape:\n" + str(df.shape)

summary += "\n\nData types:\n" + str(df.dtypes)

missing = pd.DataFrame()
missing["missing_count"] = df.isnull().sum()
missing["missing_pct"] = df.isnull().sum() / len(df) * 100

missing.to_csv("reports/missing_values.csv")

summary += "\n\nMissing values:\n" + str(missing)

summary += "\n\nSummary statistics:\n"
summary += str(df[["population", "area_km2"]].describe())

summary += "\n\nCountries per region:\n"
summary += str(df["region"].value_counts())

summary += "\n\nDuplicate rows: " + str(df.duplicated().sum())
summary += "\nDuplicate codes: " + str(df["cca3"].dropna().duplicated().sum())
summary += "\nDuplicate names: " + str(df["name_common"].duplicated().sum())

summary += "\n\nCountries with missing codes:\n"
summary += str(df[df["cca3"].isnull()]["name_common"])

summary += "\n\nNegative population: " + str((df["population"] < 0).sum())
summary += "\nZero population: " + str((df["population"] == 0).sum())
summary += "\nInvalid area: " + str((df["area_km2"] <= 0).sum())

summary += "\n\nCountries with zero population:\n"
summary += str(df[df["population"] == 0]["name_common"])

df.loc[df["area_km2"] > 0, "density"] = df["population"] / df["area_km2"]

all_outliers = []

for col in ["population", "area_km2", "density"]:
    Q1 = df[col].quantile(0.25)
    Q3 = df[col].quantile(0.75)

    IQR = Q3 - Q1

    lower = Q1 - 1.5 * IQR
    upper = Q3 + 1.5 * IQR

    outliers = df[(df[col] < lower) | (df[col] > upper)]

    summary += "\n\nOutliers in " + col
    summary += "\nLower boundary: " + str(lower)
    summary += "\nUpper boundary: " + str(upper)
    summary += "\nNumber of outliers: " + str(len(outliers))

    temp = outliers[["name_common", col]].copy()
    temp["outlier_in"] = col
    all_outliers.append(temp)

pd.concat(all_outliers).to_csv("reports/outliers.csv", index=False)

print(summary)

with open("reports/profiling_summary.txt", "w", encoding="utf-8") as f:
    f.write(summary)