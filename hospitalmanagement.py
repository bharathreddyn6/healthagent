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

# Load environment variables from a .env file in the project root (if present)
load_dotenv()
from datetime import datetime, timedelta
from langchain_google_genai import ChatGoogleGenerativeAI

# Enhanced page configuration - Modern Healthcare Portal
st.set_page_config(
    page_title="MediCare Plus - Modern Healthcare",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize session state for modern navigation
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'home'
if 'menu_open' not in st.session_state:
    st.session_state.menu_open = False

# Modern CSS with Hamburger Menu Navigation
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
        left: 0;
        background: linear-gradient(180deg, #1e3c72 0%, #2a5298 100%);
        overflow-x: hidden;
        transition: 0.3s ease;
        box-shadow: 4px 0 20px rgba(0,0,0,0.3);
    }
    
    .sidenav.open {
        width: 320px;
    }
    
    .sidenav-content {
        padding: 2rem 1rem;
        margin-top: 60px;
    }
    
    .nav-item {
        display: block;
        padding: 1rem 1.5rem;
        color: white;
        text-decoration: none;
        font-size: 1.1rem;
        font-weight: 500;
        border-radius: 12px;
        margin: 0.5rem 0;
        transition: all 0.3s ease;
        cursor: pointer;
        border: 2px solid transparent;
    }
    
    .nav-item:hover {
        background: rgba(255,255,255,0.1);
        transform: translateX(10px);
    }
    
    .nav-item.active {
        background: white;
        color: #667eea;
        transform: translateX(10px);
    }
    
    .close-btn {
        position: absolute;
        top: 1rem;
        right: 1.5rem;
        font-size: 2rem;
        color: white;
        cursor: pointer;
        background: none;
        border: none;
    }
    
    /* Content Area */
    .content {
        padding: 2rem;
        max-width: 1400px;
        margin: 0 auto;
    }
    
    /* Hero Section */
    .hero-section {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 4rem 2rem;
        text-align: center;
        border-radius: 20px;
        margin: 2rem 0;
        position: relative;
        overflow: hidden;
    }
    
    .hero-section::before {
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
    }
    
    .hero-content h1 {
        font-size: 3.5rem;
        font-weight: 800;
        margin: 0 0 1rem 0;
        text-shadow: 2px 4px 8px rgba(0,0,0,0.2);
    }
    
    .hero-content p {
        font-size: 1.3rem;
        opacity: 0.95;
        font-weight: 300;
        max-width: 600px;
        margin: 0 auto;
    }
    
    /* Feature Cards */
    .feature-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: 2rem;
        margin: 3rem 0;
    }
    
    .feature-card {
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
    
    .feature-card::before {
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
    
    .feature-card:hover {
        transform: translateY(-10px) scale(1.02);
        box-shadow: 0 20px 60px rgba(102, 126, 234, 0.3);
    }
    
    .feature-card:hover::before {
        opacity: 0.05;
    }
    
    .feature-icon {
        font-size: 3.5rem;
        margin-bottom: 1.5rem;
        display: block;
        position: relative;
        z-index: 1;
    }
    
    .feature-title {
        font-size: 1.5rem;
        font-weight: 700;
        color: #2d3748;
        margin-bottom: 1rem;
        position: relative;
        z-index: 1;
    }
    
    .feature-description {
        color: #718096;
        font-size: 1rem;
        line-height: 1.6;
        position: relative;
        z-index: 1;
    }
    
    /* Booking Cards */
    .booking-card {
        background: white;
        padding: 3rem;
        border-radius: 25px;
        box-shadow: 0 15px 50px rgba(0,0,0,0.1);
        margin: 2rem 0;
        position: relative;
    }
    
    .booking-card::after {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 5px;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        border-radius: 25px 25px 0 0;
    }
    
    /* Progress Steps */
    .progress-steps {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin: 2rem 0 3rem 0;
        position: relative;
        padding: 0 2rem;
    }
    
    .progress-steps::before {
        content: '';
        position: absolute;
        top: 25px;
        left: 10%;
        right: 10%;
        height: 3px;
        background: #e2e8f0;
        z-index: 0;
    }
    
    .step {
        text-align: center;
        position: relative;
        z-index: 1;
        flex: 1;
    }
    
    .step-circle {
        width: 50px;
        height: 50px;
        border-radius: 50%;
        background: #e2e8f0;
        color: #a0aec0;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto 0.5rem;
        font-weight: 700;
        font-size: 1.2rem;
        transition: all 0.3s ease;
        border: 3px solid white;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    }
    
    .step-circle.active {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        transform: scale(1.1);
        box-shadow: 0 10px 25px rgba(102, 126, 234, 0.4);
    }
    
    .step-circle.completed {
        background: linear-gradient(135deg, #48bb78 0%, #38a169 100%);
        color: white;
    }
    
    /* Input Fields */
    .stTextInput > div > div > input,
    .stSelectbox > div > div > select,
    .stTextArea > div > div > textarea {
        border-radius: 12px !important;
        border: 2px solid #e2e8f0 !important;
        padding: 1rem 1.5rem !important;
        font-size: 1rem !important;
        transition: all 0.3s ease !important;
        background: #f7fafc !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stSelectbox > div > div > select:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #667eea !important;
        background: white !important;
        box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.1) !important;
    }
    
    /* Buttons */
    .stButton > button {
        border-radius: 50px !important;
        padding: 1rem 3rem !important;
        font-weight: 600 !important;
        font-size: 1.1rem !important;
        transition: all 0.3s ease !important;
        border: none !important;
        box-shadow: 0 8px 20px rgba(0,0,0,0.15) !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
    }
    
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 12px 30px rgba(102, 126, 234, 0.4) !important;
    }
    
    /* Dashboard Metrics */
    .dashboard-metric {
        background: white;
        padding: 2rem;
        border-radius: 20px;
        box-shadow: 0 8px 30px rgba(0,0,0,0.08);
        text-align: center;
        transition: all 0.3s ease;
        border-top: 4px solid #667eea;
    }
    
    .dashboard-metric:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 40px rgba(102, 126, 234, 0.2);
    }
    
    .metric-value {
        font-size: 3rem;
        font-weight: 800;
        color: #667eea;
        margin: 0;
    }
    
    /* Alert Boxes */
    .alert {
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1.5rem 0;
        border-left: 5px solid;
        font-weight: 500;
    }
    
    .alert-success {
        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
        border-color: #28a745;
        color: #155724;
    }
    
    .alert-warning {
        background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);
        border-color: #ffc107;
        color: #856404;
    }
    
    .alert-info {
        background: linear-gradient(135deg, #d1ecf1 0%, #bee5eb 100%);
        border-color: #17a2b8;
        color: #0c5460;
    }
    
    /* Responsive Design */
    @media (max-width: 768px) {
        .header {
            padding: 1rem;
        }
        
        .logo {
            font-size: 1.4rem;
        }
        
        .hero-content h1 {
            font-size: 2.5rem;
        }
        
        .feature-grid {
            grid-template-columns: 1fr;
            gap: 1.5rem;
        }
        
        .content {
            padding: 1rem;
        }
    }
    
    /* Animations */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .fade-in {
        animation: fadeIn 0.6s ease-out;
    }
</style>
""", unsafe_allow_html=True)


# Load data
def load_data():
    try:
        patients_df = pd.read_csv("patients.csv")
        height: 100%;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
        transition: width 0.5s ease;
        box-shadow: 0 2px 10px rgba(102, 126, 234, 0.5);
    }

    /* Step Cards */
    .step-card {
        background: white;
        padding: 3rem;
        border-radius: 24px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.08);
        border: 1px solid rgba(230,230,230,0.5);
        margin: 2rem 0;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }

    .step-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 5px;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    }

    .step-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 20px 50px rgba(0,0,0,0.12);
    }

    .step-header {
        display: flex;
        align-items: center;
        margin-bottom: 2rem;
        padding-bottom: 1.5rem;
        border-bottom: 2px solid #f0f0f0;
    }

    .step-icon {
        width: 70px;
        height: 70px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 20px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: 2rem;
        font-weight: bold;
        margin-right: 1.5rem;
        box-shadow: 0 8px 24px rgba(102,126,234,0.4);
        position: relative;
    }

    .step-icon::after {
        content: '';
        position: absolute;
        width: 100%;
        height: 100%;
        border-radius: 20px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        opacity: 0.5;
        filter: blur(15px);
        z-index: -1;
    }

    .step-title {
        font-family: 'Poppins', sans-serif;
        font-size: 2rem;
        font-weight: 700;
        color: #1a1a1a;
        margin: 0;
        letter-spacing: -0.5px;
    }

    /* Info Cards */
    .info-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        padding: 2rem;
        border-radius: 16px;
        border-left: 5px solid #667eea;
        margin: 1.5rem 0;
        box-shadow: 0 4px 20px rgba(0,0,0,0.06);
        transition: all 0.3s ease;
    }

    .info-card:hover {
        transform: translateX(4px);
        box-shadow: 0 6px 25px rgba(0,0,0,0.1);
    }

    .info-card h4 {
        color: #667eea;
        font-weight: 700;
        font-size: 1.2rem;
        margin-bottom: 1rem;
    }

    .success-card {
        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
        border-left: 5px solid #28a745;
    }

    .success-card h4 {
        color: #155724;
    }

    .warning-card {
        background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);
        border-left: 5px solid #ffc107;
    }

    .warning-card h4 {
        color: #856404;
    }

    .symptom-card {
        background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
        padding: 2.5rem;
        border-radius: 20px;
        margin: 1.5rem 0;
        box-shadow: 0 8px 30px rgba(252, 182, 159, 0.3);
    }

    /* Alert Cards */
    .emergency-alert {
        background: linear-gradient(135deg, #ff6b6b 0%, #ee5a6f 100%);
        padding: 1.5rem;
        border-radius: 16px;
        border-left: 5px solid #dc3545;
        margin: 1.5rem 0;
        color: white;
        box-shadow: 0 8px 30px rgba(220, 53, 69, 0.3);
        animation: pulse 2s infinite;
    }

    @keyframes pulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.02); }
    }

    .urgent-alert {
        background: linear-gradient(135deg, #ffa502 0%, #ff6348 100%);
        padding: 1.5rem;
        border-radius: 16px;
        border-left: 5px solid #fd79a8;
        margin: 1.5rem 0;
        color: white;
        box-shadow: 0 8px 30px rgba(255, 99, 72, 0.3);
    }

    .routine-alert {
        background: linear-gradient(135deg, #00d2ff 0%, #3a7bd5 100%);
        padding: 1.5rem;
        border-radius: 16px;
        border-left: 5px solid #00b894;
        margin: 1.5rem 0;
        color: white;
        box-shadow: 0 8px 30px rgba(0, 184, 148, 0.3);
    }

    /* Form Elements */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > select {
        border-radius: 12px;
        border: 2px solid #e1e8ed;
        padding: 1rem 1.25rem;
        font-size: 1rem;
        transition: all 0.3s ease;
        background: white;
        font-family: 'Inter', sans-serif;
    }

    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus,
    .stSelectbox > div > div > select:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 4px rgba(102,126,234,0.1);
        outline: none;
    }

    .stTextArea > div > div > textarea {
        min-height: 120px;
    }

    /* Buttons */
    .stButton > button {
        border-radius: 12px;
        padding: 1rem 2.5rem;
        font-weight: 600;
        font-size: 1.1rem;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        border: none;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        font-family: 'Inter', sans-serif;
        letter-spacing: 0.5px;
    }

    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }

    .stButton > button[kind="secondary"] {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
    }

    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
    }

    .stButton > button:active {
        transform: translateY(-1px);
    }

    /* Metric Cards */
    .metric-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        padding: 2rem;
        border-radius: 20px;
        text-align: center;
        box-shadow: 0 6px 25px rgba(0,0,0,0.08);
        border: 1px solid rgba(230,230,230,0.5);
        margin: 1rem 0;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }

    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 4px;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    }

    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 35px rgba(0,0,0,0.12);
    }

    /* Doctor Card */
    .doctor-card {
        background: white;
        padding: 2rem;
        border-radius: 16px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.06);
        margin: 1rem 0;
        transition: all 0.3s ease;
        border: 2px solid transparent;
    }

    .doctor-card:hover {
        border-color: #667eea;
        box-shadow: 0 8px 30px rgba(102,126,234,0.2);
        transform: scale(1.02);
    }

    /* Time Slot */
    .time-slot {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 1rem 1.5rem;
        border-radius: 12px;
        margin: 0.5rem;
        display: inline-block;
        cursor: pointer;
        transition: all 0.3s ease;
        border: 2px solid transparent;
    }

    .time-slot:hover {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(102,126,234,0.3);
    }

    .time-slot.selected {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-color: #764ba2;
    }

    /* Expander Styling */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        border-radius: 12px;
        padding: 1rem;
        font-weight: 600;
        border: 2px solid #e1e8ed;
        transition: all 0.3s ease;
    }

    .streamlit-expanderHeader:hover {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-color: #667eea;
    }

    /* Admin Dashboard Specific */
    .admin-header {
        background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
        color: white;
        padding: 2rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        box-shadow: 0 8px 30px rgba(44, 62, 80, 0.3);
    }

    .admin-card {
        background: white;
        border-radius: 16px;
        padding: 2rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.06);
        margin: 1rem 0;
        border-left: 4px solid #667eea;
        transition: all 0.3s ease;
    }

    .admin-card:hover {
        box-shadow: 0 8px 30px rgba(0,0,0,0.1);
        transform: translateX(4px);
    }

    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 1rem;
        background: white;
        padding: 1rem;
        border-radius: 16px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.06);
    }

    .stTabs [data-baseweb="tab"] {
        padding: 1rem 2rem;
        border-radius: 12px;
        font-weight: 600;
        background: transparent;
        border: 2px solid transparent;
        transition: all 0.3s ease;
    }

    .stTabs [data-baseweb="tab"]:hover {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white !important;
        border-color: #667eea;
    }

    /* Dataframe Styling */
    .dataframe {
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 4px 20px rgba(0,0,0,0.06);
    }

    /* Loading Animation */
    .stSpinner > div {
        border-top-color: #667eea !important;
    }

    /* Sidebar Styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }

    /* Success/Error Messages */
    .stSuccess, .stError, .stWarning, .stInfo {
        border-radius: 12px;
        padding: 1rem 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
    }

    /* Selectbox Dropdown */
    .stSelectbox [data-baseweb="select"] {
        border-radius: 12px;
    }

    /* Smooth Animations */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }

    .step-card, .info-card, .metric-card {
        animation: fadeIn 0.5s ease-out;
    }

    /* Glassmorphism Effect */
    .glass-card {
        background: rgba(255, 255, 255, 0.7);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.3);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    }
</style>
""",
            unsafe_allow_html=True)


