import streamlit as st
import json
import os
import numpy as np
from docx import Document
import matplotlib.colors as mcolors
from operator import index
import pandas as pd
import string
from dotenv import load_dotenv
import docx
from PIL import Image
import google.generativeai as genai
import base64
import requests
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

load_dotenv()


session_state = st.session_state
if "user_index" not in st.session_state:
    st.session_state["user_index"] = 0


def signup(json_file_path="data.json"):
    st.title("Signup Page")
    with st.form("signup_form"):
        st.write("Fill in the details below to create an account:")
        name = st.text_input("Name:")
        email = st.text_input("Email:")
        age = st.number_input("Age:", min_value=0, max_value=120)
        sex = st.radio("Sex:", ("Male", "Female", "Other"))
        password = st.text_input("Password:", type="password")
        confirm_password = st.text_input("Confirm Password:", type="password")

        if st.form_submit_button("Signup"):
            if password == confirm_password:
                user = create_account(name, email, age, sex, password, json_file_path)
                session_state["logged_in"] = True
                session_state["user_info"] = user
            else:
                st.error("Passwords do not match. Please try again.")


def check_login(username, password, json_file_path="data.json"):
    try:
        with open(json_file_path, "r") as json_file:
            data = json.load(json_file)

        for user in data["users"]:
            if user["email"] == username and user["password"] == password:
                session_state["logged_in"] = True
                session_state["user_info"] = user
                st.success("Login successful!")
                render_dashboard(user)
                return user

        st.error("Invalid credentials. Please try again.")
        return None
    except Exception as e:
        st.error(f"Error checking login: {e}")
        return None


def initialize_database(json_file_path="data.json"):
    try:
        # Check if JSON file exists
        if not os.path.exists(json_file_path):
            # Create an empty JSON structure
            data = {"users": []}
            with open(json_file_path, "w") as json_file:
                json.dump(data, json_file)
    except Exception as e:
        print(f"Error initializing database: {e}")


def create_account(name, email, age, sex, password, json_file_path="data.json"):
    try:
        # Check if the JSON file exists or is empty
        if not os.path.exists(json_file_path) or os.stat(json_file_path).st_size == 0:
            data = {"users": []}
        else:
            with open(json_file_path, "r") as json_file:
                data = json.load(json_file)

        # Append new user data to the JSON structure
        user_info = {
            "name": name,
            "email": email,
            "age": age,
            "sex": sex,
            "password": password,
            "test_cases": None,
            "program": None,
        }
        data["users"].append(user_info)

        # Save the updated data to JSON
        with open(json_file_path, "w") as json_file:
            json.dump(data, json_file, indent=4)

        st.success("Account created successfully! You can now login.")
        return user_info
    except json.JSONDecodeError as e:
        st.error(f"Error decoding JSON: {e}")
        return None
    except Exception as e:
        st.error(f"Error creating account: {e}")
        return None


def login(json_file_path="data.json"):
    st.title("Login Page")
    username = st.text_input("Username:")
    password = st.text_input("Password:", type="password")

    login_button = st.button("Login")

    if login_button:
        user = check_login(username, password, json_file_path)
        if user is not None:
            session_state["logged_in"] = True
            session_state["user_info"] = user
        else:
            st.error("Invalid credentials. Please try again.")


def get_user_info(email, json_file_path="data.json"):
    try:
        with open(json_file_path, "r") as json_file:
            data = json.load(json_file)
            for user in data["users"]:
                if user["email"] == email:
                    return user
        return None
    except Exception as e:
        st.error(f"Error getting user information: {e}")
        return None


def render_dashboard(user_info, json_file_path="data.json"):
    try:
        st.title(f"Welcome to the Dashboard, {user_info['name']}!")
        st.subheader("User Information:")
        st.write(f"Name: {user_info['name']}")
        st.write(f"Sex: {user_info['sex']}")
        st.write(f"Age: {user_info['age']}")
    except Exception as e:
        st.error(f"Error rendering dashboard: {e}")


