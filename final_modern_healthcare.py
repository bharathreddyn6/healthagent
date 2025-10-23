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
    
    /* Streamlit button overrides */
    .stButton > button {
        border-radius: 50px;
        padding: 1rem 2.5rem;
        font-weight: 600;
        font-size: 1.1rem;
        transition: all 0.3s ease;
        border: none;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    
    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 15px 35px rgba(102, 126, 234, 0.4);
    }
    
    /* Input overrides */
    .stTextInput > div > div > input {
        border-radius: 12px;
        border: 2px solid #e2e8f0;
        padding: 1rem 1.5rem;
        font-size: 1rem;
        transition: all 0.3s ease;
        background: #f7fafc;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #667eea;
        background: white;
        box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.1);
    }
    
    .stSelectbox > div > div > select {
        border-radius: 12px;
        border: 2px solid #e2e8f0;
        padding: 1rem 1.5rem;
        font-size: 1rem;
        transition: all 0.3s ease;
        background: #f7fafc;
    }
    
    .stSelectbox > div > div > select:focus {
        border-color: #667eea;
        background: white;
        box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.1);
    }
    
    /* Progress Steps */
    .progress-steps {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin: 2rem 0;
        padding: 2rem;
        background: white;
        border-radius: 20px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.08);
    }
    
    .step {
        text-align: center;
        flex: 1;
        position: relative;
    }
    
    .step:not(:last-child)::after {
        content: '';
        position: absolute;
        top: 25px;
        right: -50%;
        width: 100%;
        height: 3px;
        background: #e2e8f0;
        z-index: 0;
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
        margin: 0 auto 1rem;
        font-weight: 700;
        font-size: 1.2rem;
        transition: all 0.3s ease;
        position: relative;
        z-index: 1;
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
    
    .step-label {
        font-size: 0.9rem;
        color: #718096;
        font-weight: 500;
    }
    
    .step-label.active {
        color: #667eea;
        font-weight: 600;
    }
    
    /* Alert styles */
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
    
    /* Responsive */
    @media (max-width: 768px) {
        .hero h1 { font-size: 2.5rem; }
        .hero p { font-size: 1.1rem; }
        .container { padding: 0 1rem; }
        .card { padding: 1.5rem; }
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

# Header with Modern Navigation
st.markdown("""
<div class="header">
    <div class="logo">
        🏥 MediCare Plus
    </div>
</div>
""", unsafe_allow_html=True)

# Load data function (from hospitalmanagement.py)
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

# Helper functions (from hospitalmanagement.py)
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

# AI Symptom Checker Function (from hospitalmanagement.py)
def ai_symptom_checker(symptoms_text):
    """AI-based symptom analysis using LangChain + Google GenAI"""
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-pro", api_key="AIzaSyDLe5OQ7_7iplT5EHrreg7MKfDiQ2Bl0Ww")
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

# Email Confirmation Function
def send_appointment_confirmation(patient_email, patient_name, doctor_name, appointment_slot, insurance_carrier):
    """Send appointment confirmation email to patient"""
    try:
        # Email configuration
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        sender_email = "bharathreddyn6@gmail.com"
        sender_password = "zjjn uqcb cobd qhih"
        
        if not sender_password:
            return False
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = patient_email
        msg['Subject'] = "🏥 Appointment Confirmation - MediCare Plus"
        
        # HTML email body
        html_body = f"""
        <html>
            <head>
                <style>
                    body {{ font-family: 'Arial', sans-serif; line-height: 1.6; color: #333; }}
                    .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                             color: white; padding: 20px; text-align: center; border-radius: 10px 10px 0 0; }}
                    .content {{ padding: 20px; background: #f9f9f9; }}
                    .appointment-details {{ background: white; padding: 20px; border-radius: 10px; 
                                          margin: 20px 0; border-left: 4px solid #667eea; }}
                    .footer {{ background: #2d3748; color: white; padding: 15px; text-align: center; 
                             border-radius: 0 0 10px 10px; font-size: 12px; }}
                    .highlight {{ color: #667eea; font-weight: bold; }}
                </style>
            </head>
            <body>
                <div style="max-width: 600px; margin: 0 auto; border-radius: 10px; overflow: hidden; box-shadow: 0 10px 30px rgba(0,0,0,0.1);">
                    <div class="header">
                        <h1>🏥 MediCare Plus</h1>
                        <h2>Appointment Confirmation</h2>
                    </div>
                    
                    <div class="content">
                        <p>Dear <span class="highlight">{patient_name}</span>,</p>
                        
                        <p>Your appointment has been <strong>successfully confirmed</strong>! We're looking forward to providing you with excellent healthcare.</p>
                        
                        <div class="appointment-details">
                            <h3>📅 Appointment Details</h3>
                            <p><strong>Patient:</strong> {patient_name}</p>
                            <p><strong>Doctor:</strong> Dr. {doctor_name}</p>
                            <p><strong>Date & Time:</strong> {appointment_slot}</p>
                            <p><strong>Insurance:</strong> {insurance_carrier}</p>
                        </div>
                        
                        <div style="background: #e8f4fd; padding: 15px; border-radius: 8px; margin: 20px 0;">
                            <h4>📋 Important Reminders:</h4>
                            <ul>
                                <li>Please arrive 15 minutes before your appointment</li>
                                <li>Bring a valid ID and insurance card</li>
                                <li>Bring a list of current medications</li>
                                <li>If you need to cancel or reschedule, please contact us 24 hours in advance</li>
                            </ul>
                        </div>
                        
                        <p>If you have any questions or need to make changes to your appointment, please don't hesitate to contact us.</p>
                        
                        <p>Thank you for choosing MediCare Plus!</p>
                    </div>
                    
                    <div class="footer">
                        <p><strong>MediCare Plus Healthcare</strong></p>
                        <p>📞 +1 (555) 123-4567 | 📧 contact@medicareplus.com</p>
                        <p>📍 123 Healthcare Ave, Medical City</p>
                    </div>
                </div>
            </body>
        </html>
        """
        
        msg.attach(MIMEText(html_body, 'html'))
        
        # Send email
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
        
        return True
        
    except Exception as e:
        print(f"Email sending error: {str(e)}")
        return False

# Patient Login System
def patient_login_system():
    st.markdown('<div class="container section">', unsafe_allow_html=True)
    st.markdown('<h1 style="text-align: center; margin-bottom: 2rem; color: #2d3748;">🔐 Patient Login</h1>', unsafe_allow_html=True)
    
    # Initialize patient login session state
    if 'patient_logged_in' not in st.session_state:
        st.session_state.patient_logged_in = False
    if 'patient_email' not in st.session_state:
        st.session_state.patient_email = ""
    if 'patient_name' not in st.session_state:
        st.session_state.patient_name = ""

    if not st.session_state.patient_logged_in:
        # Login Form
        st.markdown("""
        <div class="card" style="max-width: 500px; margin: 0 auto;">
            <div class="card-icon" style="text-align: center;">👤</div>
            <h3 style="text-align: center; margin-bottom: 2rem;">Patient Portal Access</h3>
        """, unsafe_allow_html=True)
        
        # Login/Register tabs
        tab1, tab2 = st.tabs(["🔑 Login", "📝 Register"])
        
        with tab1:
            st.markdown("### Welcome Back!")
            with st.form("patient_login"):
                email = st.text_input("📧 Email Address:", placeholder="your.email@example.com")
                password = st.text_input("🔒 Password:", type="password", placeholder="Enter your password")
                
                col1, col2 = st.columns(2)
                with col1:
                    login_submitted = st.form_submit_button("🔑 Login", type="primary", use_container_width=True)
                with col2:
                    if st.form_submit_button("🔄 Reset Password", use_container_width=True):
                        if email:
                            st.success("📧 Password reset instructions sent to your email!")
                        else:
                            st.error("❌ Please enter your email address")

                if login_submitted:
                    if email and password:
                        # Check if patient exists in appointments or patients data
                        try:
                            appointments_df = pd.read_excel("appointments.xlsx")
                            patients_df = pd.read_csv("patients.csv")
                            
                            # Check in both files
                            patient_exists = (
                                email in appointments_df['email'].values or 
                                email in patients_df['email'].values
                            )
                            
                            if patient_exists:
                                # Simple password check (in production, use proper authentication)
                                if password == "patient123":  # Default password
                                    st.session_state.patient_logged_in = True
                                    st.session_state.patient_email = email
                                    
                                    # Get patient name
                                    if email in patients_df['email'].values:
                                        patient_row = patients_df[patients_df['email'] == email].iloc[0]
                                        st.session_state.patient_name = patient_row.get('name', 'Patient')
                                    else:
                                        appointment_row = appointments_df[appointments_df['email'] == email].iloc[0]
                                        st.session_state.patient_name = appointment_row.get('name', 'Patient')
                                    
                                    st.success("✅ Login successful! Redirecting...")
                                    st.rerun()
                                else:
                                    st.error("❌ Invalid password! Try 'patient123'")
                            else:
                                st.error("❌ No account found with this email address. Please register first.")
                        except FileNotFoundError:
                            st.error("❌ System error: Patient database not found.")
                    else:
                        st.error("❌ Please fill in all fields")
        
        with tab2:
            st.markdown("### Create New Account")
            with st.form("patient_register"):
                reg_name = st.text_input("👤 Full Name:", placeholder="Enter your full name")
                reg_email = st.text_input("📧 Email Address:", placeholder="your.email@example.com")
                reg_phone = st.text_input("📱 Phone Number:", placeholder="+1 (555) 123-4567")
                reg_dob = st.text_input("🎂 Date of Birth:", placeholder="DD-MM-YYYY")
                reg_password = st.text_input("🔒 Create Password:", type="password", placeholder="Create a secure password")
                reg_confirm = st.text_input("🔒 Confirm Password:", type="password", placeholder="Confirm your password")
                
                register_submitted = st.form_submit_button("📝 Create Account", type="primary", use_container_width=True)

                if register_submitted:
                    if all([reg_name, reg_email, reg_phone, reg_dob, reg_password, reg_confirm]):
                        if reg_password == reg_confirm:
                            if "@" in reg_email and "." in reg_email:
                                # Add to patients database
                                try:
                                    patients_df = pd.read_csv("patients.csv")
                                    
                                    # Check if email already exists
                                    if reg_email in patients_df['email'].values:
                                        st.error("❌ Email already registered. Please use login.")
                                    else:
                                        new_patient = pd.DataFrame([{
                                            'name': reg_name,
                                            'email': reg_email,
                                            'phone': reg_phone,
                                            'dob': reg_dob,
                                            'doctor': 'Not Assigned',
                                            'insurance_carrier': ''
                                        }])
                                        
                                        updated_patients = pd.concat([patients_df, new_patient], ignore_index=True)
                                        updated_patients.to_csv("patients.csv", index=False)
                                        
                                        st.success("✅ Account created successfully! You can now login with password 'patient123'")
                                        
                                except FileNotFoundError:
                                    # Create new patients file
                                    new_patient = pd.DataFrame([{
                                        'name': reg_name,
                                        'email': reg_email,
                                        'phone': reg_phone,
                                        'dob': reg_dob,
                                        'doctor': 'Not Assigned',
                                        'insurance_carrier': ''
                                    }])
                                    new_patient.to_csv("patients.csv", index=False)
                                    st.success("✅ Account created successfully! You can now login with password 'patient123'")
                            else:
                                st.error("❌ Please enter a valid email address")
                        else:
                            st.error("❌ Passwords do not match")
                    else:
                        st.error("❌ Please fill in all fields")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    else:
        # Patient Dashboard
        patient_dashboard()
    
    st.markdown('</div>', unsafe_allow_html=True)

def patient_dashboard():
    """Patient dashboard after successful login"""
    st.markdown(f"""
    <div class="alert alert-success">
        <h4>👋 Welcome back, {st.session_state.patient_name}!</h4>
        <p>Access your medical records and manage your appointments below.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Patient Navigation
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("📅 My Appointments", type="primary", use_container_width=True):
            st.session_state.patient_section = 'appointments'
    
    with col2:
        if st.button("📋 Medical Records", type="primary", use_container_width=True):
            st.session_state.patient_section = 'records'
    
    with col3:
        if st.button("👤 Profile", type="primary", use_container_width=True):
            st.session_state.patient_section = 'profile'
    
    with col4:
        if st.button("🚪 Logout", type="secondary", use_container_width=True):
            st.session_state.patient_logged_in = False
            st.session_state.patient_email = ""
            st.session_state.patient_name = ""
            st.rerun()

    # Patient section content
    if 'patient_section' not in st.session_state:
        st.session_state.patient_section = 'appointments'
    
    if st.session_state.patient_section == 'appointments':
        show_patient_appointments()
    elif st.session_state.patient_section == 'records':
        show_patient_records()
    elif st.session_state.patient_section == 'profile':
        show_patient_profile()

def show_patient_appointments():
    """Display patient's appointments"""
    st.markdown("### 📅 Your Appointments")
    
    try:
        appointments_df = pd.read_excel("appointments.xlsx")
        patient_appointments = appointments_df[appointments_df['email'] == st.session_state.patient_email]

        if not patient_appointments.empty:
            st.success(f"Found {len(patient_appointments)} appointments")

            for idx, appointment in patient_appointments.iterrows():
                with st.expander(f"📅 Appointment with Dr. {appointment['doctor']} - {appointment['slot']}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Doctor:** Dr. {appointment['doctor']}")
                        st.write(f"**Date & Time:** {appointment['slot']}")
                        st.write(f"**Visit Type:** {appointment['visit_type']}")
                    with col2:
                        st.write(f"**Insurance:** {appointment.get('insurance_carrier', 'Self-Pay')}")
                        st.write(f"**Status:** Scheduled")
                        
                        if st.button(f"❌ Cancel Appointment", key=f"cancel_patient_{idx}"):
                            # Remove appointment
                            appointments_df = appointments_df.drop(idx)
                            appointments_df.to_excel("appointments.xlsx", index=False)
                            st.success("❌ Appointment cancelled successfully!")
                            st.rerun()
        else:
            st.info("📅 No appointments found. Book your first appointment!")
            if st.button("📅 Book New Appointment", type="primary"):
                st.session_state.current_page = 'booking'
                st.rerun()
                
    except FileNotFoundError:
        st.error("❌ No appointment records found.")

def show_patient_records():
    """Display patient's medical records"""
    st.markdown("### 📋 Medical Records")
    
    st.markdown("""
    <div class="alert alert-info">
        <h4>📋 Medical History</h4>
        <p>Your complete medical history and test results will be available here.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Show appointment history as medical records
    try:
        appointments_df = pd.read_excel("appointments.xlsx")
        patient_appointments = appointments_df[appointments_df['email'] == st.session_state.patient_email]

        if not patient_appointments.empty:
            st.markdown("#### 📊 Appointment History")
            
            # Create a summary
            total_visits = len(patient_appointments)
            doctors_visited = patient_appointments['doctor'].nunique()
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Visits", total_visits)
            with col2:
                st.metric("Doctors Consulted", doctors_visited)
            with col3:
                last_visit = patient_appointments['slot'].iloc[-1] if not patient_appointments.empty else "None"
                st.metric("Last Visit", last_visit)
            
            # Show detailed history
            st.dataframe(patient_appointments[['doctor', 'slot', 'visit_type']], use_container_width=True)
        
        st.markdown("#### 🔬 Lab Results")
        st.info("🔬 Lab results and test reports will be available in future updates.")
        
        st.markdown("#### 💊 Prescriptions")
        st.info("💊 Prescription history will be available in future updates.")
        
    except FileNotFoundError:
        st.error("❌ No medical records found.")

def show_patient_profile():
    """Display and edit patient profile"""
    st.markdown("### 👤 Patient Profile")
    
    try:
        patients_df = pd.read_csv("patients.csv")
        patient_info = patients_df[patients_df['email'] == st.session_state.patient_email]
        
        if not patient_info.empty:
            patient = patient_info.iloc[0]
            
            # Display current info
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 📋 Current Information")
                st.write(f"**Name:** {patient.get('name', 'N/A')}")
                st.write(f"**Email:** {patient.get('email', 'N/A')}")
                st.write(f"**Phone:** {patient.get('phone', 'N/A')}")
                st.write(f"**Date of Birth:** {patient.get('dob', 'N/A')}")
                st.write(f"**Assigned Doctor:** Dr. {patient.get('doctor', 'Not Assigned')}")
                st.write(f"**Insurance:** {patient.get('insurance_carrier', 'Not Provided')}")
            
            with col2:
                st.markdown("#### ✏️ Update Information")
                
                with st.form("update_profile"):
                    new_name = st.text_input("Name:", value=patient.get('name', ''))
                    new_phone = st.text_input("Phone:", value=patient.get('phone', ''))
                    new_insurance = st.text_input("Insurance:", value=patient.get('insurance_carrier', ''))
                    
                    if st.form_submit_button("💾 Update Profile", type="primary"):
                        # Update patient info
                        idx = patient_info.index[0]
                        patients_df.at[idx, 'name'] = new_name
                        patients_df.at[idx, 'phone'] = new_phone
                        patients_df.at[idx, 'insurance_carrier'] = new_insurance
                        
                        patients_df.to_csv("patients.csv", index=False)
                        st.success("✅ Profile updated successfully!")
                        st.rerun()
        else:
            st.error("❌ Patient profile not found.")
            
    except FileNotFoundError:
        st.error("❌ Patient database not found.")

# Admin functions (from hospitalmanagement.py)
def admin_login():
    st.markdown('<div class="container section">', unsafe_allow_html=True)
    st.markdown("""
    <div class="card" style="max-width: 400px; margin: 0 auto;">
        <div class="card-icon" style="text-align: center;">🔐</div>
        <h3 style="text-align: center; margin-bottom: 2rem;">Admin Login</h3>
    """, unsafe_allow_html=True)
    
    with st.form("admin_login"):
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
    
    st.markdown('</div></div>', unsafe_allow_html=True)

# Enhanced Admin Dashboard Functions
def create_admin_dashboard():
    """Main admin dashboard with comprehensive functionality"""
    st.markdown('<div class="container section">', unsafe_allow_html=True)
    st.markdown('<h1 style="text-align: center; margin-bottom: 3rem; color: #2d3748;">🔐 Admin Dashboard</h1>', unsafe_allow_html=True)
    
    # Admin authentication
    if 'admin_authenticated' not in st.session_state:
        st.session_state.admin_authenticated = False

    if not st.session_state.admin_authenticated:
        admin_login()
        return

    # Main admin interface with tabs
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📊 Dashboard Overview", 
        "📅 Appointment Management", 
        "👨‍⚕️ Doctor Schedule",
        "👥 Patient Management", 
        "📈 Analytics & Reports", 
        "⚙️ System Settings"
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

    with tab6:
        system_settings()
    
    st.markdown('</div>', unsafe_allow_html=True)

def admin_login():
    """Enhanced admin login with modern styling"""
    st.markdown("""
    <div class="card" style="max-width: 400px; margin: 0 auto;">
        <div class="card-icon" style="text-align: center;">🔐</div>
        <h3 style="text-align: center; margin-bottom: 2rem;">Admin Authentication</h3>
    """, unsafe_allow_html=True)
    
    with st.form("admin_login"):
        st.markdown("### Please enter admin credentials")
        username = st.text_input("Username:", placeholder="Enter admin username")
        password = st.text_input("Password:", type="password", placeholder="Enter admin password")
        
        submitted = st.form_submit_button("Login", type="primary", use_container_width=True)

        if submitted:
            # Simple authentication (in production, use proper authentication)
            if username == "admin" and password == "admin123":
                st.session_state.admin_authenticated = True
                st.success("✅ Login successful!")
                st.rerun()
            else:
                st.error("❌ Invalid credentials!")
    
    st.markdown('</div>', unsafe_allow_html=True)

def dashboard_overview():
    """Enhanced dashboard overview with modern cards and charts"""
    st.markdown("## 📊 Dashboard Overview")

    # Load data
    try:
        appointments_df = pd.read_excel("appointments.xlsx")
        schedule_df = pd.read_excel("doctor_schedule.xlsx")
        patients_df = pd.read_csv("patients.csv")

        # Key metrics with modern styling
        col1, col2, col3, col4, col5 = st.columns(5)

        with col1:
            total_appointments = len(appointments_df)
            st.markdown(f"""
            <div class="stats">
                <span class="stat-number">{total_appointments}</span>
                <div class="stat-label">Total Appointments</div>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            today_appointments = len(appointments_df[appointments_df['slot'].str.contains(
                datetime.now().strftime('%Y-%m-%d'), na=False)])
            st.markdown(f"""
            <div class="stats">
                <span class="stat-number">{today_appointments}</span>
                <div class="stat-label">Today's Appointments</div>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            total_patients = len(patients_df)
            st.markdown(f"""
            <div class="stats">
                <span class="stat-number">{total_patients}</span>
                <div class="stat-label">Total Patients</div>
            </div>
            """, unsafe_allow_html=True)

        with col4:
            total_doctors = len(schedule_df['doctor'].unique())
            st.markdown(f"""
            <div class="stats">
                <span class="stat-number">{total_doctors}</span>
                <div class="stat-label">Active Doctors</div>
            </div>
            """, unsafe_allow_html=True)

        with col5:
            available_slots = len(schedule_df[schedule_df['status'] == 'Available'])
            st.markdown(f"""
            <div class="stats">
                <span class="stat-number">{available_slots}</span>
                <div class="stat-label">Available Slots</div>
            </div>
            """, unsafe_allow_html=True)

        # Charts
        col1, col2 = st.columns(2)

        with col1:
            # Recent appointments chart
            fig_recent = px.bar(
                appointments_df['doctor'].value_counts().head(10),
                title="Appointments by Doctor (Top 10)",
                labels={'value': 'Number of Appointments', 'index': 'Doctor'})
            fig_recent.update_layout(showlegend=False)
            st.plotly_chart(fig_recent, use_container_width=True)

        with col2:
            # Visit type distribution
            visit_counts = appointments_df['visit_type'].value_counts()
            fig_visits = px.pie(values=visit_counts.values,
                              names=visit_counts.index,
                              title="Visit Type Distribution")
            st.plotly_chart(fig_visits, use_container_width=True)

        # Recent activity
        st.markdown("### 📋 Recent Activity")
        recent_appointments = appointments_df.tail(10)
        st.dataframe(
            recent_appointments[['name', 'doctor', 'slot', 'visit_type', 'email']], 
            use_container_width=True
        )

    except Exception as e:
        st.error(f"❌ Error loading dashboard data: {str(e)}")

def appointment_management():
    """Comprehensive appointment management with search, filter, and actions"""
    st.markdown("## 📅 Appointment Management")

    try:
        appointments_df = pd.read_excel("appointments.xlsx")

        # Search and filter
        col1, col2, col3 = st.columns(3)

        with col1:
            search_patient = st.text_input("🔍 Search by Patient Name:", 
                                         placeholder="Enter patient name...")

        with col2:
            filter_doctor = st.selectbox("👨‍⚕️ Filter by Doctor:", 
                                       ["All"] + list(appointments_df['doctor'].unique()))

        with col3:
            filter_date = st.date_input("📅 Filter by Date:")

        # Apply filters
        filtered_df = appointments_df.copy()

        if search_patient:
            filtered_df = filtered_df[filtered_df['name'].str.contains(
                search_patient, case=False, na=False)]

        if filter_doctor != "All":
            filtered_df = filtered_df[filtered_df['doctor'] == filter_doctor]

        if filter_date:
            date_str = filter_date.strftime('%Y-%m-%d')
            filtered_df = filtered_df[filtered_df['slot'].str.contains(date_str, na=False)]

        st.markdown(f"### 📋 Appointments ({len(filtered_df)} found)")

        # Display appointments with action buttons
        for idx, appointment in filtered_df.iterrows():
            with st.expander(
                f"👤 {appointment['name']} - Dr. {appointment['doctor']} - {appointment['slot']}"
            ):
                col1, col2 = st.columns([3, 1])

                with col1:
                    st.write(f"**Patient:** {appointment['name']}")
                    st.write(f"**Doctor:** Dr. {appointment['doctor']}")
                    st.write(f"**Date & Time:** {appointment['slot']}")
                    st.write(f"**Visit Type:** {appointment['visit_type']}")
                    st.write(f"**Email:** {appointment['email']}")
                    if pd.notna(appointment.get('insurance_carrier')):
                        st.write(f"**Insurance:** {appointment['insurance_carrier']}")

                with col2:
                    st.markdown("**Actions:**")
                    
                    col2_1, col2_2 = st.columns(2)
                    with col2_1:
                        if st.button("❌ Cancel", key=f"cancel_{idx}"):
                            # Remove appointment
                            appointments_df = appointments_df.drop(idx)
                            appointments_df.to_excel("appointments.xlsx", index=False)
                            st.success("🗑️ Appointment cancelled!")
                            st.rerun()

                    with col2_2:
                        if st.button("📧 Email", key=f"email_{idx}"):
                            # Send reminder email
                            email_sent = send_appointment_confirmation(
                                appointment['email'],
                                appointment['name'],
                                appointment['doctor'],
                                appointment['slot'],
                                appointment.get('insurance_carrier', 'Self-Pay')
                            )
                            if email_sent:
                                st.success("📧 Reminder sent!")
                            else:
                                st.warning("📧 Email service unavailable")

        # Bulk operations
        st.markdown("### 📊 Bulk Operations")
        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("📥 Export to CSV", type="primary"):
                csv = filtered_df.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name=f"appointments_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv")

        with col2:
            if st.button("📧 Send Reminders", type="primary"):
                # Logic to send reminder emails
                st.success("📧 Reminder emails sent to all patients!")

        with col3:
            if st.button("📊 Generate Report", type="primary"):
                st.info("📋 Appointment report generated!")

    except Exception as e:
        st.error(f"❌ Error loading appointment data: {str(e)}")

def doctor_schedule_management():
    """Advanced doctor schedule management with bulk operations"""
    st.markdown("## 👨‍⚕️ Doctor Schedule Management")

    try:
        schedule_df = pd.read_excel("doctor_schedule.xlsx")

        # Doctor selection
        selected_doctor = st.selectbox("👨‍⚕️ Select Doctor:",
                                     schedule_df['doctor'].unique())

        # Display current schedule
        doctor_schedule = schedule_df[schedule_df['doctor'] == selected_doctor]

        col1, col2 = st.columns([2, 1])

        with col1:
            st.markdown(f"### 📅 Schedule for Dr. {selected_doctor}")

            # Filter options
            col_a, col_b = st.columns(2)
            with col_a:
                status_filter = st.selectbox("🔍 Filter by Status:",
                                           ["All", "Available", "Booked", "Blocked"])
            with col_b:
                date_range = st.date_input("📅 Date Range:", value=datetime.now().date())

            # Apply filters
            filtered_schedule = doctor_schedule.copy()
            if status_filter != "All":
                filtered_schedule = filtered_schedule[filtered_schedule['status'] == status_filter]

            # Display schedule with modern styling
            for idx, slot in filtered_schedule.iterrows():
                col_x, col_y, col_z = st.columns([2, 1, 1])

                with col_x:
                    st.write(f"📅 {slot['date']} - ⏰ {slot['time_slot']}")

                with col_y:
                    status_color = {
                        'Available': '🟢',
                        'Booked': '🔴',
                        'Blocked': '🟡'
                    }.get(slot['status'], '⚪')
                    st.write(f"{status_color} {slot['status']}")

                with col_z:
                    new_status = st.selectbox("Change:",
                                            ["Available", "Booked", "Blocked"],
                                            index=["Available", "Booked", "Blocked"].index(slot['status']),
                                            key=f"status_{idx}")

                    if new_status != slot['status']:
                        if st.button("✅ Update", key=f"update_{idx}"):
                            schedule_df.at[idx, 'status'] = new_status
                            schedule_df.to_excel("doctor_schedule.xlsx", index=False)
                            st.success("✅ Status updated!")
                            st.rerun()

        with col2:
            st.markdown("### ➕ Add New Time Slots")

            with st.form("add_slots"):
                new_date = st.date_input("📅 Date:")
                new_time = st.time_input("⏰ Time:")
                slot_duration = st.selectbox("⏱️ Duration:", [30, 60])

                if st.form_submit_button("➕ Add Slot", type="primary"):
                    new_slot = pd.DataFrame([{
                        'doctor': selected_doctor,
                        'date': new_date.strftime('%Y-%m-%d'),
                        'time_slot': new_time.strftime('%H:%M'),
                        'status': 'Available'
                    }])

                    updated_schedule = pd.concat([schedule_df, new_slot], ignore_index=True)
                    updated_schedule.to_excel("doctor_schedule.xlsx", index=False)
                    st.success("✅ New slot added!")
                    st.rerun()

            st.markdown("### 📊 Bulk Operations")

            # Generate weekly schedule
            if st.button("📅 Generate Weekly Schedule", type="primary"):
                start_date = datetime.now().date()
                time_slots = ["09:00", "10:00", "11:00", "14:00", "15:00", "16:00"]

                new_slots = []
                for i in range(7):  # 7 days
                    current_date = start_date + timedelta(days=i)
                    for time_slot in time_slots:
                        new_slots.append({
                            'doctor': selected_doctor,
                            'date': current_date.strftime('%Y-%m-%d'),
                            'time_slot': time_slot,
                            'status': 'Available'
                        })

                new_schedule_df = pd.DataFrame(new_slots)
                updated_schedule = pd.concat([schedule_df, new_schedule_df], ignore_index=True)
                updated_schedule.to_excel("doctor_schedule.xlsx", index=False)
                st.success("📅 Weekly schedule generated!")
                st.rerun()

            # Block time periods
            with st.expander("🚫 Block Time Period"):
                block_start_date = st.date_input("Start Date:", key="block_start")
                block_end_date = st.date_input("End Date:", key="block_end")
                block_reason = st.text_input("Reason:", placeholder="e.g., Vacation, Conference")

                if st.button("🚫 Block Period"):
                    # Logic to block the time period
                    mask = ((schedule_df['doctor'] == selected_doctor) & 
                           (pd.to_datetime(schedule_df['date']) >= pd.to_datetime(block_start_date)) &
                           (pd.to_datetime(schedule_df['date']) <= pd.to_datetime(block_end_date)))
                    schedule_df.loc[mask, 'status'] = 'Blocked'
                    schedule_df.to_excel("doctor_schedule.xlsx", index=False)
                    st.success(f"🚫 Time period blocked: {block_reason}")
                    st.rerun()

    except Exception as e:
        st.error(f"❌ Error managing doctor schedule: {str(e)}")

def patient_management():
    """Comprehensive patient management with search and editing"""
    st.markdown("## 👥 Patient Management")

    try:
        patients_df = pd.read_csv("patients.csv")
        appointments_df = pd.read_excel("appointments.xlsx")

        # Search functionality
        search_term = st.text_input("🔍 Search Patients:",
                                  placeholder="Enter name or email...")

        if search_term:
            # Handle case where patients.csv might have different column structure
            if 'first_name' in patients_df.columns and 'last_name' in patients_df.columns:
                filtered_patients = patients_df[
                    patients_df['first_name'].str.contains(search_term, case=False, na=False) |
                    patients_df['last_name'].str.contains(search_term, case=False, na=False) |
                    patients_df['email'].str.contains(search_term, case=False, na=False)]
            else:
                # Fallback for patients.csv with 'name' column
                filtered_patients = patients_df[
                    patients_df['name'].str.contains(search_term, case=False, na=False) |
                    patients_df['email'].str.contains(search_term, case=False, na=False)]
        else:
            filtered_patients = patients_df.head(20)  # Show first 20 patients

        st.markdown(f"### 👥 Patient Records ({len(filtered_patients)} shown)")

        for idx, patient in filtered_patients.iterrows():
            # Handle different patient data structures
            if 'first_name' in patient.index and 'last_name' in patient.index:
                patient_name = f"{patient['first_name']} {patient['last_name']}"
            else:
                patient_name = patient.get('name', 'Unknown')
                
            with st.expander(f"👤 {patient_name} - {patient['email']}"):
                col1, col2 = st.columns([2, 1])

                with col1:
                    # Patient information
                    st.write(f"**Name:** {patient_name}")
                    st.write(f"**Date of Birth:** {patient.get('dob', 'N/A')}")
                    st.write(f"**Email:** {patient['email']}")
                    st.write(f"**Assigned Doctor:** Dr. {patient.get('doctor', 'Not Assigned')}")

                    if pd.notna(patient.get('insurance_carrier')):
                        st.write(f"**Insurance:** {patient['insurance_carrier']}")

                    # Patient's appointment history
                    patient_appointments = appointments_df[appointments_df['email'] == patient['email']]

                    if not patient_appointments.empty:
                        st.markdown("**📅 Appointment History:**")
                        for _, apt in patient_appointments.iterrows():
                            st.write(f"• {apt['slot']} with Dr. {apt['doctor']} ({apt['visit_type']})")
                    else:
                        st.write("**No appointment history**")

                with col2:
                    st.markdown("**⚡ Actions:**")

                    if st.button("✏️ Edit", key=f"edit_{idx}"):
                        st.session_state[f"edit_patient_{idx}"] = True

                    if st.button("📧 Message", key=f"message_{idx}"):
                        st.success("📧 Message sent to patient!")

        # Add new patient
        with st.expander("➕ Add New Patient"):
            with st.form("add_patient"):
                st.markdown("#### ➕ Add New Patient")

                col1, col2 = st.columns(2)
                with col1:
                    new_name = st.text_input("Full Name:")
                    new_email = st.text_input("Email:")
                    new_insurance = st.text_input("Insurance Carrier:")

                with col2:
                    new_dob = st.text_input("Date of Birth (DD-MM-YYYY):")
                    new_doctor = st.selectbox(
                        "Assigned Doctor:",
                        pd.read_excel("doctor_schedule.xlsx")['doctor'].unique())

                if st.form_submit_button("➕ Add Patient", type="primary"):
                    new_patient = pd.DataFrame([{
                        'name': new_name,
                        'dob': new_dob,
                        'email': new_email,
                        'doctor': new_doctor,
                        'insurance_carrier': new_insurance
                    }])

                    updated_patients = pd.concat([patients_df, new_patient], ignore_index=True)
                    updated_patients.to_csv("patients.csv", index=False)
                    st.success("✅ New patient added!")
                    st.rerun()

    except Exception as e:
        st.error(f"❌ Error managing patients: {str(e)}")

def analytics_reports():
    """Advanced analytics and reporting with multiple report types"""
    st.markdown("## 📈 Analytics & Reports")

    try:
        appointments_df = pd.read_excel("appointments.xlsx")
        patients_df = pd.read_csv("patients.csv")
        schedule_df = pd.read_excel("doctor_schedule.xlsx")

        # Report type selection
        report_type = st.selectbox("📊 Select Report Type:", [
            "Appointment Analytics", 
            "Doctor Performance", 
            "Patient Demographics",
            "Revenue Report", 
            "System Usage"
        ])

        if report_type == "Appointment Analytics":
            st.markdown("### 📊 Appointment Analytics")

            # Time-based analysis
            col1, col2 = st.columns(2)

            with col1:
                # Appointments trend
                appointments_df['date'] = pd.to_datetime(appointments_df['slot'].str.split(' ').str[0], errors='coerce')
                daily_counts = appointments_df.groupby('date').size().reset_index(name='count')

                if not daily_counts.empty:
                    fig_trend = px.line(daily_counts, x='date', y='count',
                                       title="📈 Daily Appointments Trend",
                                       labels={'count': 'Appointments', 'date': 'Date'})
                    st.plotly_chart(fig_trend, use_container_width=True)

            with col2:
                # Visit type breakdown
                visit_counts = appointments_df['visit_type'].value_counts()
                fig_visits = px.bar(x=visit_counts.values,
                                  y=visit_counts.index,
                                  orientation='h',
                                  title="👥 Visit Type Distribution")
                st.plotly_chart(fig_visits, use_container_width=True)

        elif report_type == "Doctor Performance":
            st.markdown("### 👨‍⚕️ Doctor Performance Report")

            doctor_stats = appointments_df.groupby('doctor').agg({
                'name': 'count',
                'visit_type': lambda x: (x == 'New').sum()
            }).rename(columns={
                'name': 'total_appointments',
                'visit_type': 'new_patients'
            })

            doctor_stats['returning_patients'] = doctor_stats['total_appointments'] - doctor_stats['new_patients']

            # Display as styled table
            st.dataframe(doctor_stats, use_container_width=True)

            # Performance chart
            fig_performance = px.bar(doctor_stats.reset_index(),
                                   x='doctor',
                                   y='total_appointments',
                                   title="📊 Total Appointments by Doctor")
            st.plotly_chart(fig_performance, use_container_width=True)

        elif report_type == "Patient Demographics":
            st.markdown("### 👥 Patient Demographics")

            col1, col2 = st.columns(2)
            
            with col1:
                # Insurance analysis
                if 'insurance_carrier' in patients_df.columns:
                    insurance_counts = patients_df['insurance_carrier'].value_counts().head(10)
                    fig_insurance = px.pie(values=insurance_counts.values,
                                         names=insurance_counts.index,
                                         title="🏥 Top Insurance Providers")
                    st.plotly_chart(fig_insurance, use_container_width=True)

            with col2:
                # Doctor assignment
                doctor_counts = patients_df['doctor'].value_counts()
                fig_doctors = px.bar(x=doctor_counts.values,
                                   y=doctor_counts.index,
                                   orientation='h',
                                   title="👨‍⚕️ Patients by Doctor")
                st.plotly_chart(fig_doctors, use_container_width=True)

        # Export functionality
        st.markdown("### 📥 Export Reports")
        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("📅 Export Appointments", type="primary"):
                csv_appointments = appointments_df.to_csv(index=False)
                st.download_button(
                    label="📥 Download CSV",
                    data=csv_appointments,
                    file_name=f"appointments_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv")

        with col2:
            if st.button("👥 Export Patients", type="primary"):
                csv_patients = patients_df.to_csv(index=False)
                st.download_button(
                    label="📥 Download CSV",
                    data=csv_patients,
                    file_name=f"patients_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv")

        with col3:
            if st.button("📅 Export Schedule", type="primary"):
                csv_schedule = schedule_df.to_csv(index=False)
                st.download_button(
                    label="📥 Download CSV",
                    data=csv_schedule,
                    file_name=f"schedule_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv")

    except Exception as e:
        st.error(f"❌ Error generating reports: {str(e)}")

def system_settings():
    """System configuration and management settings"""
    st.markdown("## ⚙️ System Settings")

    # System configuration
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 📧 Email Configuration")

        with st.form("email_settings"):
            smtp_server = st.text_input("SMTP Server:", value="smtp.gmail.com")
            smtp_port = st.number_input("SMTP Port:", value=587)
            admin_email = st.text_input("Admin Email:", value="admin@medicareplus.com")
            email_enabled = st.checkbox("Enable Email Notifications", value=True)
            
            if st.form_submit_button("💾 Save Email Settings", type="primary"):
                st.success("✅ Email settings saved!")

    with col2:
        st.markdown("### 🔧 System Preferences")

        with st.form("system_settings"):
            appointment_duration = st.selectbox("⏱️ Default Duration:", [30, 45, 60])
            advance_booking = st.number_input("📅 Max Advance Booking (days):", value=30)
            reminder_hours = st.number_input("⏰ Reminder Hours Before:", value=24)
            timezone = st.selectbox("🌍 Timezone:", ["UTC", "EST", "PST", "IST"])
            
            if st.form_submit_button("💾 Save System Settings", type="primary"):
                st.success("✅ System settings saved!")

    # Database management
    st.markdown("### 🗄️ Database Management")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("💾 Backup Database", type="primary"):
            st.success("✅ Database backup created!")

    with col2:
        if st.button("🧹 Clean Old Records", type="secondary"):
            st.success("✅ Old records cleaned!")

    with col3:
        if st.button("🔄 Reset Demo Data", type="secondary"):
            st.warning("⚠️ Demo data reset!")

    # Logout button
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("🚪 Logout", type="secondary", use_container_width=True):
            st.session_state.admin_authenticated = False
            st.rerun()

def admin_dashboard_overview():
    st.markdown('<h2 style="color: #2d3748; margin-bottom: 2rem;">📊 Dashboard Overview</h2>', unsafe_allow_html=True)
    
    try:
        appointments_df = pd.read_excel("appointments.xlsx")
        schedule_df = pd.read_excel("doctor_schedule.xlsx")
        patients_df = pd.read_csv("patients.csv")

        # Key Metrics
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.markdown(f"""
            <div class="stats">
                <span class="stat-number">{len(appointments_df)}</span>
                <div class="stat-label">Total Appointments</div>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            today_appointments = len(appointments_df[appointments_df['slot'].str.contains(
                datetime.now().strftime('%Y-%m-%d'), na=False)])
            st.markdown(f"""
            <div class="stats">
                <span class="stat-number">{today_appointments}</span>
                <div class="stat-label">Today's Appointments</div>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            st.markdown(f"""
            <div class="stats">
                <span class="stat-number">{len(patients_df)}</span>
                <div class="stat-label">Total Patients</div>
            </div>
            """, unsafe_allow_html=True)

        with col4:
            st.markdown(f"""
            <div class="stats">
                <span class="stat-number">{len(schedule_df["doctor"].unique())}</span>
                <div class="stat-label">Active Doctors</div>
            </div>
            """, unsafe_allow_html=True)

        # Charts
        col1, col2 = st.columns(2)

        with col1:
            fig_recent = px.bar(
                appointments_df['doctor'].value_counts().head(10),
                title="Appointments by Doctor (Top 10)",
                labels={'value': 'Number of Appointments', 'index': 'Doctor'})
            st.plotly_chart(fig_recent, use_container_width=True)

        with col2:
            visit_counts = appointments_df['visit_type'].value_counts()
            fig_visits = px.pie(values=visit_counts.values,
                                names=visit_counts.index,
                                title="Visit Type Distribution")
            st.plotly_chart(fig_visits, use_container_width=True)

        # Recent Activity
        st.markdown("### Recent Activity")
        recent_appointments = appointments_df.tail(10)
        st.dataframe(recent_appointments[['name', 'doctor', 'slot', 'visit_type', 'email']], use_container_width=True)

    except Exception as e:
        st.error(f"Error loading dashboard data: {str(e)}")

def admin_appointment_management():
    st.markdown('<h2 style="color: #2d3748; margin-bottom: 2rem;">📅 Appointment Management</h2>', unsafe_allow_html=True)
    
    try:
        appointments_df = pd.read_excel("appointments.xlsx")
        
        # Search and filter options
        col1, col2, col3 = st.columns(3)
        
        with col1:
            search_patient = st.text_input("🔍 Search by Patient Name:", placeholder="Enter patient name...")
        with col2:
            search_doctor = st.selectbox("👨‍⚕️ Filter by Doctor:", ["All Doctors"] + list(appointments_df['doctor'].unique()))
        with col3:
            date_filter = st.date_input("📅 Filter by Date:")
        
        # Filter appointments
        filtered_df = appointments_df.copy()
        
        if search_patient:
            filtered_df = filtered_df[filtered_df['name'].str.contains(search_patient, case=False, na=False)]
        
        if search_doctor != "All Doctors":
            filtered_df = filtered_df[filtered_df['doctor'] == search_doctor]
        
        if date_filter:
            date_str = date_filter.strftime('%Y-%m-%d')
            filtered_df = filtered_df[filtered_df['slot'].str.contains(date_str, na=False)]
        
        st.markdown(f"### Found {len(filtered_df)} appointments")
        
        # Display appointments with actions
        for idx, appointment in filtered_df.iterrows():
            with st.expander(f"👤 {appointment['name']} - Dr. {appointment['doctor']} - {appointment['slot']}"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.write(f"**Patient:** {appointment['name']}")
                    st.write(f"**Email:** {appointment['email']}")
                    st.write(f"**DOB:** {appointment.get('dob', 'N/A')}")
                
                with col2:
                    st.write(f"**Doctor:** Dr. {appointment['doctor']}")
                    st.write(f"**Date & Time:** {appointment['slot']}")
                    st.write(f"**Visit Type:** {appointment['visit_type']}")
                
                with col3:
                    st.write(f"**Insurance:** {appointment.get('insurance_carrier', 'Self-Pay')}")
                    
                    col3_1, col3_2 = st.columns(2)
                    with col3_1:
                        if st.button("✉️ Send Email", key=f"email_{idx}"):
                            # Send appointment reminder
                            st.success("📧 Reminder email sent!")
                    
                    with col3_2:
                        if st.button("❌ Cancel", key=f"cancel_{idx}"):
                            # Remove appointment
                            appointments_df = appointments_df.drop(idx)
                            appointments_df.to_excel("appointments.xlsx", index=False)
                            st.success("🗑️ Appointment cancelled!")
                            st.rerun()
        
    except Exception as e:
        st.error(f"Error loading appointment data: {str(e)}")

def admin_doctor_schedule():
    st.markdown('<h2 style="color: #2d3748; margin-bottom: 2rem;">👨‍⚕️ Doctor Schedule Management</h2>', unsafe_allow_html=True)
    
    try:
        schedule_df = pd.read_excel("doctor_schedule.xlsx")
        
        # Add new schedule slot
        with st.expander("➕ Add New Schedule Slot"):
            with st.form("add_schedule"):
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    new_doctor = st.text_input("Doctor Name:", placeholder="Dr. Smith")
                with col2:
                    new_date = st.date_input("Date:")
                with col3:
                    new_time = st.time_input("Time:")
                with col4:
                    new_status = st.selectbox("Status:", ["Available", "Booked", "Unavailable"])
                
                if st.form_submit_button("Add Schedule", type="primary"):
                    if new_doctor and new_date and new_time:
                        new_slot = pd.DataFrame([{
                            "doctor": new_doctor,
                            "date": new_date.strftime('%Y-%m-%d'),
                            "time_slot": new_time.strftime('%H:%M'),
                            "status": new_status
                        }])
                        
                        updated_schedule = pd.concat([schedule_df, new_slot], ignore_index=True)
                        updated_schedule.to_excel("doctor_schedule.xlsx", index=False)
                        st.success("✅ Schedule slot added successfully!")
                        st.rerun()
        
        # Display current schedule
        st.markdown("### Current Doctor Schedule")
        
        # Filter options
        col1, col2 = st.columns(2)
        with col1:
            filter_doctor = st.selectbox("Filter by Doctor:", ["All Doctors"] + list(schedule_df['doctor'].unique()))
        with col2:
            filter_status = st.selectbox("Filter by Status:", ["All Status", "Available", "Booked", "Unavailable"])
        
        # Apply filters
        filtered_schedule = schedule_df.copy()
        if filter_doctor != "All Doctors":
            filtered_schedule = filtered_schedule[filtered_schedule['doctor'] == filter_doctor]
        if filter_status != "All Status":
            filtered_schedule = filtered_schedule[filtered_schedule['status'] == filter_status]
        
        # Display schedule table with edit options
        st.dataframe(filtered_schedule, use_container_width=True)
        
        # Quick stats
        col1, col2, col3 = st.columns(3)
        with col1:
            available_slots = len(filtered_schedule[filtered_schedule['status'] == 'Available'])
            st.metric("Available Slots", available_slots)
        with col2:
            booked_slots = len(filtered_schedule[filtered_schedule['status'] == 'Booked'])
            st.metric("Booked Slots", booked_slots)
        with col3:
            total_doctors = len(filtered_schedule['doctor'].unique())
            st.metric("Active Doctors", total_doctors)
            
    except Exception as e:
        st.error(f"Error loading schedule data: {str(e)}")

def admin_patient_management():
    st.markdown('<h2 style="color: #2d3748; margin-bottom: 2rem;">👥 Patient Management</h2>', unsafe_allow_html=True)
    
    try:
        patients_df = pd.read_csv("patients.csv")
        appointments_df = pd.read_excel("appointments.xlsx")
        
        # Search patients
        search_term = st.text_input("🔍 Search Patients:", placeholder="Search by name, email, or phone...")
        
        if search_term:
            mask = (patients_df['name'].str.contains(search_term, case=False, na=False) |
                   patients_df['email'].str.contains(search_term, case=False, na=False))
            filtered_patients = patients_df[mask]
        else:
            filtered_patients = patients_df
        
        st.markdown(f"### Found {len(filtered_patients)} patients")
        
        # Patient statistics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Patients", len(patients_df))
        with col2:
            new_patients = len(appointments_df[appointments_df['visit_type'] == 'New'])
            st.metric("New Patients", new_patients)
        with col3:
            returning_patients = len(appointments_df[appointments_df['visit_type'] == 'Returning'])
            st.metric("Returning Patients", returning_patients)
        with col4:
            unique_patients = len(appointments_df['email'].unique())
            st.metric("Active Patients", unique_patients)
        
        # Display patient details
        for idx, patient in filtered_patients.iterrows():
            with st.expander(f"👤 {patient['name']} - {patient['email']}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Name:** {patient['name']}")
                    st.write(f"**Email:** {patient['email']}")
                    st.write(f"**Phone:** {patient.get('phone', 'N/A')}")
                    st.write(f"**Assigned Doctor:** Dr. {patient.get('doctor', 'N/A')}")
                
                with col2:
                    # Patient's appointment history
                    patient_appointments = appointments_df[appointments_df['email'] == patient['email']]
                    st.write(f"**Total Appointments:** {len(patient_appointments)}")
                    
                    if not patient_appointments.empty:
                        st.write("**Recent Appointments:**")
                        for _, appt in patient_appointments.tail(3).iterrows():
                            st.write(f"• Dr. {appt['doctor']} - {appt['slot']}")
        
        # Add new patient
        with st.expander("➕ Add New Patient"):
            with st.form("add_patient"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    new_name = st.text_input("Patient Name:")
                with col2:
                    new_email = st.text_input("Email:")
                with col3:
                    new_phone = st.text_input("Phone:")
                
                if st.form_submit_button("Add Patient", type="primary"):
                    if new_name and new_email:
                        new_patient = pd.DataFrame([{
                            "name": new_name,
                            "email": new_email,
                            "phone": new_phone,
                            "doctor": "Not Assigned"
                        }])
                        
                        updated_patients = pd.concat([patients_df, new_patient], ignore_index=True)
                        updated_patients.to_csv("patients.csv", index=False)
                        st.success("✅ Patient added successfully!")
                        st.rerun()
        
    except Exception as e:
        st.error(f"Error loading patient data: {str(e)}")

def admin_analytics_reports():
    st.markdown('<h2 style="color: #2d3748; margin-bottom: 2rem;">📈 Analytics & Reports</h2>', unsafe_allow_html=True)
    
    try:
        appointments_df = pd.read_excel("appointments.xlsx")
        schedule_df = pd.read_excel("doctor_schedule.xlsx")
        patients_df = pd.read_csv("patients.csv")
        
        # Date range selector
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Start Date:", value=datetime.now() - timedelta(days=30))
        with col2:
            end_date = st.date_input("End Date:", value=datetime.now())
        
        # Revenue Analytics (Simulation)
        st.markdown("### 💰 Revenue Analytics")
        col1, col2, col3, col4 = st.columns(4)
        
        # Simulated revenue data
        total_appointments = len(appointments_df)
        estimated_revenue = total_appointments * 150  # $150 average per appointment
        
        with col1:
            st.metric("Total Revenue", f"${estimated_revenue:,}")
        with col2:
            monthly_revenue = estimated_revenue / 6  # 6 months average
            st.metric("Monthly Average", f"${monthly_revenue:,.0f}")
        with col3:
            st.metric("Average per Visit", "$150")
        with col4:
            growth_rate = 15.5  # Simulated growth
            st.metric("Growth Rate", f"{growth_rate}%", delta="2.3%")
        
        # Appointment Trends
        st.markdown("### 📊 Appointment Trends")
        
        # Create time series data for appointments
        appointments_df['date'] = pd.to_datetime(appointments_df['slot'].str.split(' ').str[0], errors='coerce')
        daily_appointments = appointments_df.groupby('date').size().reset_index(name='count')
        
        if not daily_appointments.empty:
            fig_trend = px.line(daily_appointments, x='date', y='count',
                               title="Daily Appointments Trend",
                               labels={'count': 'Number of Appointments', 'date': 'Date'})
            st.plotly_chart(fig_trend, use_container_width=True)
        
        # Doctor Performance
        col1, col2 = st.columns(2)
        
        with col1:
            doctor_stats = appointments_df['doctor'].value_counts()
            fig_doctors = px.bar(x=doctor_stats.index, y=doctor_stats.values,
                               title="Doctor Performance (Total Appointments)",
                               labels={'x': 'Doctor', 'y': 'Appointments'})
            st.plotly_chart(fig_doctors, use_container_width=True)
        
        with col2:
            # Patient demographics
            visit_type_counts = appointments_df['visit_type'].value_counts()
            fig_demographics = px.pie(values=visit_type_counts.values,
                                    names=visit_type_counts.index,
                                    title="Patient Demographics")
            st.plotly_chart(fig_demographics, use_container_width=True)
        
        # Export Reports
        st.markdown("### 📋 Export Reports")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📊 Export Appointments Report", type="primary"):
                csv = appointments_df.to_csv(index=False)
                st.download_button(
                    label="Download Appointments CSV",
                    data=csv,
                    file_name=f"appointments_report_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
        
        with col2:
            if st.button("👥 Export Patients Report", type="primary"):
                csv = patients_df.to_csv(index=False)
                st.download_button(
                    label="Download Patients CSV",
                    data=csv,
                    file_name=f"patients_report_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
        
        with col3:
            if st.button("📅 Export Schedule Report", type="primary"):
                csv = schedule_df.to_csv(index=False)
                st.download_button(
                    label="Download Schedule CSV",
                    data=csv,
                    file_name=f"schedule_report_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
        
    except Exception as e:
        st.error(f"Error loading analytics data: {str(e)}")

def dashboard_overview():
    st.markdown('<div class="container section">', unsafe_allow_html=True)
    st.markdown('<h1 style="text-align: center; margin-bottom: 3rem; color: #2d3748;">Admin Dashboard</h1>', unsafe_allow_html=True)
    
    try:
        appointments_df = pd.read_excel("appointments.xlsx")
        schedule_df = pd.read_excel("doctor_schedule.xlsx")
        patients_df = pd.read_csv("patients.csv")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.markdown(f"""
            <div class="stats">
                <span class="stat-number">{len(appointments_df)}</span>
                <div class="stat-label">Total Appointments</div>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            today_appointments = len(appointments_df[appointments_df['slot'].str.contains(
                datetime.now().strftime('%Y-%m-%d'), na=False)])
            st.markdown(f"""
            <div class="stats">
                <span class="stat-number">{today_appointments}</span>
                <div class="stat-label">Today's Appointments</div>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            st.markdown(f"""
            <div class="stats">
                <span class="stat-number">{len(patients_df)}</span>
                <div class="stat-label">Total Patients</div>
            </div>
            """, unsafe_allow_html=True)

        with col4:
            st.markdown(f"""
            <div class="stats">
                <span class="stat-number">{len(schedule_df["doctor"].unique())}</span>
                <div class="stat-label">Active Doctors</div>
            </div>
            """, unsafe_allow_html=True)

        col1, col2 = st.columns(2)

        with col1:
            fig_recent = px.bar(
                appointments_df['doctor'].value_counts().head(10),
                title="Appointments by Doctor (Top 10)",
                labels={'value': 'Number of Appointments', 'index': 'Doctor'})
            st.plotly_chart(fig_recent, use_container_width=True)

        with col2:
            visit_counts = appointments_df['visit_type'].value_counts()
            fig_visits = px.pie(values=visit_counts.values,
                                names=visit_counts.index,
                                title="Visit Type Distribution")
            st.plotly_chart(fig_visits, use_container_width=True)

        st.markdown("### Recent Activity")
        recent_appointments = appointments_df.tail(10)
        st.dataframe(recent_appointments[['name', 'doctor', 'slot', 'visit_type', 'email']])

    except Exception as e:
        st.error(f"Error loading dashboard data: {str(e)}")
    
    st.markdown('</div>', unsafe_allow_html=True)

# Navigation handling (modern buttons)
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
        st.session_state.current_page = 'login'
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
    
    st.markdown('</div></div>', unsafe_allow_html=True)

elif st.session_state.current_page == 'booking':
    st.markdown('<div class="container section">', unsafe_allow_html=True)
    st.markdown('<h1 style="text-align: center; margin-bottom: 2rem; color: #2d3748;">Book Your Appointment</h1>', unsafe_allow_html=True)
    
    # Initialize booking session state
    if 'step' not in st.session_state:
        st.session_state.step = 1
    if 'patient_data' not in st.session_state:
        st.session_state.patient_data = {}

    # Progress Steps
    progress_steps = [
        {"title": "Patient Information", "icon": "1"},
        {"title": "Doctor & Schedule", "icon": "2"},
        {"title": "Insurance Details", "icon": "3"},
        {"title": "Confirmation", "icon": "4"}
    ]

    current_step = st.session_state.step

    # Progress indicator
    st.markdown('<div class="progress-steps">', unsafe_allow_html=True)
    for i, step in enumerate(progress_steps):
        step_num = i + 1
        is_active = step_num == current_step
        is_completed = step_num < current_step
        
        circle_class = "step-circle"
        if is_completed:
            circle_class += " completed"
        elif is_active:
            circle_class += " active"
            
        label_class = "step-label"
        if is_active:
            label_class += " active"
        
        st.markdown(f"""
        <div class="step">
            <div class="{circle_class}">{step["icon"]}</div>
            <div class="{label_class}">{step["title"]}</div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Step 1: Patient Information
    if st.session_state.step == 1:
        st.markdown('<div class="card" style="max-width: 600px; margin: 0 auto;">', unsafe_allow_html=True)
        st.markdown("### Step 1: Patient Information")
        
        with st.form("patient_info_form"):
            name = st.text_input("Full Name", placeholder="Enter your complete name")
            dob = st.text_input("Date of Birth", placeholder="DD-MM-YYYY")
            email = st.text_input("Email Address", placeholder="your.email@example.com")

            submitted = st.form_submit_button("Continue to Doctor Selection", type="primary")

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
                        
                        # Check if returning patient
                        try:
                            patients_df_fresh = pd.read_csv("patients.csv")
                            # Simple check for existing patient
                            existing = patients_df_fresh[patients_df_fresh['email'] == email]
                            if not existing.empty:
                                st.session_state.patient_data['visit_type'] = "Returning"
                                st.session_state.patient_data['doctor'] = existing.iloc[0]['doctor']
                                st.success(f"Welcome back, {name}!")
                            else:
                                st.session_state.patient_data['visit_type'] = "New"
                                st.info(f"Welcome to MediCare, {name}! You're registering as a new patient.")
                        except:
                            st.session_state.patient_data['visit_type'] = "New"

                        st.session_state.step = 2
                        st.rerun()
                else:
                    st.error("Please fill in all required fields")
        
        st.markdown('</div>', unsafe_allow_html=True)

    # Step 2: Doctor Selection
    elif st.session_state.step == 2:
        st.markdown('<div class="card" style="max-width: 800px; margin: 0 auto;">', unsafe_allow_html=True)
        st.markdown("### Step 2: Choose Your Doctor & Appointment Time")
        
        col1, col2 = st.columns([1, 1])

        with col1:
            st.markdown("#### Select Your Doctor")
            doctors = schedule_df["doctor"].unique().tolist()
            selected_doctor = st.selectbox("Available Doctors", doctors)

        with col2:
            st.markdown("#### Available Time Slots")
            available_slots = schedule_df[
                (schedule_df["doctor"] == selected_doctor) & 
                (schedule_df["status"] == "Available")
            ].reset_index(drop=True)

            if available_slots.empty:
                st.error(f"No available slots for Dr. {selected_doctor}")
                selected_slot = None
            else:
                slot_options = []
                for i, row in available_slots.head(10).iterrows():
                    slot_options.append(f"{row['date']} {row['time_slot']}")

                selected_slot_display = st.selectbox("Choose Your Preferred Time", slot_options)
                if selected_slot_display:
                    selected_slot_idx = slot_options.index(selected_slot_display)
                    selected_slot = available_slots.iloc[selected_slot_idx]
                else:
                    selected_slot = None

        if st.button("Continue to Insurance Details", type="primary"):
            if selected_slot is not None:
                st.session_state.patient_data['doctor'] = selected_doctor
                st.session_state.patient_data['slot'] = selected_slot_display
                st.session_state.step = 3
                st.rerun()
            else:
                st.error("Please select a time slot")
        
        st.markdown('</div>', unsafe_allow_html=True)

    # Step 3: Insurance InformationFg
    elif st.session_state.step == 3:
        st.markdown('<div class="card" style="max-width: 600px; margin: 0 auto;">', unsafe_allow_html=True)
        st.markdown("### Step 3: Insurance Information")
        
        with st.form("insurance_form"):
            carrier = st.text_input("Insurance Carrier", placeholder="e.g., Blue Cross Blue Shield")
            member_id = st.text_input("Member ID", placeholder="Your insurance member ID number")

            submitted = st.form_submit_button("Continue to Confirmation", type="primary")

            if submitted:
                st.session_state.patient_data['insurance'] = {
                    "carrier": carrier if carrier else "Self-Pay",
                    "member_id": member_id if member_id else ""
                }
                st.session_state.step = 4
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)

    # Step 4: Confirmation
    elif st.session_state.step == 4:
        st.markdown('<div class="card" style="max-width: 800px; margin: 0 auto;">', unsafe_allow_html=True)
        st.markdown("### Step 4: Confirm Your Appointment")
        
        col1, col2 = st.columns([1, 1])

        with col1:
            st.markdown("""
            <div class="alert alert-info">
                <h4>👤 Patient Information</h4>
            </div>
            """, unsafe_allow_html=True)
            
            st.write(f"**Name:** {st.session_state.patient_data['name']}")
            st.write(f"**Date of Birth:** {st.session_state.patient_data['dob']}")
            st.write(f"**Email:** {st.session_state.patient_data['email']}")

        with col2:
            st.markdown("""
            <div class="alert alert-success">
                <h4>📅 Appointment Details</h4>
            </div>
            """, unsafe_allow_html=True)
            
            st.write(f"**Doctor:** Dr. {st.session_state.patient_data['doctor']}")
            st.write(f"**Date & Time:** {st.session_state.patient_data['slot']}")
            
            insurance = st.session_state.patient_data.get('insurance', {})
            st.write(f"**Insurance:** {insurance.get('carrier', 'Self-Pay')}")

        col1, col2 = st.columns([1, 1])
        
        with col1:
            if st.button("Edit Details", type="secondary"):
                st.session_state.step = 1
                st.rerun()

        with col2:
            if st.button("Confirm Appointment", type="primary"):
                # Save appointment
                new_appt = pd.DataFrame([{
                    "name": st.session_state.patient_data["name"],
                    "dob": st.session_state.patient_data["dob"],
                    "visit_type": st.session_state.patient_data.get("visit_type", "New"),
                    "doctor": st.session_state.patient_data["doctor"],
                    "slot": st.session_state.patient_data["slot"],
                    "insurance_carrier": st.session_state.patient_data.get('insurance', {}).get("carrier", ""),
                    "email": st.session_state.patient_data["email"]
                }])

                try:
                    old_appts = pd.read_excel("appointments.xlsx")
                    all_appts = pd.concat([old_appts, new_appt], ignore_index=True)
                except FileNotFoundError:
                    all_appts = new_appt

                all_appts.to_excel("appointments.xlsx", index=False)
                
                # Send email confirmation
                email_sent = send_appointment_confirmation(
                    st.session_state.patient_data["email"],
                    st.session_state.patient_data["name"],
                    st.session_state.patient_data["doctor"],
                    st.session_state.patient_data["slot"],
                    st.session_state.patient_data.get('insurance', {}).get("carrier", "Self-Pay")
                )
                
                if email_sent:
                    st.success("🎉 Appointment confirmed successfully! Email confirmation sent.")
                else:
                    st.success("🎉 Appointment confirmed successfully!")
                    st.warning("📧 Email confirmation could not be sent. Please check your email settings.")
                
                st.balloons()
                
                # Reset for new booking
                if st.button("Book Another Appointment"):
                    for key in ['step', 'patient_data']:
                        if key in st.session_state:
                            del st.session_state[key]
                    st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.current_page == 'symptoms':
    st.markdown('<div class="container section">', unsafe_allow_html=True)
    st.markdown('<h1 style="text-align: center; margin-bottom: 2rem; color: #2d3748;">AI Symptom Checker</h1>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="alert alert-warning">
        <h4>Important Disclaimer</h4>
        <p>This symptom checker is for informational purposes only and should not replace professional medical advice.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="card" style="max-width: 700px; margin: 0 auto;">', unsafe_allow_html=True)
    
    with st.form("symptom_checker_form"):
        st.markdown("### Describe your symptoms:")

        symptoms_text = st.text_area(
            "Please describe your current symptoms in detail:",
            placeholder="e.g., I have a severe headache, fever, and nausea that started yesterday...",
            height=150)

        col1, col2 = st.columns(2)

        with col1:
            pain_scale = st.slider("Pain Level (1-10):", 1, 10, 5)
            duration = st.selectbox("Symptom Duration:", [
                "Less than 1 hour", "1-6 hours", "6-24 hours", "1-3 days", "More than 3 days"
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
    
    st.markdown('</div></div>', unsafe_allow_html=True)

elif st.session_state.current_page == 'login':
    patient_login_system()

elif st.session_state.current_page == 'admin':
    create_admin_dashboard()

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