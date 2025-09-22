"""
Email utility functions for HealthBridge AI
Handles appointment confirmations, prescription notifications, and reminders
"""
from flask import current_app, render_template
from flask_mail import Message
from app import mail
import threading

def send_async_email(app, msg):
    """Send email asynchronously to avoid blocking the main thread"""
    with app.app_context():
        try:
            mail.send(msg)
        except Exception as e:
            print(f"Error sending email: {str(e)}")

def send_email(subject, sender, recipients, text_body, html_body=None):
    """
    Send an email with both text and HTML content
    
    Args:
        subject (str): Email subject
        sender (str): Sender email address
        recipients (list): List of recipient email addresses
        text_body (str): Plain text email content
        html_body (str, optional): HTML email content
    """
    print(f"📧 Preparing to send email:")
    print(f"   Subject: {subject}")
    print(f"   From: {sender}")
    print(f"   To: {recipients}")
    
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    if html_body:
        msg.html = html_body
    
    # Send email synchronously for debugging
    print("� Sending email synchronously...")
    try:
        mail.send(msg)
        print("✅ Email sent successfully!")
    except Exception as e:
        print(f"❌ Error sending email: {str(e)}")
        import traceback
        traceback.print_exc()
        raise

def send_appointment_confirmation_email(user, appointment, doctor):
    """
    Send appointment confirmation email to patient
    
    Args:
        user: Patient user object
        appointment: Appointment object
        doctor: Doctor user object
    """
    subject = f"Appointment Confirmation - HealthBridge AI"
    sender = current_app.config['MAIL_DEFAULT_SENDER']
    recipients = [user.email]
    
    # Plain text version
    text_body = f"""
Dear {user.first_name} {user.last_name},

Your appointment has been successfully booked!

Appointment Details:
- Doctor: Dr. {doctor.first_name} {doctor.last_name}
- Specialization: {doctor.specialization or 'General Medicine'}
- Date: {appointment.date.strftime('%B %d, %Y')}
- Time: {appointment.time.strftime('%I:%M %p') if appointment.time else 'Time to be confirmed'}
- Reason: {appointment.reason or 'General consultation'}

Please arrive 15 minutes before your scheduled appointment time.

If you need to reschedule or cancel your appointment, please contact us as soon as possible.

Thank you for choosing HealthBridge AI.

Best regards,
HealthBridge AI Team
"""
    
    # HTML version
    html_body = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; background-color: #f8f9fa;">
        <div style="background-color: #007bff; color: white; text-align: center; padding: 20px; border-radius: 8px 8px 0 0;">
            <h1 style="margin: 0;">🏥 HealthBridge AI</h1>
            <p style="margin: 10px 0 0 0;">Your Healthcare Partner</p>
        </div>
        
        <div style="background-color: white; padding: 30px; border-radius: 0 0 8px 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
            <h2 style="color: #28a745; margin-top: 0;">✅ Appointment Confirmed!</h2>
            
            <p>Dear <strong>{user.first_name} {user.last_name}</strong>,</p>
            
            <p>Your appointment has been successfully booked. Here are your appointment details:</p>
            
            <div style="background-color: #f8f9fa; padding: 20px; border-radius: 6px; margin: 20px 0;">
                <h3 style="margin-top: 0; color: #007bff;">📋 Appointment Details</h3>
                <p><strong>🩺 Doctor:</strong> Dr. {doctor.first_name} {doctor.last_name}</p>
                <p><strong>🏥 Specialization:</strong> {doctor.specialization or 'General Medicine'}</p>
                <p><strong>📅 Date:</strong> {appointment.date.strftime('%B %d, %Y')}</p>
                <p><strong>🕐 Time:</strong> {appointment.time.strftime('%I:%M %p') if appointment.time else 'Time to be confirmed'}</p>
                <p><strong>📝 Reason:</strong> {appointment.reason or 'General consultation'}</p>
            </div>
            
            <div style="background-color: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; border-radius: 6px; margin: 20px 0;">
                <p style="margin: 0;"><strong>⏰ Important:</strong> Please arrive 15 minutes before your scheduled appointment time.</p>
            </div>
            
            <p>If you need to reschedule or cancel your appointment, please contact us as soon as possible.</p>
            
            <div style="text-align: center; margin: 30px 0;">
                <a href="mailto:healthbridgeassistant@gmail.com" style="background-color: #007bff; color: white; padding: 12px 25px; text-decoration: none; border-radius: 5px; display: inline-block;">Contact Us</a>
            </div>
            
            <p style="color: #6c757d; font-size: 14px; margin-top: 30px;">
                Thank you for choosing HealthBridge AI for your healthcare needs.
            </p>
            
            <hr style="border: none; border-top: 1px solid #e9ecef; margin: 20px 0;">
            
            <p style="color: #6c757d; font-size: 12px; text-align: center; margin: 0;">
                Best regards,<br>
                <strong>HealthBridge AI Team</strong><br>
                Your Trusted Healthcare Partner
            </p>
        </div>
    </div>
    """
    
    send_email(subject, sender, recipients, text_body, html_body)

def send_prescription_email(patient, prescription, doctor, medications, lab_tests):
    """
    Send prescription details email to patient
    
    Args:
        patient: Patient user object
        prescription: Prescription object
        doctor: Doctor user object
        medications: List of PrescriptionMedication objects
        lab_tests: List of LabTest objects
    """
    subject = f"Your Prescription - HealthBridge AI"
    sender = current_app.config['MAIL_DEFAULT_SENDER']
    recipients = [patient.email]
    
    # Build medications list
    medications_text = ""
    medications_html = ""
    
    if medications:
        medications_text = "\nMedications:\n"
        medications_html = "<h4 style='color: #007bff; margin-top: 20px;'>💊 Prescribed Medications:</h4><ul>"
        
        for med in medications:
            medications_text += f"- {med.medication_name}\n"
            medications_text += f"  Dosage: {med.dosage}\n"
            medications_text += f"  Frequency: {med.frequency}\n"
            medications_text += f"  Duration: {med.duration}\n"
            if med.instructions:
                medications_text += f"  Instructions: {med.instructions}\n"
            medications_text += "\n"
            
            medications_html += f"""
            <li style="margin-bottom: 15px; background-color: #f8f9fa; padding: 10px; border-radius: 5px;">
                <strong style="color: #007bff;">{med.medication_name}</strong><br>
                <span style="color: #6c757d;">Dosage:</span> {med.dosage}<br>
                <span style="color: #6c757d;">Frequency:</span> {med.frequency}<br>
                <span style="color: #6c757d;">Duration:</span> {med.duration}
                {f'<br><span style="color: #6c757d;">Instructions:</span> {med.instructions}' if med.instructions else ''}
            </li>
            """
        medications_html += "</ul>"
    
    # Build lab tests list
    lab_tests_text = ""
    lab_tests_html = ""
    
    if lab_tests:
        lab_tests_text = "\nRecommended Lab Tests:\n"
        lab_tests_html = "<h4 style='color: #dc3545; margin-top: 20px;'>🔬 Recommended Lab Tests:</h4><ul>"
        
        for test in lab_tests:
            lab_tests_text += f"- {test.test_name}\n"
            if test.instructions:
                lab_tests_text += f"  Instructions: {test.instructions}\n"
            lab_tests_text += f"  Priority: {test.priority}\n\n"
            
            lab_tests_html += f"""
            <li style="margin-bottom: 15px; background-color: #fff5f5; padding: 10px; border-radius: 5px;">
                <strong style="color: #dc3545;">{test.test_name}</strong><br>
                {f'<span style="color: #6c757d;">Instructions:</span> {test.instructions}<br>' if test.instructions else ''}
                <span style="color: #6c757d;">Priority:</span> <span style="color: #dc3545; font-weight: bold;">{test.priority}</span>
            </li>
            """
        lab_tests_html += "</ul>"
    
    # Plain text version
    text_body = f"""