def get_weather_data(city, start_date, end_date):
    """Fetch weather forecast data for a specified city and date range"""
    try:
        # Get API key from environment variable
        api_key = os.environ.get("OPENWEATHER_API_KEY")
        if not api_key:
            return {"error": "OpenWeather API key not found in environment variables"}
        
        # Calculate number of days in the date range
        start_date_obj = datetime.strptime(start_date, "%Y-%m-%d")
        end_date_obj = datetime.strptime(end_date, "%Y-%m-%d")
        date_delta = end_date_obj - start_date_obj
        days_requested = date_delta.days + 1  # Include both start and end dates
        
        # First get coordinates from city name
        geo_url = f"http://api.openweathermap.org/geo/1.0/direct?q={city}&limit=1&appid={api_key}"
        geo_response = requests.get(geo_url)
        geo_data = geo_response.json()
        
        if not geo_data:
            return {"error": f"Could not find coordinates for {city}"}
            
        lat = geo_data[0]["lat"]
        lon = geo_data[0]["lon"]
        
        # Then get weather forecast data
        # Free API is limited to 5 days forecast
        forecast_url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={api_key}&units=metric"
        response = requests.get(forecast_url)
        
        if response.status_code != 200:
            return {"error": f"Error fetching weather data: {response.status_code}"}
            
        weather_data = response.json()
        
        # Process and organize the weather data
        processed_data = []
        dates_processed = set()
        
        current_date = datetime.now().date()
        api_limit_date = current_date + timedelta(days=5)
        
        # Create a range of dates from start_date to end_date
        requested_dates = [start_date_obj + timedelta(days=i) for i in range(days_requested)]
        
        # Check if requested dates exceed API limitations
        exceeded_api_limit = any(date.date() > api_limit_date for date in requested_dates)
        
        # Process available forecast data
        for item in weather_data["list"]:
            forecast_date = item["dt_txt"].split(" ")[0]
            forecast_date_obj = datetime.strptime(forecast_date, "%Y-%m-%d").date()
            
            # Only include dates within the requested range and not already processed
            if (start_date_obj.date() <= forecast_date_obj <= end_date_obj.date() and
                forecast_date not in dates_processed):
                dates_processed.add(forecast_date)
                processed_data.append({
                    "date": forecast_date,
                    "temp": item["main"]["temp"],
                    "feels_like": item["main"]["feels_like"],
                    "humidity": item["main"]["humidity"],
                    "description": item["weather"][0]["description"],
                    "icon": item["weather"][0]["icon"]
                })
        
        # Sort by date
        processed_data.sort(key=lambda x: x["date"])
        
        return {
            "city": weather_data["city"]["name"],
            "country": weather_data["city"]["country"],
            "forecast": processed_data,
            "requested_dates": [date.strftime("%Y-%m-%d") for date in requested_dates],
            "note": "Weather forecast is only available for up to 5 days ahead" if exceeded_api_limit else "",
            "missing_dates": [date.strftime("%Y-%m-%d") for date in requested_dates if date.date() > api_limit_date]
        }
    except Exception as e:
        return {"error": f"Error processing weather data: {str(e)}"}


def display_weather_forecast(weather_data):
    """Display weather forecast in a visually appealing format"""
    if "error" in weather_data:
        st.error(weather_data["error"])
        return
    
    st.subheader(f"Weather Forecast for {weather_data['city']}, {weather_data['country']}")
    
    if weather_data.get("note"):
        st.info(weather_data["note"])
        if weather_data.get("missing_dates"):
            st.warning(f"Forecast data not available for: {', '.join(weather_data['missing_dates'])}")
    
    # Check if we have any forecast data
    if not weather_data["forecast"]:
        st.warning("No forecast data available for the selected dates.")
        return
    
    # Create columns for daily forecasts
    cols = st.columns(min(len(weather_data["forecast"]), 5))  # Limit to 5 columns max to avoid crowding
    
    # Display forecast for each day
    for i, forecast in enumerate(weather_data["forecast"][:5]):  # Display first 5 days in columns
        with cols[i]:
            date_obj = datetime.strptime(forecast["date"], "%Y-%m-%d")
            st.write(f"**{date_obj.strftime('%a, %b %d')}**")
            
            # Display weather icon
            icon_url = f"http://openweathermap.org/img/wn/{forecast['icon']}@2x.png"
            st.image(icon_url, width=50)
            
            st.write(f"**{forecast['temp']}°C**")
            st.write(f"Feels like: {forecast['feels_like']}°C")
            st.write(f"Humidity: {forecast['humidity']}%")
            st.write(f"{forecast['description'].capitalize()}")
    
    # Display remaining days in a table if more than 5
    if len(weather_data["forecast"]) > 5:
        st.write("**Additional Days:**")
        additional_data = []
        for forecast in weather_data["forecast"][5:]:
            date_obj = datetime.strptime(forecast["date"], "%Y-%m-%d")
            additional_data.append({
                "Date": date_obj.strftime('%a, %b %d'),
                "Temperature": f"{forecast['temp']}°C",
                "Feels Like": f"{forecast['feels_like']}°C",
                "Humidity": f"{forecast['humidity']}%",
                "Condition": forecast['description'].capitalize()
            })
        st.table(additional_data)
    
    # Create temperature chart
    temperatures = [day["temp"] for day in weather_data["forecast"]]
    dates = [datetime.strptime(day["date"], "%Y-%m-%d").strftime("%b %d") for day in weather_data["forecast"]]
    
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(dates, temperatures, marker='o', linestyle='-', color='#0072B2')
    ax.set_xlabel('Date')
    ax.set_ylabel('Temperature (°C)')
    ax.set_title('Temperature Forecast')
    ax.grid(True, linestyle='--', alpha=0.7)
    
    # Add temperature values above points
    for i, temp in enumerate(temperatures):
        ax.annotate(f"{temp}°C", (i, temp), textcoords="offset points", 
                   xytext=(0,10), ha='center')
    
    st.pyplot(fig)


