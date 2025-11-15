import streamlit as st
from snowflake.snowpark.functions import col
import requests

st.title(":cup_with_straw: Customize your smoothie :cup_with_straw:")
st.write("Choose the fruits you want in your custom smoothie!")

name_of_order = st.text_input('Name on Smoothie:')
st.write('The name on your Smoothie will be:', name_of_order)

cnx = st.connection("snowflake")
session = cnx.session()

my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('SEARCH ON'))
st.dataframe (data = my_dataframe, use_container_width=true)
st.stop()


ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    my_dataframe,
    max_selections=5
)

if ingredients_list:
    ingredients_string = ""

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + " "

        st.subheader(f"{fruit_chosen} Nutrition Information")

        try:
            smoothiefroot_response = requests.get(
                f"https://my.smoothiefroot.com/api/fruit/{fruit_chosen}"
            )

            sf_df = st.dataframe(
                data=smoothiefroot_response.json(),
                use_container_width=True
            )

        except Exception:
            st.error(f"Could not load data for {fruit_chosen}")

    safe_ingredients = ingredients_string.replace("'", "''")

    my_insert_stmt = f"""
        INSERT INTO SMOOTHIES.PUBLIC.ORDERS (INGREDIENTS, NAME_ON_ORDER)
        VALUES ('{safe_ingredients}', '{name_of_order}')
    """

    time_to_insert = st.button("Submit the order")

    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success(f"Your Smoothie is ordered, {name_of_order}! ✅")
