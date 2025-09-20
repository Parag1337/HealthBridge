from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models.user import User
from app.models.appointment import Appointment
from app.models.prescription import Prescription
from datetime import datetime, date

bp = Blueprint('patient', __name__, url_prefix='/patient')

@bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.role != 'patient':
        flash('Access denied. Patients only.', 'error')
        return redirect(url_for('main.index'))
    
    # Get recent appointments
    recent_appointments = Appointment.query.filter_by(
        patient_id=current_user.id
    ).order_by(Appointment.date.desc()).limit(5).all()
    
    # Get recent prescriptions
    recent_prescriptions = Prescription.query.filter_by(
        patient_id=current_user.id
    ).order_by(Prescription.created_at.desc()).limit(5).all()
    
    # Get upcoming appointments
    upcoming_appointments = Appointment.query.filter_by(
        patient_id=current_user.id
    ).filter(Appointment.date >= date.today()).order_by(Appointment.date.asc()).limit(3).all()
    
    return render_template('patient/dashboard.html',
                         recent_appointments=recent_appointments,
                         recent_prescriptions=recent_prescriptions,
                         upcoming_appointments=upcoming_appointments)

@bp.route('/appointments')
@login_required
def appointments():
    if current_user.role != 'patient':
        flash('Access denied. Patients only.', 'error')
        return redirect(url_for('main.index'))
    
    page = request.args.get('page', 1, type=int)
    appointments = Appointment.query.filter_by(
        patient_id=current_user.id
    ).order_by(Appointment.date.desc()).paginate(
        page=page, per_page=10, error_out=False
    )
    
    return render_template('patient/appointments.html', appointments=appointments)

@bp.route('/book-appointment', methods=['GET', 'POST'])
@login_required
def book_appointment():
    if current_user.role != 'patient':
        flash('Access denied. Patients only.', 'error')
        return redirect(url_for('main.index'))
    
    if request.method == 'GET':
        doctors = User.query.filter_by(role='doctor', is_active=True).all()
        return render_template('patient/book_appointment.html', doctors=doctors)
    
    # Handle POST request
    doctor_id = request.form.get('doctor_id')
    appointment_date = request.form.get('appointment_date')
    appointment_time = request.form.get('appointment_time')
    reason = request.form.get('reason')
    
    if not all([doctor_id, appointment_date, appointment_time, reason]):
        flash('All fields are required', 'error')
        doctors = User.query.filter_by(role='doctor', is_active=True).all()
        return render_template('patient/book_appointment.html', doctors=doctors)
    
    # Check if doctor exists
    doctor = User.query.filter_by(id=doctor_id, role='doctor').first()
    if not doctor:
        flash('Invalid doctor selected', 'error')
        doctors = User.query.filter_by(role='doctor', is_active=True).all()
        return render_template('patient/book_appointment.html', doctors=doctors)
    
    # Create appointment
    appointment = Appointment(
        patient_id=current_user.id,
        doctor_id=doctor_id,
        date=datetime.strptime(appointment_date, '%Y-%m-%d').date(),
        time=datetime.strptime(appointment_time, '%H:%M').time(),
        reason=reason,
        status='scheduled'
    )
    
    try:
        db.session.add(appointment)
        db.session.commit()
        flash('Appointment booked successfully!', 'success')
        return redirect(url_for('patient.appointments'))
    except Exception as e:
        db.session.rollback()
        flash('Failed to book appointment. Please try again.', 'error')
        doctors = User.query.filter_by(role='doctor', is_active=True).all()
        return render_template('patient/book_appointment.html', doctors=doctors)

@bp.route('/prescriptions')
@login_required
def prescriptions():
    if current_user.role != 'patient':
        flash('Access denied. Patients only.', 'error')
        return redirect(url_for('main.index'))
    
    page = request.args.get('page', 1, type=int)
    prescriptions = Prescription.query.filter_by(
        patient_id=current_user.id
    ).order_by(Prescription.created_at.desc()).paginate(
        page=page, per_page=10, error_out=False
    )
    
    return render_template('patient/prescriptions.html', prescriptions=prescriptions)

@bp.route('/profile')
@login_required
def profile():
    if current_user.role != 'patient':
        flash('Access denied. Patients only.', 'error')
        return redirect(url_for('main.index'))
    
    return render_template('patient/profile.html', user=current_user)
