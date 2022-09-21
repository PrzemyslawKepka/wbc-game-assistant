import pandas as pd
import requests
import streamlit as st


@st.cache(allow_output_mutation=True)
def get_unit_data() -> pd.DataFrame:
    """
    Load source data containing data on all units.

    Args:
        None

    Returns:
        Unit data stored as a dataframe.
    """
    units_file = "https://raw.githubusercontent.com/xandros15/wbc-sg-races/gh-pages/units.json"
    races_file = "https://raw.githubusercontent.com/xandros15/wbc-sg-races/gh-pages/races.json"

    response_races = requests.get(races_file).json()

    races, unit_tier, unit_id = ([] for i in range(3))
    for race in response_races:
        for unit in race["units"]:
            races.append(race["name"])
            unit_tier.append(unit["tier"])
            unit_id.append(unit["id"])

    df_races_with_unit_ids = pd.DataFrame(
        zip(races, unit_tier, unit_id), columns=["race", "tier", "unit_id"]
    )

    df_units = pd.read_json(units_file)
    df_units = df_units.merge(
        df_races_with_unit_ids, left_on="id", right_on="unit_id", how="left"
    ).drop(columns="unit_id")

    df_units.rename(columns={"name": "unit_name"}, inplace=True)
    # filter out unit with no race assigned - guardian skull
    df_units = df_units[~df_units["race"].isna()]
    df_units["tier"] = df_units["tier"].astype("int")

    return df_units


@st.cache(allow_output_mutation=True)
def get_races(source_df: pd.DataFrame) -> list:
    """
    Get all races listfrom previously read sourca data.

    Args:
        source_df: Pandas dataframe, storing information on units, including their race.

    Returns:
        List of all unique races, used further in the app.
    """
    races = source_df["race"].unique().tolist()

    return races
