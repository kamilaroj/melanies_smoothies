import streamlit as st
from snowflake.snowpark.functions import col
import pandas as pd
import requests

st.title(":cup_with_straw: Customize your smoothie :cup_with_straw:")
st.write("Choose the fruits you want in your custom smoothie!")

# Name input
name_of_order = st.text_input("Name on Smoothie:")
st.write("The name on your Smoothie will be:", name_of_order)

# Connect to Snowflake
cnx = st.connection("snowflake")
session = cnx.session()

# Load FRUIT_NAME + SEARCH_ON
my_dataframe = session.table("smoothies.public.fruit_options").select(
    col("FRUIT_NAME"),
    col("SEARCH_ON")
)

# Convert to Pandas for loc[] matching
pd_df = my_dataframe.to_pandas()

# Build list for multiselect
fruit_list = pd_df["FRUIT_NAME"].tolist()

# Ingredient selection
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    fruit_list,
    max_selections=5
)

# If the user picked fruits
if ingredients_list:
    ingredients_string = ""

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + " "

        # Get SEARCH_ON using loc/iloc (as required in the PDF)
        search_on = pd_df.loc[
            pd_df["FRUIT_NAME"] == fruit_chosen, 
            "SEARCH_ON"
        ].iloc[0]

        st.write(f"The search value for {fruit_chosen} is {search_on}.")

        st.subheader(f"{fruit_chosen} Nutrition Information")

        try:
            # API request using SEARCH_ON
            response = requests.get(
                f"https://my.smoothiefroot.com/api/fruit/{search_on}"
            )

            # Show nutrition table
            st.dataframe(
                data=response.json(),
                use_container_width=True
            )

        except Exception:
            st.error(f"Could not load nutrition data for {fruit_chosen}.")

    # Clean SQL-safe ingredient string
    safe_ingredients = ingredients_string.replace("'", "''")

    my_insert_stmt = f"""
        INSERT INTO SMOOTHIES.PUBLIC.ORDERS (INGREDIENTS, NAME_ON_ORDER)
        VALUES ('{safe_ingredients}', '{name_of_order}')
    """

    # Submit button
    time_to_insert = st.button("Submit the order")

    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success(f"Your Smoothie is ordered, {name_of_order}! ✅")
