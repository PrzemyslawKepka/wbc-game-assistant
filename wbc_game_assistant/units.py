import base64
import os
from io import BytesIO

import numpy as np
import pandas as pd
import streamlit as st
from PIL import Image

import mappings


def get_unit_image(
    unit_id: str, unit_to_image_mapping: dict, image_path: str
) -> str:
    """
    Retrieve unit image based on provided ID.

    Args:
        unit_id: Unique identifier for a unit, consisting of four characters.
        unit_to_image_mapping: A dictionary with unit ID stored as key,
                                and image filename as one of values.
        image_path: A path where unit images are stored.

    Returns:
        Full image path for a specified unit.
    """
    image = unit_to_image_mapping[unit_id][0]
    full_image_path = os.path.join(image_path, image)

    return full_image_path


def get_unit_ability(
    unit_id: str,
    unit_to_ability_mapping: dict = mappings.unit_images_and_abilities,
) -> str:
    """
    Retrieve unit ability description based on provided ID.

    Args:
        unit_id: Unique identifier for a unit, consisting of four characters.
        unit_to_image_mapping: A dictionary with unit ID stored as key,
                                and ability description as one of values.

    Returns:
        Ability description for a specified unit.
     """
    ability_description = unit_to_ability_mapping[unit_id][1]

    return ability_description


def convert_res_or_vuln_to_icon(res_or_vuln_list: list,
                                damage_type_mapping: dict = mappings.damage_types) -> str:
    """
    Take a list of damage types, stored as a unit resistance or vulnerability,
        and retrieve a corresponding icon.

    Args:
        res_or_vuln_list: A list containing damage types
        damage_type_mapping: A dictionary with damage type name and corresponding icon

    Returns:
        Icons stored in a string, or empty string if no damage type was provided
    """
    if len(res_or_vuln_list) == 0:
        return ""

    icons_list = []
    for damage_type in res_or_vuln_list:
        icon = damage_type_mapping[damage_type]
        icons_list.append(icon)

    return ",".join(icons_list)


def image_to_base64(img_path: str) -> str:
    """
    Helper function returning base64 object stored as string,
        that can be displayed within the application.

    """
    img = Image.open(img_path)
    with BytesIO() as buffer:
        img.save(buffer, "png")  # or 'jpeg'

        return base64.b64encode(buffer.getvalue()).decode()


def check_attack_types(
    player_unit: pd.Series,
    enemy_df: pd.DataFrame,
    abilities_dict: dict,
    check_context: str,
) -> pd.DataFrame:
    """
    Compare attack types of player unit and enemy units, in order
        to filter out enemy units that can't hit/can't be hit by player unit.

    Args:
        player_unit: Pandas series with selected unit info
        enemy_df: Dataframe with all enemy units
        abilities_dict: A dictionary with abilities list
        check_context: additional information with check context,
                        indication what should be checked

    Returns:
        Reduced dataframe, containing only enemy units that can interact
        with player unit (e.g. if player unit can hit only ground units
        and an enemy unit can hit only air units, then such unit is excluded)

    """
    if check_context not in ("strengths", "weaknesses"):
        raise ValueError(
            "Unknown context, check can be performed only for strenghts or weaknesses"
        )

    # extracting only abilities from image and abilities_dict
    abilities_dict = {key: value[1] for key, value in abilities_dict.items()}

    # checking if player unit is a flier
    if abilities_dict[player_unit.id] is None:
        player_unit_flying = False
    else:
        if "flying" in abilities_dict[player_unit.id].lower():
            player_unit_flying = True
        else:
            player_unit_flying = False

    # bool column if enemy unit is a flier
    enemy_df["flying"] = enemy_df["id"].map(abilities_dict)
    enemy_df["flying"] = np.where(
        enemy_df["flying"].str.lower().str.contains("flying"), True, False
    )

    if check_context == "strengths":
        if player_unit.attackType == "ground":
            # only non-flying units
            enemy_df_filtered = enemy_df.loc[~enemy_df["flying"], :]
        elif player_unit.attackType == "air":
            # only flying units
            enemy_df_filtered = enemy_df.loc[enemy_df["flying"], :]
        elif player_unit.attackType == "both":
            # all units
            enemy_df_filtered = enemy_df.copy()
    elif check_context == "weaknesses":
        if player_unit_flying is False:
            enemy_df_filtered = enemy_df.loc[
                enemy_df["attackType"].isin(["ground", "both"]), :
            ]
        elif player_unit_flying is True:
            enemy_df_filtered = enemy_df.loc[
                enemy_df["attackType"].isin(["air", "both"]), :
            ]
    return enemy_df_filtered


