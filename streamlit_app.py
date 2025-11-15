# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
import requests

# -------------------------------------------------------
# 1️⃣ Smoothiefroot API – MUSS OBEN STEHEN
# -------------------------------------------------------
smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/watermelon")
sf_df = st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)

# -------------------------------------------------------
# 2️⃣ App UI (Titel, Beschreibung)
# -------------------------------------------------------
st.title(":cup_with_straw: Customize your smoothie :cup_with_straw:")
st.write("""Choose the fruits you want in your custom smoothie!""")

# -------------------------------------------------------
# 3️⃣ Name für Bestellung
# -------------------------------------------------------
name_of_order = st.text_input('Name on Smoothie:')
st.write('The name on your Smoothie will be:', name_of_order)

# -------------------------------------------------------
# 4️⃣ Snowflake-Verbindung und Zutatenliste
# -------------------------------------------------------
cnx = st.connection("snowflake")
session = cnx.session()

my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))

# Max 5 ingredients
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    my_dataframe,
    max_selections=5
)

# -------------------------------------------------------
# 5️⃣ Bestellung speichern (INSERT)
# -------------------------------------------------------
if ingredients_list:
    # Zutatenliste als Text
    ingredients_string = ", ".join(ingredients_list)

    # SQL-sicher machen
    safe_ingredients = ingredients_string.replace("'", "''")

    # SQL-Insert
    my_insert_stmt = f"""
        INSERT INTO SMOOTHIES.PUBLIC.ORDERS (INGREDIENTS, NAME_ON_ORDER)
        VALUES ('{safe_ingredients}', '{name_of_order}')
    """

    # Button
    time_to_insert = st.button("Submit the order")

    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success(f"Your Smoothie is ordered, {name_of_order}! ✅")
