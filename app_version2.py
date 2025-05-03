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
import streamlit.components.v1 as components
import time

# Load environment variables
load_dotenv()

# Set page configuration with custom theme
st.set_page_config(
    page_title="Travel Advisor Pro",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS with Material Design principles
def local_css():
    st.markdown("""
    <style>
    /* Material Design Colors and Effects */
    :root {
        --primary-color: #1976D2;
        --secondary-color: #FF9800;
        --accent-color: #E91E63;
        --background-color: #F5F5F5;
        --card-color: #FFFFFF;
        --text-color: #212121;
        --text-light: #757575;
    }
    
    /* Main container styling */
    .main {
        background-color: var(--background-color);
        padding: 20px;
    }
    
    /* Card styling with shadow effects */
    .card {
        background-color: var(--card-color);
        border-radius: 8px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        padding: 20px;
        margin-bottom: 20px;
        transition: transform 0.3s, box-shadow 0.3s;
    }
    
    .card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
    }
    
    /* Button styling */
    .stButton > button {
        background-color: var(--primary-color) !important;
        color: white !important;
        border-radius: 4px !important;
        border: none !important;
        padding: 10px 24px !important;
        text-transform: uppercase !important;
        font-weight: 500 !important;
        letter-spacing: 0.5px !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2) !important;
    }
    
    .stButton > button:hover {
        background-color: #1565C0 !important;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3) !important;
        transform: translateY(-2px) !important;
    }
    
    /* Form input styling */
    .stTextInput > div > div > input, 
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > div {
        border-radius: 4px !important;
        border: 1px solid #BDBDBD !important;
        padding: 12px !important;
        transition: border 0.3s ease !important;
    }
    
    .stTextInput > div > div > input:focus, 
    .stTextArea > div > div > textarea:focus,
    .stSelectbox > div > div > div:focus {
        border: 2px solid var(--primary-color) !important;
        box-shadow: 0 0 0 1px rgba(25, 118, 210, 0.2) !important;
    }
    
    /* Radio button styling */
    .stRadio > div {
        background-color: white;
        border-radius: 8px;
        padding: 10px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    /* Header styling */
    h1, h2, h3 {
        color: var(--primary-color) !important;
        font-weight: 700 !important;
    }
    
    .title-container {
        background: linear-gradient(135deg, var(--primary-color), var(--accent-color));
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 30px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .title-container h1 {
        color: white !important;
        margin: 0;
        font-size: 2.5rem;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
    }
    
    .subtitle {
        color: #E1F5FE;
        font-size: 1.2rem;
        font-weight: 300;
    }
    
    /* Sidebar styling */
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, var(--primary-color), #0D47A1);
        color: white;
    }
    
    /* Animation for cards */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .animated-card {
        animation: fadeIn 0.6s ease-out;
    }
    
    /* Weather card styling */
    .weather-card {
        background: linear-gradient(45deg, #42A5F5, #1976D2);
        color: white;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease;
    }
    
    .weather-card:hover {
        transform: scale(1.02);
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
    }
    
    /* Success message styling */
    .success-message {
        background-color: #4CAF50;
        color: white;
        padding: 15px;
        border-radius: 5px;
        animation: fadeIn 0.5s;
    }
    
    /* Error message styling */
    .error-message {
        background-color: #F44336;
        color: white;
        padding: 15px;
        border-radius: 5px;
        animation: shake 0.5s;
    }
    
    @keyframes shake {
        0%, 100% { transform: translateX(0); }
        10%, 30%, 50%, 70%, 90% { transform: translateX(-5px); }
        20%, 40%, 60%, 80% { transform: translateX(5px); }
    }
    
    /* Loading animation */
    .loader {
        border: 5px solid #f3f3f3;
        border-radius: 50%;
        border-top: 5px solid var(--primary-color);
        width: 40px;
        height: 40px;
        margin: 20px auto;
        animation: spin 1s linear infinite;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    /* Dashboard tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
        background-color: white;
        border-radius: 8px;
        padding: 5px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }

    .stTabs [data-baseweb="tab"] {
        background-color: #E3F2FD;
        border-radius: 4px;
        padding: 10px 16px;
        color: var(--primary-color);
        font-weight: 500;
    }

    .stTabs [aria-selected="true"] {
        background-color: var(--primary-color);
        color: white !important;
    }

    /* Progress bar */
    .stProgress > div > div > div > div {
        background-color: var(--secondary-color);
    }
    
    /* Tables */
    .dataframe {
        border-collapse: separate;
        border-spacing: 0;
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    }
    
    .dataframe thead th {
        background-color: var(--primary-color);
        color: white;
        padding: 12px 15px;
        text-align: left;
    }
    
    .dataframe tbody tr:nth-child(even) {
        background-color: #E3F2FD;
    }
    
    .dataframe tbody tr:hover {
        background-color: #BBDEFB;
    }
    
    .dataframe td {
        padding: 10px 15px;
        border-bottom: 1px solid #E0E0E0;
    }
    
    /* Badge styling */
    .badge {
        display: inline-block;
        padding: 5px 10px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 500;
        margin-right: 5px;
    }
    
    .badge-primary {
        background-color: var(--primary-color);
        color: white;
    }
    
    .badge-secondary {
        background-color: var(--secondary-color);
        color: white;
    }
    
    .badge-accent {
        background-color: var(--accent-color);
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

# Initialize session state
session_state = st.session_state
if "user_index" not in st.session_state:
    st.session_state["user_index"] = 0
if "page_animations_done" not in st.session_state:
    st.session_state["page_animations_done"] = False

# Apply custom CSS
local_css()

def display_animated_loader():
    """Display an animated loader with a progress bar"""
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i in range(101):
        # Updating progress bar
        progress_bar.progress(i)
        
        # Update status text
        if i < 30:
            status_text.text("Initializing components...")
        elif i < 60:
            status_text.text("Processing data...")
        elif i < 90:
            status_text.text("Finalizing...")
        else:
            status_text.text("Ready!")
            
        time.sleep(0.01)
    
    # Clean up
    status_text.empty()
    progress_bar.empty()

def signup(json_file_path="data.json"):
    # Title with animation
    st.markdown("""
    <div class="title-container animated-card">
        <h1>Join Travel Advisor Pro</h1>
        <p class="subtitle">Create your account to access personalized travel recommendations</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Card container for signup form
    st.markdown('<div class="card animated-card">', unsafe_allow_html=True)
    
    # Account creation tabs
    signup_tab, oauth_tab = st.tabs(["Create Account", "Sign up with Social"])
    
    with signup_tab:
        with st.form("signup_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input("Full Name")
                email = st.text_input("Email Address")
                age = st.number_input("Age", min_value=0, max_value=120)
            
            with col2:
                sex = st.radio("Gender", ("Male", "Female", "Other"))
                password = st.text_input("Password", type="password")
                confirm_password = st.text_input("Confirm Password", type="password")
            
            # Add some stylish info text
            st.info("Your data is securely stored and will be used to personalize your travel recommendations")
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                submit_btn = st.form_submit_button("Create Account")
        
            if submit_btn:
                if not name or not email or not password:
                    st.markdown("""
                    <div class="error-message">
                        Please fill in all required fields.
                    </div>
                    """, unsafe_allow_html=True)
                elif password != confirm_password:
                    st.markdown("""
                    <div class="error-message">
                        Passwords do not match. Please try again.
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    # Show animation
                    with st.spinner("Creating your account..."):
                        time.sleep(1)  # Simulate processing time
                        user = create_account(name, email, age, sex, password, json_file_path)
                        
                    if user:
                        session_state["logged_in"] = True
                        session_state["user_info"] = user
                        st.markdown("""
                        <div class="success-message">
                            Account created successfully! Welcome aboard.
                        </div>
                        """, unsafe_allow_html=True)
                        time.sleep(1)
                        st.rerun()
    
    with oauth_tab:
        st.write("Coming Soon: Sign up with your favorite social platform")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.button("Google", key="google_signup")
        with col2:
            st.button("Facebook", key="fb_signup")
        with col3:
            st.button("Apple", key="apple_signup")
        
        st.info("Social login features will be available in the next update.")
        
    st.markdown('</div>', unsafe_allow_html=True)


def check_login(username, password, json_file_path="data.json"):
    try:
        with open(json_file_path, "r") as json_file:
            data = json.load(json_file)

        for user in data["users"]:
            if user["email"] == username and user["password"] == password:
                session_state["logged_in"] = True
                session_state["user_info"] = user
                
                # Return user info
                return user

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

        # Check if email already exists
        for user in data["users"]:
            if user["email"] == email:
                st.markdown("""
                <div class="error-message">
                    This email is already registered. Please use a different email or login.
                </div>
                """, unsafe_allow_html=True)
                return None

        # Append new user data to the JSON structure
        user_info = {
            "name": name,
            "email": email,
            "age": age,
            "sex": sex,
            "password": password,
            "test_cases": None,
            "program": None,
            "join_date": datetime.now().strftime("%Y-%m-%d"),
            "travel_history": [],
        }
        data["users"].append(user_info)

        # Save the updated data to JSON
        with open(json_file_path, "w") as json_file:
            json.dump(data, json_file, indent=4)

        return user_info
    except json.JSONDecodeError as e:
        st.error(f"Error decoding JSON: {e}")
        return None
    except Exception as e:
        st.error(f"Error creating account: {e}")
        return None


def login(json_file_path="data.json"):
    # Title with animation
    st.markdown("""
    <div class="title-container animated-card">
        <h1>Welcome Back!</h1>
        <p class="subtitle">Login to continue your journey</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Card container for login form
    st.markdown('<div class="card animated-card">', unsafe_allow_html=True)
    
    # Login tabs
    login_tab, recover_tab = st.tabs(["Login", "Forgot Password"])
    
    with login_tab:
        with st.form("login_form"):
            username = st.text_input("Email Address")
            password = st.text_input("Password", type="password")
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                login_button = st.form_submit_button("Sign In")
        
        if login_button:
            if not username or not password:
                st.markdown("""
                <div class="error-message">
                    Please enter both email and password.
                </div>
                """, unsafe_allow_html=True)
            else:
                # Show animation
                with st.spinner("Verifying your credentials..."):
                    time.sleep(1)  # Simulate processing time
                    user = check_login(username, password, json_file_path)
                
                if user:
                    st.markdown("""
                    <div class="success-message">
                        Login successful! Redirecting to dashboard...
                    </div>
                    """, unsafe_allow_html=True)
                    time.sleep(1)
                    st.rerun()
                else:
                    st.markdown("""
                    <div class="error-message">
                        Invalid credentials. Please check your email and password.
                    </div>
                    """, unsafe_allow_html=True)
    
    with recover_tab:
        with st.form("recovery_form"):
            recovery_email = st.text_input("Enter your registered email")
            submit_recovery = st.form_submit_button("Reset Password")
            
            if submit_recovery:
                st.info("If your email is registered with us, you'll receive instructions to reset your password.")
    
    st.markdown('</div>', unsafe_allow_html=True)


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
        # Title with animation
        st.markdown(f"""
        <div class="title-container animated-card">
            <h1>Welcome, {user_info['name']}!</h1>
            <p class="subtitle">Your personalized travel dashboard</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Create tabs for different dashboard sections
        profile_tab, history_tab, preferences_tab = st.tabs(["Profile", "Travel History", "Preferences"])
        
        with profile_tab:
            # User profile card
            st.markdown('<div class="card animated-card">', unsafe_allow_html=True)
            
            col1, col2 = st.columns([1, 3])
            
            with col1:
                # Display avatar with first letter of name
                first_letter = user_info['name'][0].upper()
                avatar_colors = ["#1976D2", "#E91E63", "#4CAF50", "#FF9800", "#9C27B0"]
                avatar_color = avatar_colors[hash(user_info['name']) % len(avatar_colors)]
                
                st.markdown(f"""
                <div style="width: 100px; height: 100px; background-color: {avatar_color}; border-radius: 50%; 
                display: flex; align-items: center; justify-content: center; margin: 0 auto;">
                    <span style="color: white; font-size: 48px; font-weight: bold;">{first_letter}</span>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown(f"""
                <div style="text-align: center; margin-top: 10px;">
                    <span class="badge badge-primary">Member since {user_info.get('join_date', 'N/A')}</span>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <h2 style="margin-bottom: 15px;">{user_info['name']}</h2>
                <p><strong>Email:</strong> {user_info['email']}</p>
                <p><strong>Age:</strong> {user_info['age']}</p>
                <p><strong>Gender:</strong> {user_info['sex']}</p>
                """, unsafe_allow_html=True)
                
                # Add edit profile button
                if st.button("Edit Profile", key="edit_profile"):
                    st.info("Profile editing will be available in the next update.")
                    
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Stats cards
            st.subheader("Your Travel Stats")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("""
                <div class="card" style="text-align: center;">
                    <h3 style="color: #4CAF50 !important;">0</h3>
                    <p>Trips Planned</p>
                </div>
                """, unsafe_allow_html=True)
                
            with col2:
                st.markdown("""
                <div class="card" style="text-align: center;">
                    <h3 style="color: #FF9800 !important;">0</h3>
                    <p>Countries Visited</p>
                </div>
                """, unsafe_allow_html=True)
                
            with col3:
                st.markdown("""
                <div class="card" style="text-align: center;">
                    <h3 style="color: #E91E63 !important;">0</h3>
                    <p>Recommendations</p>
                </div>
                """, unsafe_allow_html=True)
        
        with history_tab:
            st.markdown('<div class="card animated-card">', unsafe_allow_html=True)
            
            # Check if user has travel history
            if not user_info.get('travel_history') or len(user_info['travel_history']) == 0:
                st.markdown("""
                <div style="text-align: center; padding: 30px;">
                    <img src="https://www.svgrepo.com/show/447992/travel.svg" width="100" />
                    <h3 style="margin-top: 20px;">No Travel History Yet</h3>
                    <p>Your planned trips will appear here. Get started by creating a new travel recommendation!</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                # Display travel history
                for trip in user_info['travel_history']:
                    st.write(f"Trip to {trip['destination']}")
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        with preferences_tab:
            st.markdown('<div class="card animated-card">', unsafe_allow_html=True)
            
            st.subheader("Travel Preferences")
            
            col1, col2 = st.columns(2)
            
            with col1:
                preferred_trip_type = st.selectbox(
                    "Preferred Trip Type",
                    ["Adventure", "Relaxation", "Cultural", "Business", "Family", "Solo"],
                    index=0
                )
                
                preferred_accommodation = st.selectbox(
                    "Preferred Accommodation",
                    ["Hotel", "Resort", "Hostel", "Apartment", "Camping", "B&B"],
                    index=0
                )
            
            with col2:
                preferred_budget = st.select_slider(
                    "Budget Range",
                    options=["Budget", "Economy", "Mid-range", "Luxury", "Ultra-luxury"],
                    value="Mid-range"
                )
                
                preferred_climate = st.multiselect(
                    "Preferred Climate",
                    ["Tropical", "Mediterranean", "Desert", "Continental", "Polar", "Temperate"],
                    default=["Mediterranean", "Temperate"]
                )
            
            # Save button
            if st.button("Save Preferences", key="save_prefs"):
                st.success("Preferences saved successfully!")
                
            st.markdown('</div>', unsafe_allow_html=True)
    
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
    
    # Weather forecast section
    st.markdown(f"""
    <div class="card animated-card">
        <h2>Weather Forecast for {weather_data['city']}, {weather_data['country']}</h2>
    """, unsafe_allow_html=True)
    
    if weather_data.get("note"):
        st.info(weather_data["note"])
        if weather_data.get("missing_dates"):
            st.warning(f"Forecast data not available for: {', '.join(weather_data['missing_dates'])}")
    
    # Check if we have any forecast data
    if not weather_data["forecast"]:
        st.warning("No forecast data available for the selected dates.")
        st.markdown('</div>', unsafe_allow_html=True)
        return
    
    # Create columns for daily forecasts
    cols = st.columns(min(len(weather_data["forecast"]), 5))  # Limit to 5 columns max to avoid crowding
    
    # Weather icon color mapping for different conditions
    # Weather icon color mapping for different conditions
    weather_colors = {
        "clear": "#FFD700",  # Gold for clear/sun
        "cloud": "#A9A9A9",  # Dark gray for clouds
        "rain": "#4682B4",   # Steel blue for rain
        "snow": "#E0FFFF",   # Light cyan for snow
        "mist": "#B0C4DE",   # Light steel blue for mist/fog
        "storm": "#4B0082",  # Indigo for storms
        "default": "#1976D2" # Default blue
    }
    
    # Display forecast for each day
    for i, forecast in enumerate(weather_data["forecast"][:5]):  # Display first 5 days in columns
        with cols[i]:
            date_obj = datetime.strptime(forecast["date"], "%Y-%m-%d")
            
            # Determine weather color based on description
            weather_color = weather_colors["default"]
            description = forecast["description"].lower()
            if "clear" in description:
                weather_color = weather_colors["clear"]
            elif "cloud" in description:
                weather_color = weather_colors["cloud"]
            elif "rain" in description or "drizzle" in description:
                weather_color = weather_colors["rain"]
            elif "snow" in description:
                weather_color = weather_colors["snow"]
            elif "mist" in description or "fog" in description:
                weather_color = weather_colors["mist"]
            elif "storm" in description or "thunder" in description:
                weather_color = weather_colors["storm"]
            
            # Create a styled weather card
            st.markdown(f"""
            <div class="weather-card" style="background: linear-gradient(45deg, {weather_color}, {weather_color}80);">
                <h3 style="margin: 0; text-align: center;">{date_obj.strftime('%a, %b %d')}</h3>
                <div style="display: flex; justify-content: center; margin: 10px 0;">
                    <img src="http://openweathermap.org/img/wn/{forecast['icon']}@2x.png" width="80" style="filter: drop-shadow(2px 2px 4px rgba(0,0,0,0.2));">
                </div>
                <div style="text-align: center;">
                    <h2 style="margin: 0;">{forecast['temp']}°C</h2>
                    <p style="margin: 5px 0;">Feels like: {forecast['feels_like']}°C</p>
                    <p style="margin: 5px 0;">Humidity: {forecast['humidity']}%</p>
                    <p style="margin: 5px 0; font-weight: 500;">{forecast['description'].capitalize()}</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # Display remaining days in a table if more than 5
    if len(weather_data["forecast"]) > 5:
        st.markdown("<h3>Additional Days:</h3>", unsafe_allow_html=True)
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
    
    # Create temperature chart with Material Design styling
    temperatures = [day["temp"] for day in weather_data["forecast"]]
    dates = [datetime.strptime(day["date"], "%Y-%m-%d").strftime("%b %d") for day in weather_data["forecast"]]
    
    fig, ax = plt.subplots(figsize=(10, 4))
    
    # Create gradient effect for the line
    gradient = plt.cm.Blues(np.linspace(0.4, 1, len(temperatures)))
    
    # Create bars with custom styling
    bars = ax.bar(dates, temperatures, color=gradient, alpha=0.7, width=0.6)
    
    # Add connecting line
    ax.plot(dates, temperatures, marker='o', linestyle='-', color='#1976D2', linewidth=2.5, 
            markersize=8, markerfacecolor='white', markeredgecolor='#1976D2', markeredgewidth=2)
    
    # Style the chart
    ax.set_facecolor('#F5F5F5')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_color('#CCCCCC')
    ax.spines['left'].set_color('#CCCCCC')
    ax.tick_params(colors='#666666')
    ax.set_xlabel('Date', color='#666666', fontsize=12)
    ax.set_ylabel('Temperature (°C)', color='#666666', fontsize=12)
    ax.set_title('Temperature Forecast', color='#1976D2', fontsize=14, fontweight='bold')
    ax.grid(True, linestyle='--', alpha=0.7, color='#DDDDDD')
    
    # Add temperature values above points
    for i, temp in enumerate(temperatures):
        ax.annotate(f"{temp}°C", (i, temp), textcoords="offset points", 
                   xytext=(0,10), ha='center', fontsize=10, fontweight='bold', color='#1976D2')
    
    # Add some padding to the y-axis
    plt.ylim(min(temperatures) - 5, max(temperatures) + 5)
    
    # Show the plot
    st.pyplot(fig)
    
    st.markdown('</div>', unsafe_allow_html=True)


def get_travel_advisory(City, Type, start_date, end_date, Purpose=None, Activities=None, Budget=None, Requirements=None, weather_data=None):
    try:
        # Calculate number of days
        start_date_obj = datetime.strptime(start_date, "%Y-%m-%d")
        end_date_obj = datetime.strptime(end_date, "%Y-%m-%d")
        days = (end_date_obj - start_date_obj).days + 1
        
        # Configure the Gemini API
        genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
        
        # Create the prompt
        prompt = f"""You are a Travel Advisor, help me plan my trip to {City} for {days} days from {start_date_obj.strftime('%B %d, %Y')} to {end_date_obj.strftime('%B %d, %Y')}. I want to go {Type}.
        
Please structure your response using markdown with the following sections:
- **Overview**: Brief introduction to {City} as a destination
- **Itinerary Highlights**: Day-by-day summary of recommended activities
- **Accommodation Options**: Where to stay based on my preferences
- **Transportation Tips**: How to get around during the trip
- **Must-Visit Attractions**: Top places to see
- **Local Cuisine**: Food and dining recommendations
- **Travel Tips**: Important advice for visiting {City}
- **Budget Breakdown**: Estimated costs for this trip
        """
        
        if Purpose:
            prompt += f"\n\nMy trip is for {Purpose}."
        if Activities:
            prompt += f"\n\nI'm interested in {Activities}."
        if Budget:
            prompt += f"\n\nMy budget is {Budget}."
        if Requirements:
            prompt += f"\n\nI have the following requirements: {Requirements}."
        
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
    # Sidebar with gradient background and animation
    with st.sidebar:
        st.markdown("""
        <div style="text-align: center; animation: fadeIn 1s;">
            <h1 style="color: white; margin-bottom: 20px;">✈️ Travel Advisor Pro</h1>
        </div>
        """, unsafe_allow_html=True)
        
        # Add separator
        st.markdown("<hr style='margin: 15px 0; border-color: rgba(255,255,255,0.2);'>", unsafe_allow_html=True)
        
        # Navigation Menu
        st.markdown("<p style='color: white; font-weight: bold; margin-bottom: 10px;'>NAVIGATION</p>", unsafe_allow_html=True)
        
        page = st.radio(
            "",
            ["📋 Signup/Login", "📊 Dashboard", "🔍 Travel Planner"],
            key="Travel",
            label_visibility="collapsed"
        )
        
        # Add separator
        st.markdown("<hr style='margin: 15px 0; border-color: rgba(255,255,255,0.2);'>", unsafe_allow_html=True)
        
        # Display user info if logged in
        if session_state.get("logged_in"):
            user_info = session_state["user_info"]
            first_letter = user_info['name'][0].upper()
            
            st.markdown(f"""
            <div style="background-color: rgba(255,255,255,0.1); border-radius: 10px; padding: 15px; text-align: center; margin-bottom: 20px;">
                <div style="width: 50px; height: 50px; background-color: white; color: #1976D2; border-radius: 50%; 
                display: flex; align-items: center; justify-content: center; margin: 0 auto; font-weight: bold; font-size: 24px;">
                    {first_letter}
                </div>
                <p style="color: white; margin-top: 10px; font-weight: bold;">{user_info['name']}</p>
                <p style="color: rgba(255,255,255,0.7); font-size: 12px; margin: 0;">{user_info['email']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Logout button
            if st.button("Logout", key="logout_btn"):
                session_state["logged_in"] = False
                session_state["user_info"] = None
                st.rerun()
    
    # Show loading animation on first load
    if not session_state["page_animations_done"]:
        display_animated_loader()
        session_state["page_animations_done"] = True

    # Main content area
    if page == "📋 Signup/Login":
        login_or_signup = st.radio(
            "Select an option", 
            ("Login", "Signup"), 
            key="login_signup",
            horizontal=True,
            label_visibility="collapsed"
        )
        
        if login_or_signup == "Login":
            login(json_file_path)
        else:
            signup(json_file_path)

    elif page == "📊 Dashboard":
        if session_state.get("logged_in"):
            render_dashboard(session_state["user_info"], json_file_path)
        else:
            st.markdown("""
            <div class="card" style="text-align: center; padding: 40px;">
                <div style="font-size: 72px; margin-bottom: 20px;">🔒</div>
                <h2>Access Restricted</h2>
                <p>Please login or signup to view your personalized dashboard.</p>
                <p style="margin-top: 20px;">Already have an account? Use the sidebar to navigate to the login page.</p>
            </div>
            """, unsafe_allow_html=True)

    elif page == "🔍 Travel Planner":
        if session_state.get("logged_in"):
            # Title with animation
            st.markdown("""
            <div class="title-container animated-card">
                <h1>Plan Your Dream Trip</h1>
                <p class="subtitle">Get personalized travel recommendations based on your preferences</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Create a card for the form
            st.markdown('<div class="card animated-card">', unsafe_allow_html=True)
            
            with st.form("travel_recommendation_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    City = st.text_input("Destination City", placeholder="e.g. Paris, Tokyo, New York")
                    
                    Type = st.selectbox(
                        "Type of Trip",
                        ["Leisure", "Business", "Adventure", "Cultural", "Romantic", "Family", "Solo"],
                        index=0
                    )
                    
                    # Get today's date for the date picker min_value
                    today = datetime.now().date()
                    
                    # Add date selection instead of number of days
                    start_date = st.date_input("Start Date", today, min_value=today)
                    end_date = st.date_input("End Date", today + timedelta(days=3), min_value=today)
                    
                    Purpose = st.text_input("Purpose of Trip", placeholder="e.g. Honeymoon, Business Conference")
                
                with col2:
                    Activities = st.text_input("Interested Activities", placeholder="e.g. Hiking, Museums, Shopping")
                    
                    Budget = st.select_slider(
                        "Budget Range",
                        options=["Budget", "Economy", "Mid-range", "Luxury", "Ultra-luxury"],
                        value="Mid-range"
                    )
                    
                    Requirements = st.text_area("Special Requirements", placeholder="e.g. Wheelchair accessibility, Pet-friendly hotels")
                
                # Submit button
                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    submit_button = st.form_submit_button("Generate Travel Plan")
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            if submit_button and City and start_date and end_date:
                # Validate date range
                if start_date > end_date:
                    st.markdown("""
                    <div class="error-message">
                        Start date cannot be after end date.
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    # Convert date objects to string format
                    start_date_str = start_date.strftime("%Y-%m-%d")
                    end_date_str = end_date.strftime("%Y-%m-%d")
                    
                    # Create progress tracker
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    # Update progress
                    progress_bar.progress(25)
                    status_text.text("Fetching weather data...")
                    
                    weather_data = get_weather_data(City, start_date_str, end_date_str)
                    
                    # Update progress
                    progress_bar.progress(50)
                    status_text.text("Analyzing destination information...")
                    
                    # Display weather if available
                    if "error" not in weather_data:
                        display_weather_forecast(weather_data)
                    
                    # Update progress
                    progress_bar.progress(75)
                    status_text.text("Creating personalized travel plan...")
                    
                    # Generate travel recommendation
                    travel_recommendation = get_travel_advisory(
                        City, Type, start_date_str, end_date_str, Purpose, Activities, Budget, Requirements, weather_data
                    )
                    
                    # Complete progress
                    progress_bar.progress(100)
                    status_text.empty()
                    
                    # Display travel recommendation
                    st.markdown(f"""
                    <div class="card animated-card">
                        <h2>Your Personalized Travel Plan for {City}</h2>
                        <div class="badge-container" style="margin-bottom: 15px;">
                            <span class="badge badge-primary">{Type}</span>
                            <span class="badge badge-secondary">{Budget}</span>
                            <span class="badge badge-accent">{(end_date - start_date).days + 1} Days</span>
                        </div>
                        <div style="margin-top: 20px;">
                            {travel_recommendation}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Add action buttons
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        if st.button("Save Plan"):
                            st.success("Plan saved to your account!")
                    with col2:
                        if st.button("Export PDF"):
                            st.info("PDF export feature coming soon!")
                    with col3:
                        if st.button("Share Plan"):
                            st.info("Sharing feature coming soon!")
        else:
            st.markdown("""
            <div class="card" style="text-align: center; padding: 40px;">
                <div style="font-size: 72px; margin-bottom: 20px;">🔒</div>
                <h2>Access Restricted</h2>
                <p>Please login or signup to create travel plans.</p>
                <p style="margin-top: 20px;">Already have an account? Use the sidebar to navigate to the login page.</p>
            </div>
            """, unsafe_allow_html=True)


if __name__ == "__main__":
    initialize_database()
    main()