# Load data
def load_data():
    try:
        patients_df = pd.read_csv("patients.csv")
        schedule_df = pd.read_excel("doctor_schedule.xlsx")
        return patients_df, schedule_df
    except Exception as e:
        st.error(f"Error loading data files: {str(e)}")
        st.stop()


patients_df, schedule_df = load_data()


# Helper functions
def normalize_name(name: str) -> str:
    return re.sub(r'\s+', ' ', name).strip().lower()


def normalize_dob(dob: str) -> str:
    parts = dob.replace("/", "-").split("-")
    if len(parts) == 3:
        day = parts[0].zfill(2)
        month = parts[1].zfill(2)
        year = parts[2]
        return f"{day}-{month}-{year}"
    return dob.strip()


# AI Symptom Checker Function
def ai_symptom_checker(symptoms_text):
    """AI-based symptom analysis using LangChain + Google GenAI"""
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-pro" , api_key="AIzaSyDLe5OQ7_7iplT5EHrreg7MKfDiQ2Bl0Ww")
    prompt = f"""
You are a helpful medical assistant. A patient described the following symptoms:

{symptoms_text}  

Please provide:
1. A short summary of the symptoms
2. Possible conditions (not a diagnosis)
3. Urgency level (Emergency, Urgent, or Routine)
4. The type of doctor they should see
Respond clearly in simple terms.
"""
    try:
        response = llm.invoke(prompt)
        return response.content
    except Exception as e:
        return f"Error fetching AI response: {str(e)}"