Dear {patient.first_name} {patient.last_name},

You have received a new prescription from Dr. {doctor.first_name} {doctor.last_name}.

Prescription Details:
- Prescribed Date: {prescription.prescribed_date.strftime('%B %d, %Y') if prescription.prescribed_date else prescription.created_at.strftime('%B %d, %Y') if prescription.created_at else 'Not specified'}
- Status: {prescription.status or 'Active'}
{f'- Notes: {prescription.notes}' if prescription.notes else ''}
{medications_text}
{lab_tests_text}

Important Instructions:
- Please follow the prescribed dosage and frequency exactly as mentioned
- Complete the full course of medication even if you feel better
- Contact your doctor if you experience any side effects
- Get the recommended lab tests done as per the priority

For any questions or concerns, please contact your doctor or our support team.

Stay healthy!

Best regards,
HealthBridge AI Team
"""
    
    # HTML version
    html_body = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; background-color: #f8f9fa;">
        <div style="background-color: #28a745; color: white; text-align: center; padding: 20px; border-radius: 8px 8px 0 0;">
            <h1 style="margin: 0;">🏥 HealthBridge AI</h1>
            <p style="margin: 10px 0 0 0;">Your Healthcare Partner</p>
        </div>
        
        <div style="background-color: white; padding: 30px; border-radius: 0 0 8px 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
            <h2 style="color: #28a745; margin-top: 0;">📄 New Prescription Received</h2>
            
            <p>Dear <strong>{patient.first_name} {patient.last_name}</strong>,</p>
            
            <p>You have received a new prescription from <strong>Dr. {doctor.first_name} {doctor.last_name}</strong>.</p>
            
            <div style="background-color: #f8f9fa; padding: 20px; border-radius: 6px; margin: 20px 0;">
                <h3 style="margin-top: 0; color: #28a745;">📋 Prescription Information</h3>
                <p><strong>🩺 Prescribed by:</strong> Dr. {doctor.first_name} {doctor.last_name}</p>
                <p><strong>📅 Date:</strong> {prescription.prescribed_date.strftime('%B %d, %Y') if prescription.prescribed_date else prescription.created_at.strftime('%B %d, %Y') if prescription.created_at else 'Not specified'}</p>
                <p><strong>📊 Status:</strong> <span style="color: #28a745; font-weight: bold;">{prescription.status or 'Active'}</span></p>
                {f'<p><strong>📝 Notes:</strong> {prescription.notes}</p>' if prescription.notes else ''}
            </div>
            
            {medications_html}
            
            {lab_tests_html}
            
            <div style="background-color: #d1ecf1; border: 1px solid #bee5eb; padding: 15px; border-radius: 6px; margin: 20px 0;">
                <h4 style="margin-top: 0; color: #0c5460;">⚠️ Important Instructions:</h4>
                <ul style="margin: 0; padding-left: 20px;">
                    <li>Follow the prescribed dosage and frequency exactly as mentioned</li>
                    <li>Complete the full course of medication even if you feel better</li>
                    <li>Contact your doctor if you experience any side effects</li>
                    <li>Get the recommended lab tests done as per the priority</li>
                </ul>
            </div>
            
            <div style="text-align: center; margin: 30px 0;">
                <a href="mailto:healthbridgeassistant@gmail.com" style="background-color: #28a745; color: white; padding: 12px 25px; text-decoration: none; border-radius: 5px; display: inline-block; margin-right: 10px;">Contact Doctor</a>
                <a href="http://127.0.0.1:5000/patient/prescriptions" style="background-color: #007bff; color: white; padding: 12px 25px; text-decoration: none; border-radius: 5px; display: inline-block;">View in Portal</a>
            </div>
            
            <p style="color: #6c757d; font-size: 14px; margin-top: 30px;">
                For any questions or concerns, please contact your doctor or our support team.
            </p>
            
            <hr style="border: none; border-top: 1px solid #e9ecef; margin: 20px 0;">
            
            <p style="color: #6c757d; font-size: 12px; text-align: center; margin: 0;">
                Stay healthy!<br>
                <strong>HealthBridge AI Team</strong><br>
                Your Trusted Healthcare Partner
            </p>
        </div>
    </div>
    """
    
    send_email(subject, sender, recipients, text_body, html_body)

