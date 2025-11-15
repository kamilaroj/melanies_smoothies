# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col

# Write directly to the app
st.title(":cup_with_straw: Customize your smoothie :cup_with_straw:")
st.write("""Choose the fruits you want in your custom smoothie!""")

name_of_order = st.text_input('Name on Smoothie:')
st.write('The name on your Smoothie will be:', name_of_order)

cnx = st. connection("snowflake")
session = cnx. session ()

my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))

# Max 5 ingredients
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    my_dataframe,
    max_selections=5
)


# Nur wenn etwas gewählt wurde:
if ingredients_list:
    # Liste in String umwandeln ("Apple, Banana, ...")
    ingredients_string = ", ".join(ingredients_list)

    # SQL-String sicher machen (Hochkommas escapen)
    safe_ingredients = ingredients_string.replace("'", "''")

    
    # Richtiger SQL-Insert mit beiden Spalten (INGREDIENTS, NAME_ON_ORDER)
    my_insert_stmt = f"""
    INSERT INTO SMOOTHIES.PUBLIC.ORDERS (INGREDIENTS, NAME_ON_ORDER)
    VALUES ('{safe_ingredients}', '{name_of_order}')
    """

    # Button zum Absenden
    time_to_insert = st.button("Submit the order")

    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success(f"Your Smoothie is ordered, {name_of_order}! ✅")

import requests
smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/watermelon")
st.text(smoothiefroot_response)
