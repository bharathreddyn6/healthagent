import pandas as pd
import random
import csv
from pathlib import Path
from datetime import datetime

# Simple rule-based chatbot module for the healthagent Streamlit app
# Supports: 24/7 virtual assistant responses, appointment rescheduling helpers,
# medication reminders storage, basic health tips, and simple multi-language templates.

DEFAULT_TIPS = {
    'en': [
        "Stay hydrated — drink plenty of water throughout the day.",
        "Get regular sleep: 7-8 hours per night for most adults.",
        "Try to do at least 30 minutes of moderate exercise most days.",
        "Eat a balanced diet rich in vegetables, lean proteins, and whole grains.",
    ],
    'es': [
        "Mantente hidratado — bebe suficiente agua durante el día.",
        "Duerme entre 7-8 horas por noche para una mejor salud.",
        "Realiza al menos 30 minutos de ejercicio moderado la mayoría de los días.",
        "Consume una dieta equilibrada rica en verduras y proteínas magras.",
    ],
    'hi': [
        "पर्याप्त पानी पिएं — दिनभर हाइड्रेटेड रहें।",
        "रोज़ाना 7-8 घंटे की नींद लेने का प्रयास करें।",
        "सप्ताह में अधिकांश दिनों में कम से कम 30 मिनट व्यायाम करें।",
        "संतुलित आहार लें जिसमें सब्ज़ियाँ और प्रोटीन शामिल हों।",
    ]
}

TEMPLATES = {
    'greeting': {
        'en': "Hello! I'm MediCare Assistant. I can help with appointments, reminders and quick health tips.",
        'es': "¡Hola! Soy el Asistente de MediCare. Puedo ayudar con citas, recordatorios y consejos de salud rápidos.",
        'hi': "नमस्ते! मैं MediCare सहायक हूँ। मैं अपॉइंटमेंट, रिमाइंडर और स्वास्थ्य सुझावों में मदद कर सकता/सकती हूँ।"
    },
    'ask_pick_appt': {
        'en': "Please tell me which appointment you'd like to reschedule — reply with the appointment number from the list.",
        'es': "Por favor indíqueme qué cita desea reprogramar: responda con el número de cita de la lista.",
        'hi': "कृपया बताइए आप किस अपॉइंटमेंट को बदलना चाहते हैं — सूची से अपॉइंटमेंट नंबर भेजें।"
    },
    'reschedule_success': {
        'en': "Your appointment has been rescheduled successfully.",
        'es': "Su cita se ha reprogramado con éxito.",
        'hi': "आपकी अपॉइंटमेंट सफलतापूर्वक पुनर्निर्धारित हो गई है।"
    },
    'no_appts': {
        'en': "I couldn't find any appointments for this account.",
        'es': "No pude encontrar citas para esta cuenta.",
        'hi': "इस खाते के लिए कोई अपॉइंटमेंट नहीं मिली।"
    }
}


class Chatbot:
    def __init__(self, data_dir: str = '.', reminders_file: str = 'reminders.csv'):
        self.data_dir = Path(data_dir)
        self.appointments_path = self.data_dir / 'appointments.xlsx'
        self.reminders_path = self.data_dir / reminders_file
        # Ensure reminders file exists with header
        if not self.reminders_path.exists():
            with open(self.reminders_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=['email', 'medication', 'times', 'created_at'])
                writer.writeheader()

    def get_patient_appointments(self, email: str):
        try:
            df = pd.read_excel(self.appointments_path)
            return df[df['email'] == email].reset_index()
        except Exception:
            return pd.DataFrame()

    def request_reschedule(self, email: str, appt_index: int, new_slot: str):
        """Update appointment slot. appt_index should be the DataFrame index returned by get_patient_appointments()."""
        try:
            df = pd.read_excel(self.appointments_path)
            # locate rows for this email
            patient_rows = df[df['email'] == email]
            if patient_rows.empty:
                return False, TEMPLATES['no_appts']['en']

            if appt_index < 0 or appt_index >= len(patient_rows):
                return False, "Invalid appointment selection."

            # Get global index
            global_idx = patient_rows.index[appt_index]
            df.at[global_idx, 'slot'] = new_slot
            df.to_excel(self.appointments_path, index=False)
            return True, TEMPLATES['reschedule_success']['en']
        except Exception as e:
            return False, f"Error rescheduling: {e}"

    def schedule_medication_reminder(self, email: str, medication: str, times: str):
        try:
            with open(self.reminders_path, 'a', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=['email', 'medication', 'times', 'created_at'])
                writer.writerow({
                    'email': email,
                    'medication': medication,
                    'times': times,
                    'created_at': datetime.now().isoformat()
                })
            return True, f"Medication reminder set for {medication} at {times}."
        except Exception as e:
            return False, f"Failed to set reminder: {e}"

    def get_health_tip(self, language: str = 'en'):
        language = language if language in DEFAULT_TIPS else 'en'
        return random.choice(DEFAULT_TIPS[language])

    def respond(self, email: str, message: str, language: str = 'en'):
        """Basic intent detection and structured response.
        Returns a dict with keys: type (text|reschedule_list|action_response), text, and optional data.
        """
        msg = (message or '').lower()
        language = language if language in DEFAULT_TIPS else 'en'

        # Greetings
        if any(x in msg for x in ['hello', 'hi', 'hey', 'hola', 'namaste']):
            return {'type': 'text', 'text': TEMPLATES['greeting'][language]}

        # Reschedule intent
        if any(x in msg for x in ['resched', 'reschedule', 'change appointment', 'change my appointment', 'move appointment']):
            appts = self.get_patient_appointments(email)
            if appts.empty:
                return {'type': 'text', 'text': TEMPLATES['no_appts'][language]}

            # Build short list
            items = []
            for i, row in appts.iterrows():
                items.append({'index': int(i), 'doctor': row.get('doctor',''), 'slot': row.get('slot',''), 'visit_type': row.get('visit_type','')})

            return {
                'type': 'reschedule_list',
                'text': TEMPLATES['ask_pick_appt'][language],
                'appointments': items
            }

        # Medication reminder intent
        if any(x in msg for x in ['remind', 'reminder', 'medication', 'medicine', 'pill']):
            return {'type': 'text', 'text': {
                'en': "Sure — tell me the medication name and the times you'd like reminders (e.g. 'Aspirin; 08:00, 20:00').",
                'es': "Claro — dígame el nombre del medicamento y las horas (p.ej. 'Aspirin; 08:00, 20:00').",
                'hi': "ठीक है — मुझे दवा का नाम और रिमाइंडर का समय बताइए (उदा. 'Aspirin; 08:00, 20:00')."
            }[language]}

        # Health tips
        if any(x in msg for x in ['tip', 'health tip', 'advice', 'healthy']):
            tip = self.get_health_tip(language)
            return {'type': 'text', 'text': tip}

        # Default fallback
        return {'type': 'text', 'text': {
            'en': "Sorry, I didn't understand that. I can help with: rescheduling appointments, setting medication reminders, and quick health tips.",
            'es': "Lo siento, no entendí. Puedo ayudar con reprogramar citas, configurar recordatorios de medicación y consejos de salud.",
            'hi': "माफ़ कीजिए, मैं समझ नहीं पाया। मैं अपॉइंटमेंट बदलने, दवा रिमाइंडर सेट करने और स्वास्थ्य सुझाव देने में मदद कर सकता/सकती हूँ।"
        }[language]}