# Patient Portal Function
def patient_portal():
    st.markdown("## Patient Portal")

    if 'patient_email' not in st.session_state:
        st.session_state.patient_email = ""

    email = st.text_input("Enter your email to access medical records:",
                          value=st.session_state.patient_email)

    if st.button("Access Records") and email:
        st.session_state.patient_email = email

        try:
            appointments_df = pd.read_excel("appointments.xlsx")
            patient_appointments = appointments_df[appointments_df['email'] ==
                                                   email]

            if not patient_appointments.empty:
                st.success(
                    f"Found {len(patient_appointments)} appointments for {email}"
                )

                st.markdown("### Your Appointments")
                for idx, appointment in patient_appointments.iterrows():
                    with st.expander(
                            f"Appointment with Dr. {appointment['doctor']} - {appointment['slot']}"
                    ):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(
                                f"**Doctor:** Dr. {appointment['doctor']}")
                            st.write(f"**Date & Time:** {appointment['slot']}")
                            st.write(
                                f"**Visit Type:** {appointment['visit_type']}")
                        with col2:
                            st.write(
                                f"**Insurance:** {appointment.get('insurance_carrier', 'Self-Pay')}"
                            )
                            st.write(f"**Status:** Scheduled")

                st.markdown("### Medical History")
                st.info(
                    "Medical history features will be available in future updates."
                )
            else:
                st.warning("No appointments found for this email address.")
        except FileNotFoundError:
            st.error("No appointment records found in the system.")


# ADMIN DASHBOARD FUNCTIONS
def admin_login():
    st.markdown("## Admin Authentication")

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        with st.form("admin_login"):
            st.markdown("### Please enter admin credentials")
            username = st.text_input("Username:")
            password = st.text_input("Password:", type="password")

            submitted = st.form_submit_button("Login", type="primary")

            if submitted:
                if username == "admin" and password == "admin123":
                    st.session_state.admin_authenticated = True
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error("Invalid credentials!")


def dashboard_overview():
    st.markdown("## Dashboard Overview")

    try:
        appointments_df = pd.read_excel("appointments.xlsx")
        schedule_df = pd.read_excel("doctor_schedule.xlsx")
        patients_df = pd.read_csv("patients.csv")

        col1, col2, col3, col4, col5 = st.columns(5)

        with col1:
            st.metric("Total Appointments", len(appointments_df))

        with col2:
            today_appointments = len(
                appointments_df[appointments_df['slot'].str.contains(
                    datetime.now().strftime('%Y-%m-%d'), na=False)])
            st.metric("Today's Appointments", today_appointments)

        with col3:
            st.metric("Total Patients", len(patients_df))

        with col4:
            st.metric("Active Doctors", len(schedule_df["doctor"].unique()))

        with col5:
            available_slots = len(
                schedule_df[schedule_df["status"] == 'Available'])
            st.metric("Available Slots", available_slots)

        col1, col2 = st.columns(2)

        with col1:
            fig_recent = px.bar(
                appointments_df['doctor'].value_counts().head(10),
                title="Appointments by Doctor (Top 10)",
                labels={
                    'value': 'Number of Appointments',
                    'index': 'Doctor'
                })
            st.plotly_chart(fig_recent, use_container_width=True)

        with col2:
            visit_counts = appointments_df['visit_type'].value_counts()
            fig_visits = px.pie(values=visit_counts.values,
                                names=visit_counts.index,
                                title="Visit Type Distribution")
            st.plotly_chart(fig_visits, use_container_width=True)

        st.markdown("### Recent Activity")
        recent_appointments = appointments_df.tail(10)
        st.dataframe(recent_appointments[[
            'name', 'doctor', 'slot', 'visit_type', 'email'
        ]])

    except Exception as e:
        st.error(f"Error loading dashboard data: {str(e)}")


def appointment_management():
    st.markdown("## Appointment Management")

    try:
        appointments_df = pd.read_excel("appointments.xlsx")

        col1, col2, col3 = st.columns(3)

        with col1:
            search_patient = st.text_input("Search by Patient Name:")

        with col2:
            filter_doctor = st.selectbox(
                "Filter by Doctor:",
                ["All"] + list(appointments_df['doctor'].unique()))

        with col3:
            filter_date = st.date_input("Filter by Date:")

        filtered_df = appointments_df.copy()

        if search_patient:
            filtered_df = filtered_df[filtered_df['name'].str.contains(
                search_patient, case=False, na=False)]

        if filter_doctor != "All":
            filtered_df = filtered_df[filtered_df['doctor'] == filter_doctor]

        if filter_date:
            date_str = filter_date.strftime('%Y-%m-%d')
            filtered_df = filtered_df[filtered_df['slot'].str.contains(
                date_str, na=False)]

        st.markdown(f"### Appointments ({len(filtered_df)} found)")

        for idx, appointment in filtered_df.iterrows():
            with st.expander(
                    f"{appointment['name']} - Dr. {appointment['doctor']} - {appointment['slot']}"
            ):
                col1, col2 = st.columns([3, 1])

                with col1:
                    st.write(f"**Patient:** {appointment['name']}")
                    st.write(f"**Doctor:** Dr. {appointment['doctor']}")
                    st.write(f"**Date & Time:** {appointment['slot']}")
                    st.write(f"**Visit Type:** {appointment['visit_type']}")
                    st.write(f"**Email:** {appointment['email']}")
                    if pd.notna(appointment.get('insurance_carrier')):
                        st.write(
                            f"**Insurance:** {appointment['insurance_carrier']}"
                        )

                with col2:
                    if st.button(f"Cancel", key=f"cancel_{idx}"):
                        appointments_df = appointments_df.drop(idx)
                        appointments_df.to_excel("appointments.xlsx",
                                                 index=False)
                        st.success("Appointment cancelled!")
                        st.rerun()

        col1, col2 = st.columns(2)

        with col1:
            if st.button("Export Appointments to CSV"):
                csv = filtered_df.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name=
                    f"appointments_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv")

    except Exception as e:
        st.error(f"Error managing appointments: {str(e)}")


def doctor_schedule_management():
    st.markdown("## Doctor Schedule Management")

    try:
        schedule_df = pd.read_excel("doctor_schedule.xlsx")
        selected_doctor = st.selectbox("Select Doctor:",
                                       schedule_df['doctor'].unique())

        doctor_schedule = schedule_df[schedule_df['doctor'] == selected_doctor]

        col1, col2 = st.columns([2, 1])

        with col1:
            st.markdown(f"### Schedule for Dr. {selected_doctor}")

            status_filter = st.selectbox(
                "Filter by Status:", ["All", "Available", "Booked", "Blocked"])

            filtered_schedule = doctor_schedule.copy()
            if status_filter != "All":
                filtered_schedule = filtered_schedule[
                    filtered_schedule['status'] == status_filter]

            for idx, slot in filtered_schedule.iterrows():
                col_x, col_y, col_z = st.columns([2, 1, 1])

                with col_x:
                    st.write(f"{slot['date']} - {slot['time_slot']}")

                with col_y:
                    status_color = {
                        'Available': '🟢',
                        'Booked': '🔴',
                        'Blocked': '🟡'
                    }.get(slot['status'], '⚪')
                    st.write(f"{status_color} {slot['status']}")

                with col_z:
                    new_status = st.selectbox(
                        "Change Status:", ["Available", "Booked", "Blocked"],
                        index=["Available", "Booked",
                               "Blocked"].index(slot['status']),
                        key=f"status_{idx}")

                    if new_status != slot['status']:
                        if st.button("Update", key=f"update_{idx}"):
                            schedule_df.at[idx, 'status'] = new_status
                            schedule_df.to_excel("doctor_schedule.xlsx",
                                                 index=False)
                            st.success("Status updated!")
                            st.rerun()

        with col2:
            st.markdown("### Add New Time Slots")

            with st.form("add_slots"):
                new_date = st.date_input("Date:")
                new_time = st.time_input("Time:")

                if st.form_submit_button("Add Slot"):
                    new_slot = pd.DataFrame([{
                        'doctor':
                        selected_doctor,
                        'date':
                        new_date.strftime('%Y-%m-%d'),
                        'time_slot':
                        new_time.strftime('%H:%M'),
                        'status':
                        'Available'
                    }])

                    updated_schedule = pd.concat([schedule_df, new_slot],
                                                 ignore_index=True)
                    updated_schedule.to_excel("doctor_schedule.xlsx",
                                              index=False)
                    st.success("New slot added!")
                    st.rerun()

    except Exception as e:
        st.error(f"Error managing schedule: {str(e)}")