def get_strong_against(
    player_unit: pd.Series, enemy_df: pd.DataFrame, strength_type: str
) -> str:
    """
    Retrieve good match-ups for a player unit, stored as
        string containing image, that will be displayed.

    Args:
        player_unit: Pandas series with selected unit info
        enemy_df: Dataframe with all enemy units
        strength_type: Different type of possible strength provided
                        as a string, can be resistence or enemy vulnerability
    Returns:
        A string that will be used inside HTML code,
        containing unit images.

    """
    if strength_type not in ("resistance", "enemy_vulnerability"):
        raise ValueError(
            "Unknown strength_type, only resistance and enemy_vulnerability are allowed"
        )

    # filter out units that can't be hit (e.g. fliers when unit can hit only ground units)
    enemy_df = check_attack_types(
        player_unit, enemy_df, mappings.unit_images_and_abilities, "strengths"
    )

    if strength_type == "enemy_vulnerability":
        strong_against = enemy_df.loc[
            enemy_df["vulnerability"]
            .astype(str)
            .str.contains(player_unit.damageType),
            "id",
        ].tolist()
    elif strength_type == "resistance":
        strong_against = []
        for i, enemy_unit in enemy_df.iterrows():
            if enemy_unit.damageType in str(player_unit.resilience):
                strong_against.append(enemy_unit.id)

    if len(strong_against) == 0:
        return "&nbsp"

    html_images = []
    for i in strong_against:
        unit_image_path = get_unit_image(
            i, mappings.unit_images_and_abilities, mappings.IMAGE_PATH
        )
        image_b64 = image_to_base64(unit_image_path)
        html_img_string = f'<img src="data:image/jpg;base64,{image_b64}" width="40" height="40">'
        html_images.append(html_img_string)

    return "".join(list(dict.fromkeys(html_images)))


def get_strong_against_deprecated(
    player_unit: pd.Series, enemy_df: pd.DataFrame
) -> str:
    """
    Deprecated of version of get_strong_against() function, without
        a split between unit resistance and enemy vulnerability strength types.

     """
    # filter out units that can't be hit (e.g. fliers when unit can hit only ground units)
    enemy_df = check_attack_types(
        player_unit, enemy_df, mappings.unit_images_and_abilities, "strengths"
    )

    # enemy units vulnerable against player's unit dmg type
    vuln_enemy_units = enemy_df.loc[
        enemy_df["vulnerability"]
        .astype(str)
        .str.contains(player_unit.damageType),
        "id",
    ].tolist()
    # enemy units with dmg type player's unit is resistant against
    resistant_against = []
    for i, enemy_unit in enemy_df.iterrows():
        if enemy_unit.damageType in str(player_unit.resilience):
            resistant_against.append(enemy_unit.id)

    all_strong_against = vuln_enemy_units + resistant_against

    html_images = []
    for i in all_strong_against:
        unit_image_path = get_unit_image(
            i, mappings.unit_images_and_abilities, mappings.IMAGE_PATH
        )
        image_b64 = image_to_base64(unit_image_path)
        html_img_string = f'<img src="data:image/jpg;base64,{image_b64}" width="40" height="40">'
        html_images.append(html_img_string)

    return "".join(list(dict.fromkeys(html_images)))


