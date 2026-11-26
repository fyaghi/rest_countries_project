import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

CLEAN_PATH = os.path.join("data", "clean", "countries_clean.csv")
FIG_DIR = os.path.join("reports", "figures")

REGION_COLORS = {
    "Africa": "#E69F00",
    "Americas": "#56B4E9",
    "Asia": "#D55E00",
    "Europe": "#0072B2",
    "Oceania": "#009E73",
    "Antarctic": "#999999",
}


def save(fig, name):
    path = os.path.join(FIG_DIR, name)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"Saved -> {path}")


def main():
    os.makedirs(FIG_DIR, exist_ok=True)
    df = pd.read_csv(CLEAN_PATH, keep_default_na=False, na_values=[""])
    inhabited = df[(df["population"] > 0) & (df["region"] != "Antarctic")]

    q1 = "Q1: Which regions hold most of the world's population?"
    pop = inhabited.groupby("region")["population"].sum().sort_values() / 1e9
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.barh(pop.index, pop.values, color=[REGION_COLORS[r] for r in pop.index])
    for i, v in enumerate(pop.values):
        ax.text(v + 0.05, i, f"{v:.2f} B", va="center")
    ax.set_xlabel("Total population (billions)")
    ax.set_title("Total population by region")
    save(fig, "chart1_population_by_region.png")
    share = pop / pop.sum() * 100
    print(f"   {q1}\n   Finding: Asia = {share['Asia']:.1f}% of the total; "
          f"Oceania = {share['Oceania']:.1f}%.\n")

    q2 = "Q2: How spread out are country populations within each region?"
    regions = ["Africa", "Americas", "Asia", "Europe", "Oceania"]
    data = [inhabited.loc[inhabited["region"] == r, "log10_population"] for r in regions]
    fig, ax = plt.subplots(figsize=(8, 5))
    box = ax.boxplot(data, patch_artist=True)
    for patch, r in zip(box["boxes"], regions):
        patch.set_facecolor(REGION_COLORS[r])
        patch.set_alpha(0.7)
    ax.set_xticks(range(1, len(regions) + 1))
    ax.set_xticklabels(regions)
    ax.set_yticks([2, 3, 4, 5, 6, 7, 8, 9])
    ax.set_yticklabels(["100", "1K", "10K", "100K", "1M", "10M", "100M", "1B"])
    ax.set_ylabel("Population (log scale)")
    ax.set_title("Distribution of country populations by region")
    save(fig, "chart2_population_distribution.png")
    medians = inhabited.groupby("region")["population"].median().sort_values()
    print(f"   {q2}\n   Finding: median population is lowest in {medians.index[0]} "
          f"({medians.iloc[0]:,.0f}) and highest in {medians.index[-1]} "
          f"({medians.iloc[-1]:,.0f}).\n")

    q3 = "Q3: Do bigger countries have bigger populations?"
    fig, ax = plt.subplots(figsize=(8, 6))
    for r in regions:
        sub = inhabited[inhabited["region"] == r]
        ax.scatter(sub["area_km2"], sub["population"], label=r,
                   color=REGION_COLORS[r], alpha=0.7, s=30)
    for name in ["China", "India", "Russia", "Canada", "Monaco", "Singapore"]:
        row = inhabited[inhabited["name_common"] == name]
        if not row.empty:
            ax.annotate(name, (row["area_km2"].iloc[0], row["population"].iloc[0]),
                        fontsize=8, xytext=(4, 4), textcoords="offset points")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("Area (km², log scale)")
    ax.set_ylabel("Population (log scale)")
    ax.set_title("Area vs population")
    ax.legend(title="Region")
    save(fig, "chart3_area_vs_population.png")
    corr = inhabited["log10_area"].corr(inhabited["log10_population"])
    print(f"   {q3}\n   Finding: correlation between log(area) and log(population) "
          f"= {corr:.2f}.\n")

    q4 = "Q4: Which sovereign states are the most crowded?"
    top = (df[df["entity_type"] == "Sovereign state"]
           .nlargest(10, "density").sort_values("density"))
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.barh(top["name_common"], top["density"],
            color=[REGION_COLORS[r] for r in top["region"]])
    ax.set_xlabel("People per km²")
    ax.set_title("Top 10 most densely populated sovereign states")
    save(fig, "chart4_top10_density.png")
    print(f"   {q4}\n   Finding: most crowded = {top['name_common'].iloc[-1]} "
          f"({top['density'].iloc[-1]:,.0f} people/km²).\n")

    q5 = "Q5: Which regions have the most languages and currencies per country?"
    div = inhabited.groupby("region")[["n_languages", "n_currencies"]].mean().loc[regions]
    fig, ax = plt.subplots(figsize=(8, 5))
    x = range(len(regions))
    ax.bar([i - 0.2 for i in x], div["n_languages"], width=0.4, label="Languages", color="#0072B2")
    ax.bar([i + 0.2 for i in x], div["n_currencies"], width=0.4, label="Currencies", color="#E69F00")
    ax.set_xticks(list(x))
    ax.set_xticklabels(regions)
    ax.set_ylabel("Average number per country")
    ax.set_title("Average languages and currencies per country, by region")
    ax.legend()
    save(fig, "chart5_language_currency_diversity.png")
    most_lang = df.nlargest(1, "n_languages")
    print(f"   {q5}\n   Finding: highest avg languages = {div['n_languages'].idxmax()} "
          f"({div['n_languages'].max():.2f}); single country with most = "
          f"{most_lang['name_common'].iloc[0]} ({most_lang['n_languages'].iloc[0]}).\n")

    q6 = "Q6: Where in the world are the biggest populations located?"
    fig, ax = plt.subplots(figsize=(11, 6))
    size = inhabited["population"] / inhabited["population"].max() * 2500 + 5
    ax.scatter(inhabited["lng"], inhabited["lat"], s=size,
               c=[REGION_COLORS[r] for r in inhabited["region"]],
               alpha=0.5, edgecolors="white", linewidths=0.5)
    for _, row in inhabited.nlargest(6, "population").iterrows():
        ax.annotate(row["name_common"], (row["lng"], row["lat"]), fontsize=8, ha="center")
    ax.set_xlim(-180, 180)
    ax.set_ylim(-60, 85)
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.set_title("World population bubble map (bubble size = population)")
    ax.grid(alpha=0.3)
    for r in regions:
        ax.scatter([], [], color=REGION_COLORS[r], label=r, s=60)
    ax.legend(title="Region", loc="lower left")
    save(fig, "chart6_world_bubble_map.png")
    north = inhabited.loc[inhabited["lat"] > 0, "population"].sum() / inhabited["population"].sum() * 100
    print(f"   {q6}\n   Finding: {north:.1f}% of the population lives in countries "
          f"north of the equator.\n")


if __name__ == "__main__":
    main()