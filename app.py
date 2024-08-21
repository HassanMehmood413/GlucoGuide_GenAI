import streamlit as st
import anthropic
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

def get_meal_plan(api_key, fasting_sugar, pre_meal_sugar, post_meal_sugar, dietary_preferences, age, activity_level):
    client = anthropic.Anthropic(api_key=api_key)
    
    user_input = (
        f"My fasting sugar level is {fasting_sugar}, "
        f"my pre-meal sugar level is {pre_meal_sugar}, "
        f"and my post-meal sugar level is {post_meal_sugar}. "
        f"My dietary preferences are {dietary_preferences}. "
        f"I am {age} years old and my activity level is {activity_level}. "
        "Please provide a detailed personalized meal plan."
    )

    try:
        response = client.messages.create(
            model="claude-3-5-sonnet-20240620",
            max_tokens=2000,
            temperature=0,
            messages=[
                {
                    "role": "user",
                    "content": user_input
                }
            ]
        )

        # Extract and concatenate the content from the response
        if hasattr(response, 'content') and len(response.content) > 0:
            text_blocks = response.content
            meal_plan = ''.join([block.text for block in text_blocks])
            return meal_plan.strip()
        else:
            return "Unexpected response structure. Please check the API documentation."

    except anthropic.BadRequestError as e:
        return f"Error: {e.error['message']}"
    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"

# Streamlit UI
st.title("GlucoGuide")
st.write(
    "Welcome to GlucoGuide! This app helps diabetic patients get personalized meal plans based on their sugar levels, dietary preferences, age, and activity level."
)

# Sidebar for user inputs
with st.sidebar:
    st.header("Enter Your Details")
    api_key = st.secrets['claude_api_key']
    fasting_sugar = st.number_input("Fasting Sugar Level (mg/dL):", min_value=0)
    pre_meal_sugar = st.number_input("Pre-Meal Sugar Level (mg/dL):", min_value=0)
    post_meal_sugar = st.number_input("Post-Meal Sugar Level (mg/dL):", min_value=0)
    dietary_preferences = st.text_input("Dietary Preferences (e.g., vegetarian, low-carb):")
    age = st.number_input("Age:", min_value=0)
    activity_level = st.selectbox("Activity Level:", ["Sedentary", "Light", "Moderate", "Active"])
    language = st.selectbox("Select Language:", ["English", "Spanish", "French", "German"])  # Example languages

    if st.button("Get Meal Plan"):
        if api_key:
            with st.spinner("Fetching your personalized meal plan..."):
                meal_plan = get_meal_plan(api_key, fasting_sugar, pre_meal_sugar, post_meal_sugar, dietary_preferences, age, activity_level)
                st.session_state['meal_plan'] = meal_plan  # Store the meal plan in session state

                # Display health-related graphs
                st.write("**Health Metrics Graphs:**")

                # Bar Chart
                st.write("**Bar Chart of Sugar Levels:**")
                labels = ['Fasting Sugar', 'Pre-Meal Sugar', 'Post-Meal Sugar']
                values = [fasting_sugar, pre_meal_sugar, post_meal_sugar]
                fig, ax = plt.subplots(figsize=(8, 6))
                bars = ax.bar(labels, values, color=['#1f77b4', '#ff7f0e', '#2ca02c'], edgecolor='black')
                ax.set_ylabel('Sugar Levels (mg/dL)')
                ax.set_title('Comparison of Sugar Levels')
                for bar in bars:
                    yval = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width()/2, yval + 1, round(yval, 1), ha='center', va='bottom', fontsize=12, fontweight='bold')
                st.pyplot(fig)


                # Pie Chart
                st.write("**Pie Chart of Dietary Preferences Distribution:**")
                dietary_preference_counts = {
                    'Vegetarian': 50,  # Example data
                    'Low-Carb': 30,
                    'Vegan': 20
                }
                labels = dietary_preference_counts.keys()
                values = dietary_preference_counts.values()
                fig, ax = plt.subplots(figsize=(8, 8))
                ax.pie(values, labels=labels, autopct='%1.1f%%', colors=['#ff9999','#66b3ff','#99ff99'])
                ax.set_title('Dietary Preferences Distribution')
                st.pyplot(fig)

                # Histogram
                st.write("**Histogram of Sugar Levels Distribution:**")
                sugar_levels = [fasting_sugar, pre_meal_sugar, post_meal_sugar]  # Example data
                fig, ax = plt.subplots(figsize=(8, 6))
                ax.hist(sugar_levels, bins=5, color='#1f77b4', edgecolor='black')
                ax.set_xlabel('Sugar Levels (mg/dL)')
                ax.set_ylabel('Frequency')
                ax.set_title('Distribution of Sugar Levels')
                st.pyplot(fig)

                # Radar Chart
                st.write("**Radar Chart of Nutritional Breakdown:**")
                categories = ['Carbs', 'Proteins', 'Fats', 'Vitamins', 'Minerals']
                values = [50, 30, 20, 10, 5]  # Example data
                num_vars = len(categories)
                angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
                values += values[:1]
                angles += angles[:1]
                fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
                ax.fill(angles, values, color='blue', alpha=0.25)
                ax.plot(angles, values, color='blue', linewidth=2)
                ax.set_yticklabels([])
                ax.set_xticks(angles[:-1])
                ax.set_xticklabels(categories)
                ax.set_title('Nutritional Breakdown')
                st.pyplot(fig)

        else:
            st.warning("Please enter your API key.")

# Display meal plan on the main page
if 'meal_plan' in st.session_state:
    st.write("**Personalized Meal Plan:**")
    st.write(st.session_state['meal_plan'])