def send_appointment_reminder_email(user, appointment, doctor):
    """
    Send appointment reminder email (can be used for future reminder functionality)
    
    Args:
        user: Patient user object
        appointment: Appointment object
        doctor: Doctor user object
    """
    subject = f"Appointment Reminder - Tomorrow at {appointment.time.strftime('%I:%M %p') if appointment.time else 'TBD'}"
    sender = current_app.config['MAIL_DEFAULT_SENDER']
    recipients = [user.email]
    
    text_body = f"""
Dear {user.first_name} {user.last_name},

This is a friendly reminder about your upcoming appointment tomorrow.

Appointment Details:
- Doctor: Dr. {doctor.first_name} {doctor.last_name}
- Date: {appointment.date.strftime('%B %d, %Y')}
- Time: {appointment.time.strftime('%I:%M %p') if appointment.time else 'Time to be confirmed'}

Please arrive 15 minutes early.

Best regards,
HealthBridge AI Team
"""
    
    html_body = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
        <h2 style="color: #ffc107;">⏰ Appointment Reminder</h2>
        <p>Dear <strong>{user.first_name} {user.last_name}</strong>,</p>
        <p>This is a friendly reminder about your upcoming appointment <strong>tomorrow</strong>.</p>
        <div style="background-color: #fff3cd; padding: 15px; border-radius: 5px; margin: 20px 0;">
            <p><strong>Doctor:</strong> Dr. {doctor.first_name} {doctor.last_name}</p>
            <p><strong>Date:</strong> {appointment.date.strftime('%B %d, %Y')}</p>
            <p><strong>Time:</strong> {appointment.time.strftime('%I:%M %p') if appointment.time else 'Time to be confirmed'}</p>
        </div>
        <p><em>Please arrive 15 minutes early.</em></p>
        <p>Best regards,<br>HealthBridge AI Team</p>
    </div>
    """
    
    send_email(subject, sender, recipients, text_body, html_body)