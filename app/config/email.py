import os
from dotenv import load_dotenv
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

load_dotenv()

class EmailConfig:
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    MAIL_FROM = os.getenv("MAIL_FROM")
    MAIL_PORT = int(os.getenv("MAIL_PORT", "587"))
    MAIL_SERVER = os.getenv("MAIL_SERVER")
    MAIL_FROM_NAME = os.getenv("MAIL_FROM_NAME")

async def send_email(to_email: str, subject: str, body: str):
    message = MIMEMultipart()
    message["From"] = f"{EmailConfig.MAIL_FROM_NAME} <{EmailConfig.MAIL_FROM}>"
    message["To"] = to_email
    message["Subject"] = subject
    
    message.attach(MIMEText(body, "html"))
    
    try:
        async with aiosmtplib.SMTP(
            hostname=EmailConfig.MAIL_SERVER,
            port=EmailConfig.MAIL_PORT,
            use_tls=True
        ) as smtp:
            await smtp.login(EmailConfig.MAIL_USERNAME, EmailConfig.MAIL_PASSWORD)
            await smtp.send_message(message)
        return True
    except Exception as e:
        print(f"Failed to send email: {str(e)}")
        return False
