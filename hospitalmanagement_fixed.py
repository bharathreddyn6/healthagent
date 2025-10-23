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
    page_title="MediCare Plus - Healthcare at Your Fingertips",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Modern, Premium Healthcare Portal CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800&display=swap');
    
    /* Global Styles */
    * {
        font-family: 'Poppins', sans-serif;
    }
    
    .main {
        padding: 0;
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    
    /* Hide default Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display:none;}
    header {visibility: hidden;}
    
    /* Hero Section */
    .hero-section {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 4rem 2rem;
        border-radius: 0 0 50px 50px;
        margin: -1rem -1rem 3rem -1rem;
        box-shadow: 0 20px 60px rgba(0,0,0,0.3);
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
        color: white;
        text-align: center;
    }
    
    .hero-content h1 {
        font-size: 3.5rem;
        font-weight: 800;
        margin: 0 0 1rem 0;
        text-shadow: 2px 4px 8px rgba(0,0,0,0.2);
        letter-spacing: -1px;
    }
    
    .hero-content p {
        font-size: 1.3rem;
        opacity: 0.95;
        font-weight: 300;
        max-width: 600px;
        margin: 0 auto;
    }
    
    /* Feature Cards */
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
    }
    
    .feature-title {
        font-size: 1.5rem;
        font-weight: 700;
        color: #2d3748;
        margin-bottom: 1rem;
    }
    
    .feature-description {
        color: #718096;
        font-size: 1rem;
        line-height: 1.6;
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
    
    .step-label {
        font-size: 0.85rem;
        color: #718096;
        font-weight: 500;
    }
    
    .step-label.active {
        color: #667eea;
        font-weight: 600;
    }
    
    /* Input Fields */
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
    
    /* Buttons */
    .stButton > button {
        border-radius: 50px;
        padding: 1rem 3rem;
        font-weight: 600;
        font-size: 1.1rem;
        transition: all 0.3s ease;
        border: none;
        box-shadow: 0 8px 20px rgba(0,0,0,0.15);
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    
    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 12px 30px rgba(102, 126, 234, 0.4);
    }
    
    /* Stats */
    .stats {
        background: white;
        padding: 2rem;
        border-radius: 20px;
        box-shadow: 0 8px 30px rgba(0,0,0,0.08);
        text-align: center;
        border-top: 4px solid #667eea;
        transition: all 0.3s ease;
    }
    
    .stats:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 40px rgba(102, 126, 234, 0.2);
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
    
    /* Responsive */
    @media (max-width: 768px) {
        .hero-content h1 { font-size: 2.5rem; }
        .hero-content p { font-size: 1.1rem; }
        .feature-card { padding: 1.5rem; }
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
            patient_appointments = appointments_df[appointments_df['email'] == email]

            if not patient_appointments.empty:
                st.success(f"Found {len(patient_appointments)} appointments for {email}")

                st.markdown("### Your Appointments")
                for idx, appointment in patient_appointments.iterrows():
                    with st.expander(f"Appointment with Dr. {appointment['doctor']} - {appointment['slot']}"):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"**Doctor:** Dr. {appointment['doctor']}")
                            st.write(f"**Date & Time:** {appointment['slot']}")
                            st.write(f"**Visit Type:** {appointment['visit_type']}")
                        with col2:
                            st.write(f"**Insurance:** {appointment.get('insurance_carrier', 'Self-Pay')}")
                            st.write(f"**Status:** Scheduled")

                st.markdown("### Medical History")
                st.info("Medical history features will be available in future updates.")
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
            today_appointments = len(appointments_df[appointments_df['slot'].str.contains(
                datetime.now().strftime('%Y-%m-%d'), na=False)])
            st.metric("Today's Appointments", today_appointments)

        with col3:
            st.metric("Total Patients", len(patients_df))

        with col4:
            st.metric("Active Doctors", len(schedule_df["doctor"].unique()))

        with col5:
            available_slots = len(schedule_df[schedule_df["status"] == 'Available'])
            st.metric("Available Slots", available_slots)

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

# MAIN APP
st.markdown("""
<div class="hero-section">
    <div class="hero-content">
        <h1>🏥 MediCare Plus</h1>
        <p>Your Health, Our Priority - Experience world-class healthcare with modern technology</p>
    </div>
</div>
""", unsafe_allow_html=True)

# Initialize session state for admin
if 'admin_authenticated' not in st.session_state:
    st.session_state.admin_authenticated = False

# Modern Navigation
menu_options = [
    "🏠 Home", 
    "📋 Book Appointment", 
    "🧠 Symptom Checker", 
    "👤 Patient Portal",
    "🔐 Admin Dashboard"
]

selected_menu = st.selectbox("Navigate to:", menu_options)

# Route to different pages
if selected_menu == "🏠 Home":
    # Stats Section
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
    st.markdown('<h2 style="text-align: center; margin: 3rem 0; font-size: 2.5rem; color: #2d3748;">Our Services</h2>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="feature-card fade-in-up">
            <div class="feature-icon">📅</div>
            <h3 class="feature-title">Online Booking</h3>
            <p class="feature-description">Schedule appointments with our specialists instantly through our advanced booking system.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card fade-in-up">
            <div class="feature-icon">🤖</div>
            <h3 class="feature-title">AI Diagnosis</h3>
            <p class="feature-description">Get preliminary health assessments using our AI-powered symptom checker technology.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="feature-card fade-in-up">
            <div class="feature-icon">📱</div>
            <h3 class="feature-title">Digital Records</h3>
            <p class="feature-description">Access your complete medical history and test results anytime, anywhere securely.</p>
        </div>
        """, unsafe_allow_html=True)

elif selected_menu == "🧠 Symptom Checker":
    st.markdown("## AI-Powered Symptom Checker")

    st.markdown("""
    <div class="alert alert-warning">
        <h4>Important Disclaimer</h4>
        <p>This symptom checker is for informational purposes only and should not replace professional medical advice.</p>
    </div>
    """, unsafe_allow_html=True)

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

elif selected_menu == "👤 Patient Portal":
    patient_portal()

elif selected_menu == "🔐 Admin Dashboard":
    if not st.session_state.admin_authenticated:
        admin_login()
    else:
        dashboard_overview()
        
        st.markdown("---")
        if st.button("Logout", type="secondary"):
            st.session_state.admin_authenticated = False
            st.rerun()

else:  # Book Appointment
    st.markdown("## Book Your Appointment")
    
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

    # Step 2: Doctor Selection
    elif st.session_state.step == 2:
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

    # Step 3: Insurance Information
    elif st.session_state.step == 3:
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

    # Step 4: Confirmation
    elif st.session_state.step == 4:
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
                
                st.success("🎉 Appointment confirmed successfully!")
                st.balloons()
                
                # Reset for new booking
                if st.button("Book Another Appointment"):
                    for key in ['step', 'patient_data']:
                        if key in st.session_state:
                            del st.session_state[key]
                    st.rerun()