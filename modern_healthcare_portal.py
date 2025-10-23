import streamlit as st
import pandas as pd
import re
import plotly.express as px
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import smtplib
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
from langchain_google_genai import ChatGoogleGenerativeAI

# Load environment variables
load_dotenv()

# Page Configuration - Modern Healthcare Portal
st.set_page_config(
    page_title="MediCare Plus - Modern Healthcare",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize session state
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'home'
if 'menu_open' not in st.session_state:
    st.session_state.menu_open = False
if 'admin_authenticated' not in st.session_state:
    st.session_state.admin_authenticated = False
if 'booking_step' not in st.session_state:
    st.session_state.booking_step = 1
if 'patient_data' not in st.session_state:
    st.session_state.patient_data = {}

# Modern CSS with Hamburger Menu
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display: none;}
    header {visibility: hidden;}
    [data-testid="stSidebar"] {display: none;}
    
    /* Main container */
    .main {
        padding: 0 !important;
        background: #f8fafc;
        min-height: 100vh;
    }
    
    /* Header with Hamburger Menu */
    .header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem 2rem;
        position: sticky;
        top: 0;
        z-index: 1000;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .logo {
        color: white;
        font-size: 1.8rem;
        font-weight: 800;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .hamburger {
        cursor: pointer;
        background: none;
        border: none;
        color: white;
        font-size: 1.5rem;
        padding: 0.5rem;
        border-radius: 8px;
        transition: all 0.3s ease;
    }
    
    .hamburger:hover {
        background: rgba(255,255,255,0.1);
    }
    
    /* Side Navigation */
    .sidenav {
        height: 100vh;
        width: 0;
        position: fixed;
        z-index: 1001;
        top: 0;
        right: 0;
        background: linear-gradient(180deg, #1a202c 0%, #2d3748 100%);
        overflow-x: hidden;
        transition: 0.4s cubic-bezier(0.23, 1, 0.320, 1);
        box-shadow: -10px 0 30px rgba(0,0,0,0.3);
    }
    
    .sidenav.open {
        width: 350px;
    }
    
    .closebtn {
        position: absolute;
        top: 1rem;
        right: 1.5rem;
        font-size: 2rem;
        color: white;
        cursor: pointer;
        background: none;
        border: none;
        padding: 0.5rem;
        border-radius: 8px;
        transition: all 0.3s ease;
    }
    
    .closebtn:hover {
        background: rgba(255,255,255,0.1);
        transform: rotate(90deg);
    }
    
    .nav-content {
        padding: 4rem 2rem 2rem;
    }
    
    .nav-item {
        display: block;
        padding: 1.2rem 1.5rem;
        color: #e2e8f0;
        text-decoration: none;
        font-size: 1.1rem;
        font-weight: 500;
        border-radius: 12px;
        margin: 0.5rem 0;
        transition: all 0.3s ease;
        cursor: pointer;
        display: flex;
        align-items: center;
        gap: 1rem;
    }
    
    .nav-item:hover {
        background: rgba(255,255,255,0.1);
        color: white;
        transform: translateX(10px);
    }
    
    .nav-item.active {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
    }
    
    .nav-icon {
        font-size: 1.3rem;
        width: 24px;
        text-align: center;
    }
    
    /* Hero Section */
    .hero {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 6rem 2rem;
        text-align: center;
        position: relative;
        overflow: hidden;
    }
    
    .hero::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1440 320"><path fill="%23ffffff" fill-opacity="0.1" d="M0,96L48,112C96,128,192,160,288,160C384,160,480,128,576,122.7C672,117,768,139,864,154.7C960,171,1056,181,1152,165.3C1248,149,1344,107,1392,85.3L1440,64L1440,320L1392,320C1344,320,1248,320,1152,320C1056,320,960,320,864,320C768,320,672,320,576,320C480,320,384,320,288,320C192,320,96,320,48,320L0,320Z"></path></svg>') no-repeat bottom;
        background-size: cover;
    }
    
    .hero-content {
        position: relative;
        z-index: 1;
        max-width: 800px;
        margin: 0 auto;
    }
    
    .hero h1 {
        font-size: 3.5rem;
        font-weight: 800;
        margin-bottom: 1.5rem;
        text-shadow: 2px 4px 8px rgba(0,0,0,0.2);
        line-height: 1.2;
    }
    
    .hero p {
        font-size: 1.3rem;
        opacity: 0.95;
        margin-bottom: 2.5rem;
        font-weight: 300;
    }
    
    /* Container */
    .container {
        max-width: 1200px;
        margin: 0 auto;
        padding: 0 2rem;
    }
    
    /* Section */
    .section {
        padding: 4rem 0;
    }
    
    /* Grid */
    .grid {
        display: grid;
        gap: 2rem;
    }
    
    .grid-2 { grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); }
    .grid-3 { grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); }
    .grid-4 { grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); }
    
    /* Cards */
    .card {
        background: white;
        padding: 2.5rem;
        border-radius: 20px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.08);
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        border: 1px solid rgba(0,0,0,0.05);
        cursor: pointer;
        position: relative;
        overflow: hidden;
    }
    
    .card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        opacity: 0;
        transition: opacity 0.3s ease;
    }
    
    .card:hover {
        transform: translateY(-10px) scale(1.02);
        box-shadow: 0 20px 60px rgba(102, 126, 234, 0.3);
    }
    
    .card:hover::before {
        opacity: 0.05;
    }
    
    .card-icon {
        font-size: 3.5rem;
        margin-bottom: 1.5rem;
        display: block;
        position: relative;
        z-index: 1;
    }
    
    .card-title {
        font-size: 1.5rem;
        font-weight: 700;
        color: #2d3748;
        margin-bottom: 1rem;
        position: relative;
        z-index: 1;
    }
    
    .card-description {
        color: #718096;
        font-size: 1rem;
        line-height: 1.6;
        position: relative;
        z-index: 1;
    }
    
    /* Stats */
    .stats {
        background: white;
        padding: 3rem;
        border-radius: 20px;
        box-shadow: 0 15px 50px rgba(0,0,0,0.1);
        text-align: center;
        border-top: 4px solid #667eea;
    }
    
    .stat-number {
        font-size: 3rem;
        font-weight: 800;
        color: #667eea;
        margin-bottom: 0.5rem;
        display: block;
    }
    
    .stat-label {
        color: #718096;
        font-size: 1rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-weight: 600;
    }
    
    /* Image Placeholder */
    .image-placeholder {
        background: linear-gradient(135deg, #e2e8f0 0%, #cbd5e0 100%);
        border-radius: 15px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #a0aec0;
        font-size: 4rem;
        min-height: 300px;
        margin: 2rem 0;
        border: 2px dashed #cbd5e0;
        transition: all 0.3s ease;
    }
    
    .image-placeholder:hover {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-color: #667eea;
    }
    
    /* Buttons */
    .btn {
        display: inline-block;
        padding: 1rem 2.5rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 50px;
        font-size: 1.1rem;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
        text-decoration: none;
        text-transform: uppercase;
        letter-spacing: 1px;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
    }
    
    .btn:hover {
        transform: translateY(-3px);
        box-shadow: 0 15px 35px rgba(102, 126, 234, 0.4);
    }
    
    .btn-secondary {
        background: linear-gradient(135deg, #e2e8f0 0%, #cbd5e0 100%);
        color: #4a5568;
    }
    
    /* Form Elements */
    .form-group {
        margin-bottom: 1.5rem;
    }
    
    .form-label {
        display: block;
        margin-bottom: 0.5rem;
        font-weight: 600;
        color: #4a5568;
    }
    
    .form-input {
        width: 100%;
        padding: 1rem 1.5rem;
        border: 2px solid #e2e8f0;
        border-radius: 12px;
        font-size: 1rem;
        transition: all 0.3s ease;
        background: #f7fafc;
    }
    
    .form-input:focus {
        border-color: #667eea;
        background: white;
        box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.1);
        outline: none;
    }
    
    /* Responsive */
    @media (max-width: 768px) {
        .hero h1 { font-size: 2.5rem; }
        .hero p { font-size: 1.1rem; }
        .container { padding: 0 1rem; }
        .card { padding: 1.5rem; }
        .sidenav.open { width: 280px; }
    }
    
    /* Animations */
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(30px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .fade-in-up {
        animation: fadeInUp 0.6s ease-out;
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar { width: 8px; }
    ::-webkit-scrollbar-track { background: #f1f1f1; }
    ::-webkit-scrollbar-thumb { 
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 4px;
    }
    ::-webkit-scrollbar-thumb:hover { background: #5568d3; }
</style>
""", unsafe_allow_html=True)

# Header with Hamburger Menu
st.markdown(f"""
<div class="header">
    <div class="logo">
        🏥 MediCare Plus
    </div>
    <button class="hamburger" onclick="toggleNav()">
        ☰
    </button>
</div>

<div id="sideNav" class="sidenav">
    <button class="closebtn" onclick="closeNav()">&times;</button>
    <div class="nav-content">
        <a href="#" class="nav-item {'active' if st.session_state.current_page == 'home' else ''}" onclick="navigateTo('home')">
            <span class="nav-icon">🏠</span>
            Home
        </a>
        <a href="#" class="nav-item {'active' if st.session_state.current_page == 'booking' else ''}" onclick="navigateTo('booking')">
            <span class="nav-icon">📅</span>
            Book Appointment
        </a>
        <a href="#" class="nav-item {'active' if st.session_state.current_page == 'symptoms' else ''}" onclick="navigateTo('symptoms')">
            <span class="nav-icon">🔍</span>
            Symptom Checker
        </a>
        <a href="#" class="nav-item {'active' if st.session_state.current_page == 'portal' else ''}" onclick="navigateTo('portal')">
            <span class="nav-icon">👤</span>
            Patient Portal
        </a>
        <a href="#" class="nav-item {'active' if st.session_state.current_page == 'admin' else ''}" onclick="navigateTo('admin')">
            <span class="nav-icon">🔐</span>
            Admin Dashboard
        </a>
    </div>
</div>

<script>
function toggleNav() {{
    const nav = document.getElementById("sideNav");
    nav.classList.toggle("open");
}}

function closeNav() {{
    document.getElementById("sideNav").classList.remove("open");
}}

function navigateTo(page) {{
    window.parent.postMessage({{
        type: 'streamlit:setComponentValue',
        value: page
    }}, '*');
    closeNav();
}}
</script>
""", unsafe_allow_html=True)

# Load data function
@st.cache_data
def load_data():
    try:
        patients_df = pd.read_csv("patients.csv")
        schedule_df = pd.read_excel("doctor_schedule.xlsx")
        return patients_df, schedule_df
    except Exception as e:
        st.error(f"Error loading data files: {str(e)}")
        return pd.DataFrame(), pd.DataFrame()

patients_df, schedule_df = load_data()

# Navigation handling
col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    if st.button("🏠 Home", key="nav_home"):
        st.session_state.current_page = 'home'
with col2:
    if st.button("📅 Book", key="nav_book"):
        st.session_state.current_page = 'booking'
with col3:
    if st.button("🔍 Symptoms", key="nav_symptoms"):
        st.session_state.current_page = 'symptoms'
with col4:
    if st.button("👤 Portal", key="nav_portal"):
        st.session_state.current_page = 'portal'
with col5:
    if st.button("🔐 Admin", key="nav_admin"):
        st.session_state.current_page = 'admin'

# Page Routing
if st.session_state.current_page == 'home':
    # Hero Section
    st.markdown("""
    <div class="hero">
        <div class="hero-content">
            <h1>Your Health, Our Priority</h1>
            <p>Experience world-class healthcare with cutting-edge technology and compassionate care</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Stats Section
    st.markdown('<div class="container section">', unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="stats fade-in-up">
            <span class="stat-number">15K+</span>
            <div class="stat-label">Happy Patients</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="stats fade-in-up">
            <span class="stat-number">50+</span>
            <div class="stat-label">Expert Doctors</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="stats fade-in-up">
            <span class="stat-number">4.9★</span>
            <div class="stat-label">Patient Rating</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="stats fade-in-up">
            <span class="stat-number">24/7</span>
            <div class="stat-label">Emergency Care</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Services Section
    st.markdown('<div class="section">', unsafe_allow_html=True)
    st.markdown('<h2 style="text-align: center; margin-bottom: 3rem; font-size: 2.5rem; color: #2d3748;">Our Services</h2>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="card fade-in-up">
            <div class="card-icon">📅</div>
            <h3 class="card-title">Online Booking</h3>
            <p class="card-description">Schedule appointments with our specialists instantly through our advanced booking system.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="card fade-in-up">
            <div class="card-icon">🤖</div>
            <h3 class="card-title">AI Diagnosis</h3>
            <p class="card-description">Get preliminary health assessments using our AI-powered symptom checker technology.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="card fade-in-up">
            <div class="card-icon">📱</div>
            <h3 class="card-title">Digital Records</h3>
            <p class="card-description">Access your complete medical history and test results anytime, anywhere securely.</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Image placeholder
    st.markdown("""
    <div class="image-placeholder">
        🏥 Modern Healthcare Facility Image
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('</div></div>', unsafe_allow_html=True)

elif st.session_state.current_page == 'booking':
    st.markdown("""
    <div class="container section">
        <h1 style="text-align: center; margin-bottom: 2rem; color: #2d3748;">Book Your Appointment</h1>
        <div class="card" style="max-width: 600px; margin: 0 auto;">
            <h3>Patient Information</h3>
            <form>
                <div class="form-group">
                    <label class="form-label">Full Name</label>
                    <input type="text" class="form-input" placeholder="Enter your full name">
                </div>
                <div class="form-group">
                    <label class="form-label">Email Address</label>
                    <input type="email" class="form-input" placeholder="your.email@example.com">
                </div>
                <div class="form-group">
                    <label class="form-label">Phone Number</label>
                    <input type="tel" class="form-input" placeholder="+1 (555) 000-0000">
                </div>
                <div class="form-group">
                    <label class="form-label">Preferred Doctor</label>
                    <select class="form-input">
                        <option>Select a doctor...</option>
                        <option>Dr. Sarah Johnson - Cardiology</option>
                        <option>Dr. Michael Chen - Dermatology</option>
                        <option>Dr. Emily Davis - Pediatrics</option>
                    </select>
                </div>
                <button type="submit" class="btn" style="width: 100%; margin-top: 1rem;">
                    Book Appointment
                </button>
            </form>
        </div>
    </div>
    """, unsafe_allow_html=True)

elif st.session_state.current_page == 'symptoms':
    st.markdown("""
    <div class="container section">
        <h1 style="text-align: center; margin-bottom: 2rem; color: #2d3748;">AI Symptom Checker</h1>
        <div class="card" style="max-width: 700px; margin: 0 auto;">
            <div class="card-icon" style="text-align: center;">🤖</div>
            <h3 style="text-align: center; margin-bottom: 2rem;">Describe Your Symptoms</h3>
            <form>
                <div class="form-group">
                    <label class="form-label">What symptoms are you experiencing?</label>
                    <textarea class="form-input" rows="4" placeholder="Please describe your symptoms in detail..."></textarea>
                </div>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
                    <div class="form-group">
                        <label class="form-label">Pain Level (1-10)</label>
                        <input type="range" min="1" max="10" class="form-input">
                    </div>
                    <div class="form-group">
                        <label class="form-label">Duration</label>
                        <select class="form-input">
                            <option>Less than 1 hour</option>
                            <option>1-6 hours</option>
                            <option>6-24 hours</option>
                            <option>1-3 days</option>
                            <option>More than 3 days</option>
                        </select>
                    </div>
                </div>
                <button type="submit" class="btn" style="width: 100%; margin-top: 1rem;">
                    Analyze Symptoms
                </button>
            </form>
        </div>
    </div>
    """, unsafe_allow_html=True)

elif st.session_state.current_page == 'portal':
    st.markdown("""
    <div class="container section">
        <h1 style="text-align: center; margin-bottom: 2rem; color: #2d3748;">Patient Portal</h1>
        <div class="grid grid-2">
            <div class="card">
                <div class="card-icon">👤</div>
                <h3 class="card-title">My Profile</h3>
                <p class="card-description">View and update your personal information and medical history.</p>
            </div>
            <div class="card">
                <div class="card-icon">📋</div>
                <h3 class="card-title">Appointments</h3>
                <p class="card-description">View upcoming appointments and appointment history.</p>
            </div>
            <div class="card">
                <div class="card-icon">💊</div>
                <h3 class="card-title">Prescriptions</h3>
                <p class="card-description">Access your current medications and prescription history.</p>
            </div>
            <div class="card">
                <div class="card-icon">📊</div>
                <h3 class="card-title">Test Results</h3>
                <p class="card-description">View your latest lab results and medical reports.</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

elif st.session_state.current_page == 'admin':
    if not st.session_state.admin_authenticated:
        st.markdown("""
        <div class="container section">
            <div class="card" style="max-width: 400px; margin: 0 auto;">
                <div class="card-icon" style="text-align: center;">🔐</div>
                <h3 style="text-align: center; margin-bottom: 2rem;">Admin Login</h3>
                <form>
                    <div class="form-group">
                        <label class="form-label">Username</label>
                        <input type="text" class="form-input" placeholder="Enter username">
                    </div>
                    <div class="form-group">
                        <label class="form-label">Password</label>
                        <input type="password" class="form-input" placeholder="Enter password">
                    </div>
                    <button type="submit" class="btn" style="width: 100%;">
                        Login
                    </button>
                </form>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="container section">
            <h1 style="text-align: center; margin-bottom: 3rem; color: #2d3748;">Admin Dashboard</h1>
            <div class="grid grid-4">
                <div class="stats">
                    <span class="stat-number">156</span>
                    <div class="stat-label">Total Appointments</div>
                </div>
                <div class="stats">
                    <span class="stat-number">12</span>
                    <div class="stat-label">Today's Appointments</div>
                </div>
                <div class="stats">
                    <span class="stat-number">1,247</span>
                    <div class="stat-label">Total Patients</div>
                </div>
                <div class="stats">
                    <span class="stat-number">8</span>
                    <div class="stat-label">Active Doctors</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# Footer
st.markdown("""
<div style="background: #2d3748; color: white; padding: 3rem 2rem; margin-top: 4rem;">
    <div class="container">
        <div style="text-align: center;">
            <h3 style="margin-bottom: 1rem;">MediCare Plus</h3>
            <p style="opacity: 0.8; margin-bottom: 2rem;">Your trusted healthcare partner</p>
            <div style="display: flex; justify-content: center; gap: 2rem; flex-wrap: wrap;">
                <span>📞 +1 (555) 123-4567</span>
                <span>📧 contact@medicareplus.com</span>
                <span>📍 123 Healthcare Ave, Medical City</span>
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)