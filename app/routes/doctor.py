from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models.user import User
from app.models.appointment import Appointment
from app.models.prescription import Prescription
from datetime import datetime, date

bp = Blueprint('doctor', __name__, url_prefix='/doctor')

@bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.role != 'doctor':
        flash('Access denied. Doctors only.', 'error')
        return redirect(url_for('main.index'))
    
    # Get today's appointments
    today_appointments = Appointment.query.filter_by(
        doctor_id=current_user.id,
        date=date.today()
    ).order_by(Appointment.time.asc()).all()
    
    # Get upcoming appointments (next 7 days)
    upcoming_appointments = Appointment.query.filter_by(
        doctor_id=current_user.id
    ).filter(Appointment.date > date.today()).order_by(Appointment.date.asc()).limit(10).all()
    
    # Get patients count
    patients_count = db.session.query(Appointment.patient_id).filter_by(
        doctor_id=current_user.id
    ).distinct().count()
    
    return render_template('doctor/dashboard.html',
                         today_appointments=today_appointments,
                         upcoming_appointments=upcoming_appointments,
                         patients_count=patients_count)
