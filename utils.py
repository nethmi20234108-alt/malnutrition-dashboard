import pandas as pd

def load_data():
    df = pd.read_csv(
        "jointmalnutritionestimatesbycountrymarch2020_1.csv",
        encoding="cp1252",
        header=16,
        skiprows=[17]
    )
    # Rename for convenience
    df = df.rename(columns={
        "ISO Code": "iso_code",
        "Country": "country",
        "Year*": "year",
        "United Nations Region": "un_region",
        "United Nations Sub-Region": "un_subregion",
        "World Bank Income Classification": "income_group",
        "Severe Wasting": "severe_wasting",
        "Wasting": "wasting",
        "Overweight": "overweight",
        "Stunting": "stunting",
        "Underweight": "underweight",
        "U5 Population ('000s)": "u5_population"
    })
    # Keep relevant columns
    cols = ["iso_code","country","year","un_region","un_subregion",
            "income_group","severe_wasting","wasting","overweight",
            "stunting","underweight","u5_population"]
    df = df[cols].copy()
    # Drop rows where all indicators are null
    df = df.dropna(subset=["stunting","wasting","underweight","overweight"], how="all")
    df["year"] = pd.to_numeric(df["year"], errors="coerce")
    return df