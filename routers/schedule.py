from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, EmailStr
from datetime import datetime
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import aiosmtplib

router = APIRouter()
templates = Jinja2Templates(directory="templates")

# In-memory storage (replace with database in production)
bookings = []

class ScheduleRequest(BaseModel):
    name: str
    email: EmailStr
    phone: str
    topic: str
    message: str = ""
    date: str
    time: str

@router.get("/schedule", response_class=HTMLResponse)
async def schedule_page(request: Request):
    return templates.TemplateResponse("schedule.html", {"request": request})

@router.post("/api/schedule")
async def create_booking(booking: ScheduleRequest):
    try:
        # Create booking record
        booking_dict = booking.dict()
        booking_dict["created_at"] = datetime.now().isoformat()
        booking_dict["status"] = "pending"
        bookings.append(booking_dict)

        # Send confirmation emails
        await send_confirmation_emails(booking)
        
        return {"status": "success", "message": "Booking created successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

async def send_confirmation_emails(booking: ScheduleRequest):
    # Email configuration
    email_host = os.getenv("MAIL_SERVER", "smtp.gmail.com")
    email_port = int(os.getenv("MAIL_PORT", "587"))
    email_username = os.getenv("MAIL_USERNAME", "your-email@gmail.com")
    email_password = os.getenv("MAIL_PASSWORD", "your-password")

    # Create customer email
    customer_html = f"""
    <h2>Konsultasiya Təsdiqi</h2>
    <p>Hörmətli {booking.name},</p>
    <p>Konsultasiya müraciətiniz qəbul edildi. Təfərrüatlar aşağıdakı kimidir:</p>
    <ul>
        <li>Tarix: {booking.date}</li>
        <li>Vaxt: {booking.time}</li>
        <li>Mövzu: {booking.topic}</li>
    </ul>
    <p>Biz sizinlə əlaqə saxlayacağıq.</p>
    <p>Hörmətlə,<br>Komandamız</p>
    """

    # Create admin notification email
    admin_html = f"""
    <h2>Yeni Konsultasiya Müraciəti</h2>
    <p>Müştəri məlumatları:</p>
    <ul>
        <li>Ad: {booking.name}</li>
        <li>Email: {booking.email}</li>
        <li>Telefon: {booking.phone}</li>
        <li>Tarix: {booking.date}</li>
        <li>Vaxt: {booking.time}</li>
        <li>Mövzu: {booking.topic}</li>
        <li>Mesaj: {booking.message}</li>
    </ul>
    """

    try:
        # Send customer confirmation
        customer_message = MIMEMultipart()
        customer_message["From"] = email_username
        customer_message["To"] = booking.email
        customer_message["Subject"] = "Konsultasiya Təsdiqi"
        customer_message.attach(MIMEText(customer_html, "html"))

        # Send admin notification
        admin_message = MIMEMultipart()
        admin_message["From"] = email_username
        admin_message["To"] = email_username  # Send to admin email
        admin_message["Subject"] = "Yeni Konsultasiya Müraciəti"
        admin_message.attach(MIMEText(admin_html, "html"))

        # Connect to SMTP server and send emails
        async with aiosmtplib.SMTP(hostname=email_host, port=email_port, use_tls=True) as smtp:
            await smtp.login(email_username, email_password)
            await smtp.send_message(customer_message)
            await smtp.send_message(admin_message)

    except Exception as e:
        print(f"Error sending email: {str(e)}")
        # Don't raise the exception - we don't want to fail the booking if email fails
        pass