def get_weak_against(player_unit: pd.Series, enemy_df: pd.DataFrame) -> str:
    """
    Equivalent function of get_strong_against(), but instead returning
        bad match-ups for player unit, based on it's vulnerabilities.
    """
    # filter out units that can't hit our unit (e.g. fliers hitting only other fliers)
    enemy_df = check_attack_types(
        player_unit, enemy_df, mappings.unit_images_and_abilities, "weaknesses"
    )

    weak_against = []
    for i, enemy_unit in enemy_df.iterrows():
        if enemy_unit.damageType in str(player_unit.vulnerability):
            weak_against.append(enemy_unit.id)

    if len(weak_against) == 0:
        return "&nbsp"

    html_images = []
    for i in weak_against:
        unit_image_path = get_unit_image(
            i, mappings.unit_images_and_abilities, mappings.IMAGE_PATH
        )
        image_b64 = image_to_base64(unit_image_path)
        html_img_string = f'<img src="data:image/jpg;base64,{image_b64}" width="40" height="40">'
        html_images.append(html_img_string)

    return "".join(list(dict.fromkeys(html_images)))


def create_unit_description(unit_row: pd.Series) -> st._DeltaGenerator:
    """
    Create an HTML table containing unit description.

    Args:
        unit_row: Pandas series with unit information.

    Returns:
        Markdown text stored as Streamlit internal data type,
            which will be rendered as table by the app.
    """
    unit_description_table = f"""
    <table class="unit_description" style="font-size:16px; border-collapse: collapse; border: none; margin-top: 0em; table-layout: auto;">
    <thead>
    <tr style="border: none;">
        <th colspan="2" style="padding: 0 1em 0 0.5em; border: none;">{unit_row.unit_name}</th>
        <th style="padding: 0 1em 0 0.5em; border: none;">⏳: {unit_row.production['time']}</th>
        <th style="padding: 0 1em 0 0.5em; border: none;">Cost:</th>
    </tr>
    </thead>
    <tbody>
        <tr style="border: none;">
            <td style="padding: 0 1em 0 0.5em; text-align: right; border: none;">
                Tier: <strong>{unit_row.tier}</strong>
            </td>
            <td style="padding: 0 0.5em 0 0.5em; text-align: left; border: none;">
                Damage: <strong>{unit_row.damage}</strong>
            </td>
            <td style="padding: 0 0.5em 0 0.5em; text-align: left; border: none;">
                Range: <strong>{unit_row.range}</strong>
            </td>
            <td style="padding: 0 0.5em 0 0.5em; text-align: left; border: none;">
                💰: <strong>{unit_row.production['gold']}</strong>
            </td>
        </tr>
        <tr style="border: none;">
            <td style="padding: 0 1em 0 0.5em; text-align: right; border: none;">
                Combat: <strong>{unit_row.combat}</strong>
            </td>
            <td style="padding: 0 0.5em 0 0.5em; text-align: left; border: none;">
                Damage Type: <strong>{mappings.damage_types[unit_row.damageType]}</strong>
            </td>
            <td style="padding: 0 0.5em 0 0.5em; text-align: left; border: none;">
                Attack Type: <strong>{unit_row.attackType}</strong>
            </td>
            <td style="padding: 0 0.5em 0 0.5em; text-align: left; border: none;">
                🛡️: <strong>{unit_row.production['metal']}</strong>
            </td>
        </tr>
        <tr style="border: none;">
            <td style="padding: 0 1em 0 0.5em; text-align: right; border: none;">
                HP: <strong>{unit_row.hits}</strong>
            </td>
            <td style="padding: 0 0.5em 0 0.5em; text-align: left; border: none;">
                Armor: <strong>{unit_row.armour}</strong>
            </td>
            <td style="padding: 0 0.5em 0 0.5em; text-align: left; border: none;">
                Resistance: <strong>{convert_res_or_vuln_to_icon(unit_row.resilience)}</strong>
            </td>
            <td style="padding: 0 0.5em 0 0.5em; text-align: left; border: none;">
                🗿: <strong>{unit_row.production['stone']}</strong>
            </td>
        </tr>
        <tr style="border: none;">
            <td style="padding: 0 1em 0 0.5em; text-align: right; border: none;">
                Speed: <strong>{unit_row.speed}</strong>
            </td>
            <td style="padding: 0 0.5em 0 0.5em; text-align: left; border: none;">
                Resistance: <strong>{unit_row.resistance}</strong>
            </td>
            <td style="padding: 0 0.5em 0 0.5em; text-align: left; border: none;">
                Vulnerability: <strong>{convert_res_or_vuln_to_icon(unit_row.vulnerability)}</strong>
            </td>
            <td style="padding: 0 0.5em 0 0.5em; text-align: left; border: none;">
                💎: <strong>{unit_row.production['crystal']}</strong>
            </td>
        </tr>
    </tbody>
    """

    return st.markdown(unit_description_table, unsafe_allow_html=True)