def get_travel_advisory(City, Type, start_date, end_date, Purpose=None, Activities=None, Budget=None, Requirements=None, weather_data=None):
    try:
        # Calculate number of days
        start_date_obj = datetime.strptime(start_date, "%Y-%m-%d")
        end_date_obj = datetime.strptime(end_date, "%Y-%m-%d")
        days = (end_date_obj - start_date_obj).days + 1
        
        # Configure the Gemini API
        genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
        
        # Create the prompt
        prompt = f"You are a Travel Advisor, help me plan my trip to {City} for {days} days from {start_date_obj.strftime('%B %d, %Y')} to {end_date_obj.strftime('%B %d, %Y')}. I want to go {Type}."
        if Purpose:
            prompt += f" My trip is for {Purpose}."
        if Activities:
            prompt += f" I'm interested in {Activities}."
        if Budget:
            prompt += f" My budget is {Budget}."
        if Requirements:
            prompt += f" I have the following requirements: {Requirements}."
        
        # Add weather information to the prompt if available
        if weather_data and "error" not in weather_data and weather_data.get("forecast"):
            prompt += "\n\nWeather forecast for the trip:"
            for day in weather_data["forecast"]:
                date_obj = datetime.strptime(day["date"], "%Y-%m-%d")
                prompt += f"\n- {date_obj.strftime('%b %d')}: {day['temp']}°C, {day['description']}, humidity {day['humidity']}%"
            prompt += "\n\nPlease consider this weather forecast in your recommendations and suggest appropriate activities, clothing, and precautions based on the expected weather conditions."
        
        # Generate content using Gemini
        model = genai.GenerativeModel('gemini-2.0-flash')
        response = model.generate_content(prompt)
        
        return response.text
    except Exception as e:
        print(f"An error occurred: {e}")
        return f"Error generating travel recommendation: {str(e)}"


def main(json_file_path="data.json"):
    st.sidebar.title("Tourism Recommendation System")
    page = st.sidebar.radio(
        "Go to",
        ("Signup/Login", "Dashboard", "Get Travel Recommendation"),
        key="Travel",
    )

    if page == "Signup/Login":
        st.title("Signup/Login Page")
        login_or_signup = st.radio(
            "Select an option", ("Login", "Signup"), key="login_signup"
        )
        if login_or_signup == "Login":
            login(json_file_path)
        else:
            signup(json_file_path)

    elif page == "Dashboard":
        if session_state.get("logged_in"):
            render_dashboard(session_state["user_info"], json_file_path)
        else:
            st.warning("Please login/signup to view the dashboard.")

    elif page == "Get Travel Recommendation":
        if session_state.get("logged_in"):
            st.title("Travel Recommendation System")
            
            with st.form("travel_recommendation_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    City = st.text_input("City", "")
                    Type = st.selectbox("Type of Trip", ["Business", "Leisure"])
                    
                    # Get today's date for the date picker min_value
                    today = datetime.now().date()
                    
                    # Add date selection instead of number of days
                    start_date = st.date_input("Start Date", today, min_value=today)
                    end_date = st.date_input("End Date", today + timedelta(days=3), min_value=today)
                    
                    Purpose = st.text_input("Purpose", "")
                
                with col2:
                    Activities = st.text_input("Activities", "")
                    Budget = st.number_input("Budget", min_value=0, step=1)
                    Requirements = st.text_area("Requirements", "")
                
                submit_button = st.form_submit_button("Generate Travel Recommendation")
            
            if submit_button and City and start_date and end_date:
                # Validate date range
                if start_date > end_date:
                    st.error("Start date cannot be after end date.")
                else:
                    # Convert date objects to string format
                    start_date_str = start_date.strftime("%Y-%m-%d")
                    end_date_str = end_date.strftime("%Y-%m-%d")
                    
                    with st.spinner("Fetching weather data..."):
                        weather_data = get_weather_data(City, start_date_str, end_date_str)
                        
                        if "error" not in weather_data:
                            display_weather_forecast(weather_data)
                        else:
                            st.error(f"Weather data error: {weather_data['error']}")
                    
                    with st.spinner("Generating travel recommendation..."):
                        travel_recommendation = get_travel_advisory(
                            City, Type, start_date_str, end_date_str, Purpose, Activities, Budget, Requirements, weather_data
                        )
                        st.subheader("Travel Recommendation:")
                        st.write(travel_recommendation)
            
        else:
            st.warning("Please login/signup to view the dashboard.")


if __name__ == "__main__":
    initialize_database()
    main()