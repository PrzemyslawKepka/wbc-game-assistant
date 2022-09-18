import streamlit as st

from wbc_game_assistant import load_data, mappings, units

st.set_page_config(layout="wide", page_icon="⚒️", page_title= 'WBC Game Assistant',
                    initial_sidebar_state="collapsed")

st.title("WBC game assistant")

with st.sidebar:
    st.image("wbc_game_assistant/images/wbc_icon.png")


units_df = load_data.get_unit_data()
races = load_data.get_races(units_df)

with st.expander("Browse all units"):
    race = st.selectbox("Race", options=['All'] + races)
    if race == 'All':
        filtered_units_df = st.dataframe(units_df.sort_values(['race', 'tier']))
    else:
        filtered_units_df = st.dataframe(
            units_df[units_df["race"] == race].sort_values("tier")
        )

player_col, enemy_col = st.columns(2)

with player_col:
    player_race = st.selectbox("Player Race", options=races, key="player", index=0)
    player_units_df = units_df[units_df["race"] == player_race].sort_values("tier")

with enemy_col:
    enemy_races = st.multiselect("Enemy Race", options=races, key="enemy")
    enemy_units_df = units_df[units_df["race"].isin(enemy_races)].sort_values(
        ["race", "tier"]
    )

    if len(enemy_races) > 5:
        st.error("It's not TPC, max number of enemies is 5!")

with st.expander("Advanced filters:"):
    player_filters_side, enemy_filters_side = st.columns(2)

    with player_filters_side:
        st.markdown("Include units:")
    with enemy_filters_side:
        st.markdown("Include enemy units:")

    p1, p2, p3, p4, e1, e2, e3, e4 = st.columns(8)

    with p1:
        p_builders = st.checkbox("Builders", value=True, key="player")
    with p2:
        p_titans = st.checkbox("Titans", value=True, key="player")
    with p3:
        st.empty()
    with p4:
        st.empty()
    with e1:
        e_builders = st.checkbox("Builders", value=True, key="enemy")
    with e2:
        e_t1_fliers = st.checkbox("T1 fliers", value=True, key="enemy")
    with e3:
        e_dragons = st.checkbox("Dragons", value=True, key="enemy")
    with e4:
        e_titans = st.checkbox("Titans", value=True, key="enemy")

player_units_df = units.filter_units(player_units_df, p_builders, titans=p_titans)
enemy_units_df = units.filter_units(
    enemy_units_df, e_builders, e_t1_fliers, e_dragons, e_titans
)

for i, unit in player_units_df.iterrows():
    with st.container():
        unit_image_col, unit_descr_col, unit_traits_col = st.columns([1, 3, 4])
        with unit_image_col:
            unit_image = units.get_unit_image(
                unit.id, mappings.unit_images_and_abilities, mappings.IMAGE_PATH
            )
            st.image(unit_image)
        with unit_descr_col:
            units.create_unit_description(unit)
        with unit_traits_col:
            units.create_unit_traits(unit, enemy_units_df)
        st.markdown('<hr style="margin: 5px" />', unsafe_allow_html=True)

st.write('Damage to icon mapping:')
st.write(mappings.damage_types)
