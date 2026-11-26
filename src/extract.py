import json
import os

import pandas as pd
import requests

BASE_URL = "https://api.restcountries.com/countries/v5"
RAW_DIR = os.path.join("data", "raw")
PAGE_SIZE = 100


def load_api_key():
    with open("api_key.txt", "r", encoding="utf-8") as f:
        return f.read().strip()


def fetch_all(api_key):
    headers = {
        "Authorization": f"Bearer {api_key}",
        "User-Agent": "psut-data-engineering-project",
    }
    all_countries = []
    offset = 0

    while True:
        params = {"limit": PAGE_SIZE, "offset": offset}
        response = requests.get(BASE_URL, headers=headers, params=params, timeout=30)
        body = response.json()

        if response.status_code != 200 or body.get("errors"):
            print("API error:", response.status_code, body.get("errors"))
            raise SystemExit(1)

        page = body["data"]["objects"]
        meta = body["data"]["meta"]
        all_countries.extend(page)
        print(f"Fetched {len(page)} countries (offset {offset}), total so far: {len(all_countries)}")

        if not meta.get("more"):
            break
        offset += PAGE_SIZE

    return all_countries


def get_name(item):
    if item is None:
        return None
    if isinstance(item, str):
        return item
    if isinstance(item, dict):
        for key in ("name", "common", "english", "official"):
            if isinstance(item.get(key), str):
                return item[key]
            if isinstance(item.get(key), dict):
                return get_name(item[key])
    return str(item)


def get_number(value):
    if isinstance(value, dict):
        for key in ("value", "total", "kilometers", "count"):
            if key in value:
                return value[key]
        return None
    return value


def flatten(country):
    names = country.get("names") or {}
    codes = country.get("codes") or {}
    capitals = country.get("capitals") or []
    area = country.get("area") or {}
    coords = country.get("coordinates") or {}
    languages = country.get("languages") or []
    currencies = country.get("currencies") or {}
    borders = country.get("borders") or []
    classification = country.get("classification") or {}
    memberships = country.get("memberships") or {}

    if isinstance(languages, list):
        language_names = [get_name(l) for l in languages]
    else:
        language_names = [get_name(v) for v in languages.values()]

    if isinstance(currencies, dict):
        currency_codes = list(currencies.keys())
        currency_names = [get_name(v) for v in currencies.values()]
    else:
        currency_codes = [c.get("code") for c in currencies if isinstance(c, dict)]
        currency_names = [get_name(c) for c in currencies]

    un_member = memberships.get("un")
    if un_member is None:
        un_member = classification.get("un_member")

    return {
        "cca2": codes.get("alpha_2"),
        "cca3": codes.get("alpha_3"),
        "name_common": names.get("common"),
        "name_official": names.get("official"),
        "capital": get_name(capitals[0]) if capitals else None,
        "region": get_name(country.get("region")),
        "subregion": get_name(country.get("subregion")),
        "population": get_number(country.get("population")),
        "area_km2": area.get("kilometers") if isinstance(area, dict) else area,
        "lat": coords.get("lat"),
        "lng": coords.get("lng"),
        "languages": "; ".join(n for n in language_names if n) or None,
        "n_languages": len(language_names),
        "currency_codes": "; ".join(c for c in currency_codes if c) or None,
        "currency_names": "; ".join(n for n in currency_names if n) or None,
        "n_currencies": len(currency_codes),
        "borders": "; ".join(borders) if borders else None,
        "n_borders": len(borders),
        "sovereign": classification.get("sovereign"),
        "un_member": un_member,
        "landlocked": country.get("landlocked"),
    }


def main():
    os.makedirs(RAW_DIR, exist_ok=True)

    api_key = load_api_key()
    raw = fetch_all(api_key)

    raw_path = os.path.join(RAW_DIR, "countries_raw.json")
    with open(raw_path, "w", encoding="utf-8") as f:
        json.dump(raw, f, ensure_ascii=False, indent=2)
    print(f"Saved raw JSON -> {raw_path}")

    df = pd.DataFrame([flatten(c) for c in raw])

    flat_path = os.path.join(RAW_DIR, "countries_flat.csv")
    df.to_csv(flat_path, index=False, encoding="utf-8")
    print(f"Saved flattened CSV -> {flat_path}")
    print(f"Shape: {df.shape[0]} rows x {df.shape[1]} columns")

    print("\nMissing values per column:")
    print(df.isna().sum())


if __name__ == "__main__":
    main()