def create_unit_traits(
    unit_row: pd.Series, enemy_df: pd.DataFrame
) -> st._DeltaGenerator:
    """
    Create an HTML table containing unit traits (ability description,
        as well as good and bad match-ups).

    Args:
        unit_row: Pandas series with unit information
        enemy_df: Dataframe with all enemy units data.

    Returns:
        Markdown text stored as Streamlit internal data type,
            which will be rendered as table by the app.

    """
    unit_traits_table = f"""
    <table class="unit_description" style="font-size:16px; border-collapse: separate; border-spacing: 0.3em; border: none; margin-top: 0em; table-layout: auto;">
    <thead>
    <tr style="border: none;">
        <th colspan="2" style="padding: 0 1em 0 0.5em; border: none;">Ability:</th>

    </tr>
    </thead>
    <tbody>
        <tr style="border: none;">
            <td colspan="2" style="padding: 0 1em 0 0.5em; text-align: left; border: none; line-height: 24px;">
            {get_unit_ability(unit_row.id)}
            </td>
        </tr>
        <tr style="border: none;">
            <td style="padding: 0 1em 0 0.5em; text-align: left; border: none;">
                <strong>Strong against</strong> (resistance):
            </td>
            <td style="padding: 0 0.5em 0 0.5em; text-align: left; border: none;">
                {get_strong_against(unit_row, enemy_df, 'resistance')}
            </td>
        </tr>
        <tr style="border: none;">
            <td style="padding: 0 1em 0 0.5em; text-align: left; border: none;">
                Enemy vulnerability:
            </td>
            <td style="padding: 0 0.5em 0 0.5em; text-align: left; border: none;">
                {get_strong_against(unit_row, enemy_df, 'enemy_vulnerability')}
            </td>
        </tr>
        <tr style="border: none;">
            <td style="padding: 0 1em 0 0.5em; text-align: left; border: none;">
                <strong>Weak againsts</strong>:
            </td>
            <td style="padding: 0 0.5em 0 0.5em; text-align: left; border: none;">
                {get_weak_against(unit_row, enemy_df)}
            </td>
        </tr>
    </tbody>
    """
    return st.markdown(unit_traits_table, unsafe_allow_html=True)


def filter_units(
    units_df: pd.DataFrame,
    builders: bool = True,
    t1_fliers: bool = True,
    dragons: bool = True,
    titans: bool = True,
) -> pd.DataFrame:
    """
    Filter units that will be displayed by the app,
        based on the user selection.

    Args:
        units_df: Dataframe with unit data, can be player or enemy
        Remaining args are boolean values, based on user selection
            for units that should be displayed or hidden.

    Returns:
        Filtered unit dataframe, containing only units that the user
            wants to see.

    """

    builders_list = ["AHBX", "ABBX", "AEBX", "AEAX", "AUBX", "ADBX",
                    "AFBX", "ALBX", "AVBX", "AABX", "AOBX","ARBX"]
    t1_fliers_list = ["AAEG", "AAPH", "AALH", "AABA", "AADF", "AAFB", "AAWA"]
    dragons_list = ["AADB", "AADR", "AADG", "AADW", "AADC", "AADU"]
    titans_list = ["ATDX", "ATPX", "ATEX", "ATHX", "ATBX", "ATFX", "ATMX",
                    "ATLX", "ATWX", "ATVX", "ATKX", "ATAX", "ATOX", "ATGX",
                    "ATRX", "ATUX"]

    if builders is not True:
        # exclude builders
        units_df = units_df.loc[~units_df["id"].isin(builders_list), :]
    if t1_fliers is not True:
        # exclude t1 fliers
        units_df = units_df.loc[~units_df["id"].isin(t1_fliers_list), :]
    if dragons is not True:
        # exclude dragons
        units_df = units_df.loc[~units_df["id"].isin(dragons_list), :]
    if titans is not True:
        # exclude titans
        units_df = units_df.loc[~units_df["id"].isin(titans_list), :]

    return units_df