def patient_management():
    st.markdown("## Patient Management")

    try:
        patients_df = pd.read_csv("patients.csv")
        appointments_df = pd.read_excel("appointments.xlsx")

        search_term = st.text_input("Search Patients:",
                                    placeholder="Enter name or email")

        if search_term:
            filtered_patients = patients_df[
                patients_df['first_name'].str.
                contains(search_term, case=False, na=False)
                | patients_df['last_name'].str.
                contains(search_term, case=False, na=False)
                | patients_df['email'].str.
                contains(search_term, case=False, na=False)]
        else:
            filtered_patients = patients_df.head(20)

        st.markdown(f"### Patient Records ({len(filtered_patients)} shown)")

        for idx, patient in filtered_patients.iterrows():
            with st.expander(
                    f"{patient['first_name']} {patient['last_name']} - {patient['email']}"
            ):
                col1, col2 = st.columns([2, 1])

                with col1:
                    st.write(
                        f"**Name:** {patient['first_name']} {patient['last_name']}"
                    )
                    st.write(f"**Date of Birth:** {patient['dob']}")
                    st.write(f"**Email:** {patient['email']}")
                    st.write(f"**Assigned Doctor:** Dr. {patient['doctor']}")

                    if pd.notna(patient.get('insurance_carrier')):
                        st.write(
                            f"**Insurance:** {patient['insurance_carrier']}")

                    patient_appointments = appointments_df[
                        appointments_df['email'] == patient['email']]

                    if not patient_appointments.empty:
                        st.markdown("**Appointment History:**")
                        for _, apt in patient_appointments.iterrows():
                            st.write(
                                f"- {apt['slot']} with Dr. {apt['doctor']}")

    except Exception as e:
        st.error(f"Error managing patients: {str(e)}")


def analytics_reports():
    st.markdown("## Analytics & Reports")

    try:
        appointments_df = pd.read_excel("appointments.xlsx")
        patients_df = pd.read_csv("patients.csv")
        schedule_df = pd.read_excel("doctor_schedule.xlsx")

        report_type = st.selectbox("Select Report Type:", [
            "Appointment Analytics", "Doctor Performance",
            "Patient Demographics"
        ])

        if report_type == "Appointment Analytics":
            st.markdown("### Appointment Analytics")

            col1, col2 = st.columns(2)

            with col1:
                fig_visits = px.bar(
                    appointments_df['visit_type'].value_counts(),
                    title="Visit Type Distribution")
                st.plotly_chart(fig_visits, use_container_width=True)

            with col2:
                fig_doctor = px.bar(appointments_df['doctor'].value_counts(),
                                    title="Appointments by Doctor")
                st.plotly_chart(fig_doctor, use_container_width=True)

        elif report_type == "Doctor Performance":
            st.markdown("### Doctor Performance Report")

            doctor_stats = appointments_df.groupby('doctor').agg({
                'name':
                'count',
                'visit_type':
                lambda x: (x == 'New').sum()
            }).rename(columns={
                'name': 'total_appointments',
                'visit_type': 'new_patients'
            })

            st.dataframe(doctor_stats)

        elif report_type == "Patient Demographics":
            st.markdown("### Patient Demographics")

            insurance_counts = patients_df['insurance_carrier'].value_counts(
            ).head(10)
            fig_insurance = px.pie(values=insurance_counts.values,
                                   names=insurance_counts.index,
                                   title="Top Insurance Providers")
            st.plotly_chart(fig_insurance, use_container_width=True)

    except Exception as e:
        st.error(f"Error generating reports: {str(e)}")


# Modern Navigation Header with Hamburger Menu
def toggle_menu():
    st.session_state.menu_open = not st.session_state.menu_open

def navigate_to(page):
    st.session_state.current_page = page
    st.session_state.menu_open = False
    st.rerun()

# Header with hamburger menu
st.markdown(f"""
<div class="header">
    <div class="logo">
        <span>🏥</span>
        <span>MediCare Plus</span>
    </div>
    <button class="hamburger" onclick="document.getElementById('sidenav').classList.toggle('open')">
        ☰
    </button>
</div>

<div id="sidenav" class="sidenav {'open' if st.session_state.menu_open else ''}">
    <button class="close-btn" onclick="document.getElementById('sidenav').classList.remove('open')">&times;</button>
    <div class="sidenav-content">
        <div class="nav-item {'active' if st.session_state.current_page == 'home' else ''}" onclick="navigate_to('home')">
            🏠 Home
        </div>
        <div class="nav-item {'active' if st.session_state.current_page == 'booking' else ''}" onclick="navigate_to('booking')">
            📅 Book Appointment
        </div>
        <div class="nav-item {'active' if st.session_state.current_page == 'symptoms' else ''}" onclick="navigate_to('symptoms')">
            🧠 Symptom Checker
        </div>
        <div class="nav-item {'active' if st.session_state.current_page == 'portal' else ''}" onclick="navigate_to('portal')">
            👤 Patient Portal
        </div>
        <div class="nav-item {'active' if st.session_state.current_page == 'admin' else ''}" onclick="navigate_to('admin')">
            🔐 Admin Dashboard
        </div>
    </div>
</div>

<script>
function navigate_to(page) {{
    window.parent.postMessage({{
        type: 'streamlit:setComponentValue',
        value: page
    }}, '*');
}}
</script>
""", unsafe_allow_html=True)

# Navigation buttons (temporary until we get proper JS integration)
col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    if st.button("🏠 Home", key="nav_home"):
        st.session_state.current_page = 'home'
        st.rerun()
with col2:
    if st.button("📅 Book", key="nav_book"):
        st.session_state.current_page = 'booking'
        st.rerun()
with col3:
    if st.button("🧠 Symptoms", key="nav_symptoms"):
        st.session_state.current_page = 'symptoms'
        st.rerun()
with col4:
    if st.button("👤 Portal", key="nav_portal"):
        st.session_state.current_page = 'portal'
        st.rerun()
with col5:
    if st.button("🔐 Admin", key="nav_admin"):
        st.session_state.current_page = 'admin'
        st.rerun()

st.markdown('<div class="content">', unsafe_allow_html=True)

# Initialize session state for admin
if 'admin_authenticated' not in st.session_state:
    st.session_state.admin_authenticated = False

# Navigation menu with modern icons
st.markdown("""
<div style="background: white; padding: 1rem 2rem; border-radius: 16px; box-shadow: 0 4px 20px rgba(0,0,0,0.08); margin: 2rem 0;">
    <h3 style="color: #667eea; margin: 0; font-size: 1.2rem; font-weight: 700;">📍 Navigate</h3>
</div>
""", unsafe_allow_html=True)

menu_options = [
    "🏠 Home", 
    "� Book Appointment", 
    "� Symptom Checker", 
    "👤 Patient Portal",
    "🔐 Admin Dashboard"
]

selected_menu = st.selectbox("Go to:", menu_options, label_visibility="collapsed")

# Route to different pages using modern navigation
current_page = st.session_state.current_page

