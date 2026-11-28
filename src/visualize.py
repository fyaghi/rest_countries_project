import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("data/clean/countries_clean.csv",
                 keep_default_na=False, na_values=[""])

# Chart 1: Population by region
population = df.groupby("region")["population"].sum() / 1000000

plt.figure()
plt.bar(population.index, population.values)
plt.title("Total Population by Region")
plt.xlabel("Region")
plt.ylabel("Population (millions)")
plt.tight_layout()
plt.savefig("reports/figures/population_by_region.png")
plt.close()

print("Population by region:")
print(population)

# Chart 2: Population distribution
plt.figure()
plt.hist(df["population"] / 1000000, bins=20)
plt.title("Population Distribution")
plt.xlabel("Population (millions)")
plt.ylabel("Number of countries")
plt.tight_layout()
plt.savefig("reports/figures/population_distribution.png")
plt.close()

print("\nPopulation statistics:")
print(df["population"].describe())

# Chart 3: Area vs population
plt.figure()
plt.scatter(df["area_km2"], df["population"])
plt.title("Area vs Population")
plt.xlabel("Area (km2)")
plt.ylabel("Population")
plt.tight_layout()
plt.savefig("reports/figures/area_vs_population.png")
plt.close()

# Chart 4: Top 10 countries by population density
countries = df[(df["sovereign"] == True) &
               (df["has_iso_code"] == True)]

top = countries.sort_values("density", ascending=False).head(10)

plt.figure()
plt.barh(top["name_common"], top["density"])
plt.title("Top 10 Countries by Population Density")
plt.xlabel("People per km2")
plt.ylabel("Country")
plt.tight_layout()
plt.savefig("reports/figures/population_density.png")
plt.close()

print("\nTop 10 countries by density:")
print(top[["name_common", "density"]])

# Chart 5: Average number of languages by region
languages = df.groupby("region")["n_languages"].mean()

plt.figure()
plt.bar(languages.index, languages.values)
plt.title("Average Number of Languages by Region")
plt.xlabel("Region")
plt.ylabel("Average number of languages")
plt.tight_layout()
plt.savefig("reports/figures/language_diversity.png")
plt.close()

print("\nAverage languages by region:")
print(languages)

print("\nAll five charts saved.")
