import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict

# Email configuration
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = os.getenv("MAIL_USERNAME", "farrza111@gmail.com")
SENDER_PASSWORD = os.getenv("MAIL_PASSWORD", "zcnu rshv xlih yacf")
RECIPIENT_EMAIL = os.getenv("MAIL_USERNAME", "farrza111@gmail.com")

def create_meeting_email(form_data: Dict) -> MIMEMultipart:
    """Create email message for meeting requests."""
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = RECIPIENT_EMAIL
    msg['Subject'] = f"Yeni Görüş Tələbi - {form_data['name']}"
    
    # Create email body
    body = f"""
        Yeni görüş tələbi alındı:
        
        Ad və Soyad: {form_data['name']}
        Email: {form_data['email']}
        Telefon: {form_data['phone']}
        
        Mesaj:
        {form_data['message']}
        
        ------------------
        Bu mesaj avtomatik olaraq göndərilib.
    """
    
    msg.attach(MIMEText(body, 'plain', 'utf-8'))
    return msg

async def send_email(form_data: Dict) -> bool:
    """Send email asynchronously."""
    try:
        msg = create_meeting_email(form_data)
        
        # Create SMTP session
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
        
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False
