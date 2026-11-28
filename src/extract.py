import pandas as pd
import requests
import json

url = "https://api.restcountries.com/countries/v5"

with open("api_key.txt", "r") as f:
    api_key = f.read().strip()

headers = {"Authorization": "Bearer " + api_key}

countries = []
offset = 0

while True:
    params = {"limit": 100, "offset": offset}
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()

    data = response.json()["data"]
    countries.extend(data["objects"])

    if not data["meta"]["more"]:
        break

    offset = offset + 100

with open("data/raw/countries_raw.json", "w", encoding="utf-8") as f:
    json.dump(countries, f, indent=2, ensure_ascii=False)

rows = []

for country in countries:
    names = country.get("names") or {}
    codes = country.get("codes") or {}
    capitals = country.get("capitals") or []
    area = country.get("area") or {}
    coords = country.get("coordinates") or {}
    languages = country.get("languages") or []
    currencies = country.get("currencies") or []
    borders = country.get("borders") or []
    classification = country.get("classification") or {}
    memberships = country.get("memberships") or {}

    language_names = []

    for language in languages:
        language_names.append(language["name"])

    currency_codes = []
    currency_names = []

    for currency in currencies:
        currency_codes.append(currency["code"])
        currency_names.append(currency["name"])

    row = {
        "cca2": codes.get("alpha_2"),
        "cca3": codes.get("alpha_3"),
        "name_common": names.get("common"),
        "name_official": names.get("official"),
        "capital": capitals[0]["name"] if capitals else None,
        "region": country.get("region"),
        "subregion": country.get("subregion"),
        "population": country.get("population"),
        "area_km2": area.get("kilometers"),
        "lat": coords.get("lat"),
        "lng": coords.get("lng"),
        "languages": "; ".join(language_names),
        "n_languages": len(languages),
        "currency_codes": "; ".join(currency_codes),
        "currency_names": "; ".join(currency_names),
        "n_currencies": len(currencies),
        "borders": "; ".join(borders),
        "n_borders": len(borders),
        "sovereign": classification.get("sovereign"),
        "un_member": memberships.get("un"),
        "landlocked": country.get("landlocked")
    }

    rows.append(row)

df = pd.DataFrame(rows)

df.to_csv("data/raw/countries_flat.csv", index=False)

print(df.shape)
print(df.isnull().sum())
print(df.head())
df.info()