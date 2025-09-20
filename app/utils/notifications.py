from flask import current_app
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email(to_email, subject, body):
    try:
        # Set up the server
        server = smtplib.SMTP(current_app.config['SMTP_SERVER'], current_app.config['SMTP_PORT'])
        server.starttls()
        server.login(current_app.config['SMTP_USERNAME'], current_app.config['SMTP_PASSWORD'])

        # Create the email
        msg = MIMEMultipart()
        msg['From'] = current_app.config['SMTP_USERNAME']
        msg['To'] = to_email
        msg['Subject'] = subject

        # Attach the body with the msg instance
        msg.attach(MIMEText(body, 'plain'))

        # Send the email
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False

def send_reminder_email(patient_email, appointment_details):
    subject = "Appointment Reminder"
    body = f"Dear Patient,\n\nThis is a reminder for your upcoming appointment:\n{appointment_details}\n\nThank you!"
    return send_email(patient_email, subject, body)