if current_page == "home":
    # Modern Hero Section
    st.markdown("""
    <div class="hero-section fade-in">
        <div class="hero-content">
            <h1>Welcome to MediCare Plus</h1>
            <p>Your trusted healthcare partner providing world-class medical services with cutting-edge technology</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Hero Section with Stats
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">👥</div>
            <h2 style="color: #667eea; margin: 0; font-size: 2rem; font-weight: 800;">5000+</h2>
            <p style="color: #666; margin: 0.5rem 0 0 0; font-size: 0.9rem;">Happy Patients</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">⭐</div>
            <h2 style="color: #667eea; margin: 0; font-size: 2rem; font-weight: 800;">4.9/5</h2>
            <p style="color: #666; margin: 0.5rem 0 0 0; font-size: 0.9rem;">Average Rating</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">👨‍⚕️</div>
            <h2 style="color: #667eea; margin: 0; font-size: 2rem; font-weight: 800;">50+</h2>
            <p style="color: #666; margin: 0.5rem 0 0 0; font-size: 0.9rem;">Expert Doctors</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-card">
            <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">🏥</div>
            <h2 style="color: #667eea; margin: 0; font-size: 2rem; font-weight: 800;">24/7</h2>
            <p style="color: #666; margin: 0.5rem 0 0 0; font-size: 0.9rem;">Support Available</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("""
        <div class="step-card">
            <h2 style="color: #1a1a1a; font-weight: 700; font-size: 2rem; margin-bottom: 1.5rem;">
                Welcome to MediCare 💙
            </h2>
            <p style="font-size: 1.1rem; color: #555; line-height: 1.8; margin-bottom: 2rem;">
                Your trusted healthcare partner providing world-class medical services. 
                Book appointments, get AI-powered symptom analysis, and manage your health records all in one place.
            </p>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div style="background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); padding: 2rem; border-radius: 16px; margin: 1.5rem 0;">
            <h3 style="color: #667eea; font-weight: 700; margin-bottom: 1.5rem;">🎯 Our Services</h3>
            <div style="display: grid; gap: 1rem;">
                <div style="display: flex; align-items: start; gap: 1rem;">
                    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                                width: 40px; height: 40px; border-radius: 10px; display: flex; 
                                align-items: center; justify-content: center; color: white; font-size: 1.2rem; flex-shrink: 0;">
                        📅
                    </div>
                    <div>
                        <h4 style="margin: 0; color: #1a1a1a; font-weight: 600;">Online Appointment Booking</h4>
                        <p style="margin: 0.5rem 0 0 0; color: #666; font-size: 0.95rem;">
                            Schedule appointments with specialists instantly
                        </p>
                    </div>
                </div>
                
                <div style="display: flex; align-items: start; gap: 1rem;">
                    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                                width: 40px; height: 40px; border-radius: 10px; display: flex; 
                                align-items: center; justify-content: center; color: white; font-size: 1.2rem; flex-shrink: 0;">
                        🤖
                    </div>
                    <div>
                        <h4 style="margin: 0; color: #1a1a1a; font-weight: 600;">AI Symptom Checker</h4>
                        <p style="margin: 0.5rem 0 0 0; color: #666; font-size: 0.95rem;">
                            Get preliminary health assessments powered by AI
                        </p>
                    </div>
                </div>
                
                <div style="display: flex; align-items: start; gap: 1rem;">
                    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                                width: 40px; height: 40px; border-radius: 10px; display: flex; 
                                align-items: center; justify-content: center; color: white; font-size: 1.2rem; flex-shrink: 0;">
                        �
                    </div>
                    <div>
                        <h4 style="margin: 0; color: #1a1a1a; font-weight: 600;">Patient Portal</h4>
                        <p style="margin: 0.5rem 0 0 0; color: #666; font-size: 0.95rem;">
                            Access your medical records and appointment history
                        </p>
                    </div>
                </div>
                
                <div style="display: flex; align-items: start; gap: 1rem;">
                    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                                width: 40px; height: 40px; border-radius: 10px; display: flex; 
                                align-items: center; justify-content: center; color: white; font-size: 1.2rem; flex-shrink: 0;">
                        🔒
                    </div>
                    <div>
                        <h4 style="margin: 0; color: #1a1a1a; font-weight: 600;">Secure & Confidential</h4>
                        <p style="margin: 0.5rem 0 0 0; color: #666; font-size: 0.95rem;">
                            Your health data is protected with enterprise-grade security
                        </p>
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("### Quick Actions")
        col_a, col_b, col_c = st.columns(3)

        with col_a:
            if st.button("� Book Appointment",
                         type="primary",
                         key="home_book",
                         use_container_width=True):
                st.session_state.selected_menu_override = "� Book Appointment"
                st.rerun()

        with col_b:
            if st.button("� Check Symptoms", key="home_symptoms", use_container_width=True):
                st.session_state.selected_menu_override = "� Symptom Checker"
                st.rerun()

        with col_c:
            if st.button("👤 View Records", key="home_records", use_container_width=True):
                st.session_state.selected_menu_override = "👤 Patient Portal"
                st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="info-card success-card">
            <h3 style="color: #155724; margin: 0 0 1rem 0; font-weight: 700;">💡 Health Tips</h3>
            <ul style="margin: 0; padding-left: 1.5rem; color: #155724;">
                <li style="margin: 0.8rem 0;">Exercise 30 minutes daily</li>
                <li style="margin: 0.8rem 0;">Stay hydrated - 8 glasses/day</li>
                <li style="margin: 0.8rem 0;">Get 7-8 hours of sleep</li>
                <li style="margin: 0.8rem 0;">Annual health check-ups</li>
                <li style="margin: 0.8rem 0;">Follow prescribed medications</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("### System Status")

        try:
            total_patients = len(patients_df)
            available_doctors = len(schedule_df["doctor"].unique())
            available_slots = len(
                schedule_df[schedule_df["status"] == "Available"])

            st.markdown(f"""
            <div class="doctor-card">
                <div style="text-align: center;">
                    <h3 style="color: #667eea; margin: 0 0 1rem 0;">📊 Live Stats</h3>
                    <div style="margin: 1rem 0;">
                        <div style="font-size: 2rem; font-weight: 800; color: #1a1a1a;">{total_patients}</div>
                        <div style="color: #666; font-size: 0.9rem;">Registered Patients</div>
                    </div>
                    <div style="margin: 1rem 0;">
                        <div style="font-size: 2rem; font-weight: 800; color: #1a1a1a;">{available_doctors}</div>
                        <div style="color: #666; font-size: 0.9rem;">Available Doctors</div>
                    </div>
                    <div style="margin: 1rem 0;">
                        <div style="font-size: 2rem; font-weight: 800; color: #28a745;">{available_slots}</div>
                        <div style="color: #666; font-size: 0.9rem;">Open Appointment Slots</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        except Exception as e:
            st.error(f"Error loading metrics: {str(e)}")

    st.markdown('</div>', unsafe_allow_html=True)

elif selected_menu == "� Symptom Checker":
    st.markdown("## AI-Powered Symptom Checker")

    st.markdown("""
    <div class="symptom-card">
        <h4>Important Disclaimer</h4>
        <p>This symptom checker is for informational purposes only and should not replace professional medical advice.</p>
    </div>
    """,
                unsafe_allow_html=True)

    with st.form("symptom_checker_form"):
        st.markdown("### Describe your symptoms:")

        symptoms_text = st.text_area(
            "Please describe your current symptoms in detail:",
            placeholder=
            "e.g., I have a severe headache, fever, and nausea that started yesterday...",
            height=150)

        col1, col2 = st.columns(2)

        with col1:
            pain_scale = st.slider("Pain Level (1-10):", 1, 10, 5)
            duration = st.selectbox("Symptom Duration:", [
                "Less than 1 hour", "1-6 hours", "6-24 hours", "1-3 days",
                "More than 3 days"
            ])

        with col2:
            has_fever = st.checkbox("Do you have a fever?")
            difficulty_breathing = st.checkbox("Difficulty breathing?")
            severe_pain = st.checkbox("Severe pain?")

        submitted = st.form_submit_button("Analyze Symptoms", type="primary")

        if submitted and symptoms_text:
            additional_symptoms = []
            if has_fever:
                additional_symptoms.append("fever")
            if difficulty_breathing:
                additional_symptoms.append("difficulty breathing")
            if severe_pain:
                additional_symptoms.append("severe pain")

            full_symptoms = symptoms_text + " " + " ".join(additional_symptoms)

            st.markdown("### AI Symptom Analysis")
            ai_result = ai_symptom_checker(full_symptoms)
            st.markdown(ai_result)

elif selected_menu == "👤 Patient Portal":
    patient_portal()

elif selected_menu == "🔐 Admin Dashboard":
    if not st.session_state.admin_authenticated:
        admin_login()
    else:
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "Dashboard Overview", "Appointment Management", "Doctor Schedule",
            "Patient Management", "Analytics & Reports"
        ])

        with tab1:
            dashboard_overview()

        with tab2:
            appointment_management()

        with tab3:
            doctor_schedule_management()

        with tab4:
            patient_management()

        with tab5:
            analytics_reports()

        st.markdown("---")
        if st.button("Logout", type="secondary"):
            st.session_state.admin_authenticated = False
            st.rerun()

else:  # Book Appointment
    if st.session_state.get('selected_menu_override') == "📋 Book Appointment":
        st.session_state.pop('selected_menu_override', None)

    if 'step' not in st.session_state:
        st.session_state.step = 1
    if 'patient_data' not in st.session_state:
        st.session_state.patient_data = {}

    progress_steps = [{
        "title": "Patient Information",
        "icon": "👤"
    }, {
        "title": "Doctor & Schedule",
        "icon": "👨‍⚕️"
    }, {
        "title": "Insurance Details",
        "icon": "💳"
    }, {
        "title": "Confirmation",
        "icon": "✅"
    }, {
        "title": "Complete",
        "icon": "🎉"
    }]

    current_step = st.session_state.step
    progress_value = (current_step - 1) / (len(progress_steps) - 1)

    st.markdown('<div class="progress-container">', unsafe_allow_html=True)
    st.progress(progress_value)

    cols = st.columns(len(progress_steps))
    for i, (col, step) in enumerate(zip(cols, progress_steps)):
        with col:
            if i + 1 <= current_step:
                status_color = "#28a745" if i + 1 < current_step else "#667eea"
                st.markdown(f"""
                <div style="text-align: center; margin: 1rem 0;">
                    <div style="width: 40px; height: 40px; background: {status_color}; 
                               border-radius: 50%; display: flex; align-items: center; 
                               justify-content: center; color: white; font-size: 1.2rem; 
                               font-weight: bold; margin: 0 auto 0.5rem auto;">
                        {step["icon"]}
                    </div>
                    <div style="font-size: 0.8rem; font-weight: 500; color: {status_color};">
                        {step["title"]}
                    </div>
                </div>
                """,
                            unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="text-align: center; margin: 1rem 0;">
                    <div style="width: 40px; height: 40px; background: #e9ecef; 
                               border-radius: 50%; display: flex; align-items: center; 
                               justify-content: center; color: #6c757d; font-size: 1.2rem; 
                               margin: 0 auto 0.5rem auto;">
                        {step["icon"]}
                    </div>
                    <div style="font-size: 0.8rem; color: #6c757d;">
                        {step["title"]}
                    </div>
                </div>
                """,
                            unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # Step 1: Patient Information
    if st.session_state.step == 1:
        st.markdown("""
        <div class="step-card">
            <div class="step-header">
                <div class="step-icon">1</div>
                <h2 class="step-title">Welcome! Let's start with your information</h2>
            </div>
        """,
                    unsafe_allow_html=True)

        col1, col2 = st.columns([2, 1])

        with col1:
            with st.form("patient_info_form", clear_on_submit=False):
                st.markdown("### Patient Details")

                name = st.text_input("Full Name",
                                     placeholder="Enter your complete name")
                dob = st.text_input("Date of Birth", placeholder="DD-MM-YYYY")
                email = st.text_input("Email Address",
                                      placeholder="your.email@example.com")

                submitted = st.form_submit_button(
                    "Continue to Doctor Selection", type="primary")

                if submitted:
                    if name and dob and email:
                        if "@" not in email or "." not in email:
                            st.error("Please enter a valid email address")
                        else:
                            st.session_state.patient_data.update({
                                'name': name,
                                'dob': dob,
                                'email': email
                            })

                            try:
                                patients_df_fresh = pd.read_csv("patients.csv")
                                patients_df_fresh = patients_df_fresh.dropna(
                                    subset=[
                                        'first_name', 'last_name', 'email'
                                    ])

                                normalized_input_name = normalize_name(name)
                                normalized_input_dob = normalize_dob(dob)
                                normalized_input_email = email.strip().lower()

                                matches = []
                                for idx, row in patients_df_fresh.iterrows():
                                    patient_full_name = f"{str(row['first_name']).strip()} {str(row['last_name']).strip()}"
                                    patient_normalized_name = normalize_name(
                                        patient_full_name)
                                    patient_normalized_dob = normalize_dob(
                                        str(row['dob']))
                                    patient_normalized_email = str(
                                        row['email']).strip().lower()

                                    if (patient_normalized_name
                                            == normalized_input_name
                                            and patient_normalized_dob
                                            == normalized_input_dob
                                            and patient_normalized_email
                                            == normalized_input_email):
                                        matches.append(row)
                                        break

                                if matches:
                                    match = matches[0]
                                    st.session_state.patient_data[
                                        'visit_type'] = "Returning"
                                    st.session_state.patient_data[
                                        'doctor'] = match["doctor"]
                                    st.success(
                                        f"Welcome back, {name}! Your assigned doctor: **{match['doctor']}**"
                                    )
                                else:
                                    st.session_state.patient_data[
                                        'visit_type'] = "New"
                                    st.session_state.patient_data[
                                        'doctor'] = None
                                    st.info(
                                        f"Welcome to MediCare, {name}! You're registering as a new patient."
                                    )

                            except Exception as e:
                                st.error(
                                    f"Error checking patient status: {str(e)}")
                                st.session_state.patient_data[
                                    'visit_type'] = "New"
                                st.session_state.patient_data['doctor'] = None

                            st.session_state.step = 2
                            st.rerun()
                    else:
                        st.error("Please fill in all required fields")

        with col2:
            st.markdown("""
            <div class="info-card">
                <h4>Privacy Matters</h4>
                <p>Your information is secure and protected according to healthcare privacy standards.</p>
            </div>
            """,
                        unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

    # Step 2: Doctor Selection and Scheduling
    elif st.session_state.step == 2:
        st.markdown("""
        <div class="step-card">
            <div class="step-header">
                <div class="step-icon">2</div>
                <h2 class="step-title">Choose Your Doctor & Appointment Time</h2>
            </div>
        """,
                    unsafe_allow_html=True)

        col1, col2 = st.columns([1, 1])

        with col1:
            st.markdown("### Select Your Doctor")
            doctors = schedule_df["doctor"].unique().tolist()

            if st.session_state.patient_data.get('doctor'):
                try:
                    default_doctor_idx = doctors.index(
                        st.session_state.patient_data['doctor'])
                except ValueError:
                    default_doctor_idx = 0
            else:
                default_doctor_idx = 0

            selected_doctor = st.selectbox("Available Doctors",
                                           doctors,
                                           index=default_doctor_idx)

            doctor_slots = len(
                schedule_df[(schedule_df["doctor"] == selected_doctor)
                            & (schedule_df["status"] == "Available")])

            st.markdown(f"""
            <div class="info-card success-card">
                <h4>Dr. {selected_doctor}</h4>
                <p><strong>{doctor_slots}</strong> available appointment slots</p>
            </div>
            """,
                        unsafe_allow_html=True)

        with col2:
            st.markdown("### Available Time Slots")

            available_slots = schedule_df[
                (schedule_df["doctor"] == selected_doctor)
                & (schedule_df["status"] == "Available")].reset_index(
                    drop=True)

            if available_slots.empty:
                st.error(f"No available slots for Dr. {selected_doctor}")
                selected_slot = None
            else:
                slot_options = []
                for i, row in available_slots.head(10).iterrows():
                    slot_options.append(f"{row['date']} {row['time_slot']}")

                selected_slot_display = st.selectbox(
                    "Choose Your Preferred Time", slot_options)

                if selected_slot_display:
                    selected_slot_idx = slot_options.index(
                        selected_slot_display)
                    selected_slot = available_slots.iloc[selected_slot_idx]
                else:
                    selected_slot = None

        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("Book This Appointment",
                         type="primary",
                         key="book_btn"):
                if selected_slot is not None:
                    st.session_state.patient_data['doctor'] = selected_doctor
                    schedule_df_copy = schedule_df.copy()

                    idx = selected_slot.name
                    schedule_df_copy.at[idx, "status"] = "Booked"
                    slot_info = f"{selected_slot['date']} {selected_slot['time_slot']}"

                    schedule_df_copy.to_excel("doctor_schedule.xlsx",
                                              index=False)

                    st.session_state.patient_data['slot'] = slot_info
                    st.success(f"Appointment reserved: {slot_info}")
                    st.session_state.step = 3
                    st.rerun()
                else:
                    st.error("Please select a time slot")

        st.markdown('</div>', unsafe_allow_html=True)

    # Step 3: Insurance Information
    elif st.session_state.step == 3:
        st.markdown("""
        <div class="step-card">
            <div class="step-header">
                <div class="step-icon">3</div>
                <h2 class="step-title">Insurance Information</h2>
            </div>
        """,
                    unsafe_allow_html=True)

        col1, col2 = st.columns([2, 1])

        with col1:
            with st.form("insurance_form"):
                st.markdown("### Insurance Details")

                carrier = st.text_input(
                    "Insurance Carrier",
                    placeholder="e.g., Blue Cross Blue Shield")
                member_id = st.text_input(
                    "Member ID", placeholder="Your insurance member ID number")
                group = st.text_input(
                    "Group Number",
                    placeholder="Your group number (if applicable)")

                submitted = st.form_submit_button("Continue to Confirmation",
                                                  type="primary")

                if submitted:
                    insurance_data = {
                        "carrier": carrier if carrier else None,
                        "member_id": member_id if member_id else None,
                        "group": group if group else None
                    }
                    st.session_state.patient_data['insurance'] = insurance_data
                    st.session_state.step = 4
                    st.rerun()

        with col2:
            st.markdown("""
            <div class="info-card">
                <h4>Insurance Tips</h4>
                <ul>
                    <li>Have your insurance card ready</li>
                    <li>Double-check member ID</li>
                    <li>Group number is optional</li>
                </ul>
            </div>
            """,
                        unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

    # Step 4: Confirmation
    elif st.session_state.step == 4:
        st.markdown(f"""
        <div class="step-card">
            <div class="step-header">
                <div class="step-icon">4</div>
                <h2 class="step-title">Confirm Your Appointment</h2>
            </div>
        """,
                    unsafe_allow_html=True)

        # Display appointment summary in an attractive card layout
        col1, col2 = st.columns([1, 1])

        with col1:
            st.markdown("""
            <div style="background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); 
                        padding: 2rem; border-radius: 15px; margin: 1rem 0;">
                <h4 style="color: #495057; margin-bottom: 1.5rem;">👤 Patient Information</h4>
            """,
                        unsafe_allow_html=True)

            st.markdown(f"**Name:** {st.session_state.patient_data['name']}")
            st.markdown(
                f"**Date of Birth:** {st.session_state.patient_data['dob']}")
            st.markdown(
                f"**Visit Type:** {st.session_state.patient_data['visit_type']} Patient"
            )
            st.markdown(f"**Email:** {st.session_state.patient_data['email']}")

            st.markdown("</div>", unsafe_allow_html=True)

        with col2:
            st.markdown("""
            <div style="background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%); 
                        padding: 2rem; border-radius: 15px; margin: 1rem 0;">
                <h4 style="color: #1565c0; margin-bottom: 1.5rem;">📅 Appointment Details</h4>
            """,
                        unsafe_allow_html=True)

            st.markdown(
                f"**Doctor:** Dr. {st.session_state.patient_data['doctor']}")
            st.markdown(
                f"**Date & Time:** {st.session_state.patient_data['slot']}")

            insurance = st.session_state.patient_data.get('insurance', {})
            if insurance and (insurance.get('carrier')
                              or insurance.get('member_id')):
                st.markdown(
                    f"**Insurance:** {insurance.get('carrier', 'N/A')}")
                st.markdown(
                    f"**Member ID:** {insurance.get('member_id', 'N/A')}")
            else:
                st.markdown("**Insurance:** Self-Pay")

            st.markdown("</div>", unsafe_allow_html=True)

        # Important notes
        st.markdown("""
        <div class="info-card warning-card">
            <h4>📋 Important Reminders</h4>
            <ul>
                <li>Arrive 15 minutes before your appointment</li>
                <li>Bring a valid photo ID and insurance card</li>
                <li>Cancel at least 24 hours in advance if needed</li>
                <li>New patients will receive intake forms via email</li>
            </ul>
        </div>
        """,
                    unsafe_allow_html=True)

        # Confirmation buttons
        col1, col2, col3 = st.columns([1, 1, 1])

        with col1:
            if st.button("❌ Cancel Appointment", key="cancel_btn"):
                st.session_state.patient_data['confirmed'] = False
                st.error("Appointment cancelled.")
                if st.button("🔄 Start Over"):
                    for key in st.session_state.keys():
                        del st.session_state[key]
                    st.rerun()

        with col2:
            if st.button("✏️ Edit Details", key="edit_btn"):
                st.session_state.step = 1
                st.rerun()

        with col3:
            if st.button("✅ Confirm Appointment",
                         type="primary",
                         key="confirm_btn"):
                # Save appointment
                email = st.session_state.patient_data["email"]
                insurance = st.session_state.patient_data.get('insurance', {})

                new_appt = pd.DataFrame([{
                    "name":
                    st.session_state.patient_data["name"],
                    "dob":
                    st.session_state.patient_data["dob"],
                    "visit_type":
                    st.session_state.patient_data["visit_type"],
                    "doctor":
                    st.session_state.patient_data["doctor"],
                    "slot":
                    st.session_state.patient_data["slot"],
                    "insurance_carrier":
                    insurance.get("carrier"),
                    "insurance_member_id":
                    insurance.get("member_id"),
                    "insurance_group":
                    insurance.get("group"),
                    "email":
                    email
                }])

                try:
                    old_appts = pd.read_excel("appointments.xlsx")
                    all_appts = pd.concat([old_appts, new_appt],
                                          ignore_index=True)
                except FileNotFoundError:
                    all_appts = new_appt

                all_appts.to_excel("appointments.xlsx", index=False)

                # Add new patient to patients.csv
                if st.session_state.patient_data["visit_type"] == "New":
                    try:
                        name_parts = st.session_state.patient_data[
                            "name"].split()
                        first_name = name_parts[0]
                        last_name = " ".join(
                            name_parts[1:]) if len(name_parts) > 1 else ""

                        new_patient = pd.DataFrame([{
                            "patient_id":
                            "",  # Will be auto-assigned
                            "first_name":
                            first_name,
                            "last_name":
                            last_name,
                            "dob":
                            st.session_state.patient_data["dob"],
                            "email":
                            email,
                            "phone":
                            "",  # Empty for now
                            "insurance_carrier":
                            insurance.get("carrier", ""),
                            "insurance_member_id":
                            insurance.get("member_id", ""),
                            "insurance_group":
                            insurance.get("group", ""),
                            "doctor":
                            st.session_state.patient_data["doctor"],
                            "visit_type":
                            st.session_state.patient_data["visit_type"]
                        }])

                        # Load existing patients and append
                        try:
                            old_patients = pd.read_csv("patients.csv")
                            # Get next patient ID
                            max_id = old_patients['patient_id'].max(
                            ) if not old_patients.empty else 0
                            new_patient['patient_id'] = max_id + 1
                            updated_patients = pd.concat(
                                [old_patients, new_patient], ignore_index=True)
                        except FileNotFoundError:
                            new_patient['patient_id'] = 1
                            updated_patients = new_patient

                        updated_patients.to_csv("patients.csv", index=False)
                        st.success(
                            f"New patient record created with ID: {new_patient['patient_id'].iloc[0]}"
                        )

                    except Exception as e:
                        st.error(f"Error saving patient data: {str(e)}")

                st.session_state.patient_data['confirmed'] = True
                st.session_state.step = 5
                st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

    # Step 5: Complete
    elif st.session_state.step == 5:
        st.markdown(f"""
            <div class="step-card">
                <div class="step-header">
                    <div class="step-icon">🎉</div>
                    <h2 class="step-title">Appointment Confirmed Successfully!</h2>
                </div>
            """,
                    unsafe_allow_html=True)

        # Success animation effect
        st.balloons()

        # Confirmation details in attractive cards
        col1, col2 = st.columns([1, 1])

        with col1:
            st.markdown("""
                <div style="background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%); 
                            padding: 2rem; border-radius: 15px; border-left: 5px solid #28a745;">
                    <h4 style="color: #155724;">📅 Your Appointment</h4>
                """,
                        unsafe_allow_html=True)

            st.markdown(
                f"**Patient:** {st.session_state.patient_data['name']}")
            st.markdown(
                f"**Doctor:** Dr. {st.session_state.patient_data['doctor']}")
            st.markdown(
                f"**Date & Time:** {st.session_state.patient_data['slot']}")
            st.markdown(
                f"**Type:** {st.session_state.patient_data['visit_type']} Patient"
            )
            st.markdown(f"**Email:** {st.session_state.patient_data['email']}")

            st.markdown("</div>", unsafe_allow_html=True)

        with col2:
            st.markdown("""
                <div style="background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%); 
                            padding: 2rem; border-radius: 15px; border-left: 5px solid #ffc107;">
                    <h4 style="color: #856404;">📋 Next Steps</h4>
                    <div style="margin: 1rem 0;">
                        <p>✅ Appointment saved to system</p>
                        <p>📧 Confirmation email ready to send</p>
                        <p>📋 New patients will receive intake forms</p>
                        <p>📞 Contact us: +91-XXXXXXXXXX</p>
                    </div>
                </div>
                """,
                        unsafe_allow_html=True)

        # Special note for new patients
        if st.session_state.patient_data['visit_type'] == "New":
            st.markdown("""
                <div class="info-card warning-card">
                    <h4>📋 New Patient Information</h4>
                    <p><strong>Important:</strong> Please complete the New Patient Intake Form that will be attached to your confirmation email. This helps us provide better care during your visit.</p>
                </div>
                """,
                        unsafe_allow_html=True)

        # Email sending section
        st.markdown("---")
        st.markdown("### 📧 Send Confirmation Email")

        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("📧 Send Confirmation Email",
                         type="primary",
                         key="send_email"):
                try:
                    # Email sending logic
                    sender_email = "bharathreddyn6@gmail.com"
                    sender_password = "zjjn uqcb cobd qhih"
                    recipient_email = st.session_state.patient_data['email']

                    if not sender_email or not sender_password:
                        st.error(
                            "❌ Email credentials not configured. Please configure GMAIL_EMAIL and GMAIL_APP_PASSWORD."
                        )

                        with st.expander("How to configure email credentials"):
                            st.markdown(
                                """
                                **Recommended (create a `.env` file in the project folder):**

                                1. Create a file named `.env` in the same folder where you run the app.
                                2. Add the following lines (replace placeholders):

                                GMAIL_EMAIL=your.email@gmail.com
                                GMAIL_APP_PASSWORD=your_app_password
                                (Optional) SMTP_DEBUG=1

                                3. Restart the Streamlit app.

                                **Or (temporary, current PowerShell session only):**

                                ```powershell
                                $env:GMAIL_EMAIL = 'your.email@gmail.com'
                                $env:GMAIL_APP_PASSWORD = 'your_app_password'
                                $env:SMTP_DEBUG = '1'  # optional
                                streamlit run d:\chatbot\hospitalmanagement.py
                                ```

                                **Notes:** For Gmail use an App Password (recommended). See Google Account -> Security -> App passwords.
                                """
                            )
                    else:
                        # Create professional email
                        subject = "🏥 Your Appointment Confirmation - MediCare"
                        body = f"""
    Dear {st.session_state.patient_data['name']},

    Thank you for choosing MediCare! We are pleased to confirm your medical appointment.

    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
     🏥 APPOINTMENT CONFIRMATION
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    👨‍⚕️ Doctor       : Dr. {st.session_state.patient_data['doctor']}
    📅 Date & Time  : {st.session_state.patient_data['slot']}
    🔄 Visit Type   : {st.session_state.patient_data['visit_type']} Patient
    📧 Email        : {recipient_email}

    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
     📋 IMPORTANT INFORMATION
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    • Please arrive 15 minutes prior to your appointment
    • Bring a valid photo ID and your insurance card
    • If you need to cancel or reschedule, please contact our office at least 24 hours in advance
    • For new patients: Please complete the attached intake form before your visit

    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    Thank you for choosing MediCare. We look forward to providing you with exceptional healthcare.

    Best regards,
    The MediCare Team

    📞 Contact: +91-XXXXXXXXXX
    🏥 Address: 123 Medical Street, Healthcare City
    🌐 Website: www.medicare.com
                            """

                        # Create multipart message
                        msg = MIMEMultipart()
                        msg["Subject"] = subject
                        msg["From"] = sender_email
                        msg["To"] = recipient_email

                        msg.attach(MIMEText(body, "plain"))

                        # Attach intake form for new patients
                        if st.session_state.patient_data[
                                'visit_type'] == "New":
                            try:
                                with open("New Patient Intake Form.pdf",
                                          "rb") as f:
                                    part = MIMEApplication(
                                        f.read(),
                                        Name="New Patient Intake Form.pdf")
                                    part[
                                        "Content-Disposition"] = 'attachment; filename="New Patient Intake Form.pdf"'
                                    msg.attach(part)
                            except FileNotFoundError:
                                st.warning(
                                    "⚠️ Intake form file not found - email sent without attachment"
                                )

                        # Send email with improved diagnostics
                        smtp_debug = os.getenv("SMTP_DEBUG", "0")
                        try:
                            with smtplib.SMTP("smtp.gmail.com", 587, timeout=30) as server:
                                # Optional debug output to server.log — controlled by SMTP_DEBUG env var
                                if smtp_debug == "1":
                                    server.set_debuglevel(1)

                                # Greet and start TLS
                                server.ehlo()
                                server.starttls()
                                server.ehlo()

                                # Attempt login
                                server.login(sender_email, sender_password)

                                # Send the message
                                server.send_message(msg)

                            st.success(
                                f"✅ Confirmation email sent successfully to {recipient_email}!"
                            )
                            st.info(
                                "📬 Please check your email (including spam folder) for the confirmation."
                            )

                        except smtplib.SMTPAuthenticationError as auth_err:
                            # Provide clearer guidance to the admin on common Gmail issues
                            st.error(
                                "❌ Email authentication failed. Please check the following:\n"
                                "1) Ensure the GMAIL_EMAIL and GMAIL_APP_PASSWORD environment variables are set correctly.\n"
                                "2) If using Gmail, create an App Password and use it as GMAIL_APP_PASSWORD (recommended).\n"
                                "3) If using regular account password, make sure 2-Step Verification is disabled (not recommended).\n"
                                "4) Verify there are no extra whitespace characters when copying the password.\n"
                                f"Error details: {auth_err}"
                            )
                        except smtplib.SMTPException as smtp_err:
                            st.error(f"❌ SMTP error occurred while sending email: {str(smtp_err)}")
                        except OSError as os_err:
                            st.error(f"❌ Network error while connecting to SMTP server: {str(os_err)}")

                except smtplib.SMTPAuthenticationError:
                    st.error(
                        "❌ Email authentication failed. Please check Gmail app password settings."
                    )
                except smtplib.SMTPException as e:
                    st.error(f"❌ SMTP error occurred: {str(e)}")
                except Exception as e:
                    st.error(f"❌ Failed to send email: {str(e)}")

        st.markdown("---")

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🔄 Book Another Appointment", key="book_another"):
            for key in st.session_state.keys():
                del st.session_state[key]
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)
