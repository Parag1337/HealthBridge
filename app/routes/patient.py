from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.user import User
from app.models.appointment import Appointment
from app.models.prescription import Prescription
from app.models.prescription_components import PrescriptionMedication, LabTest, PrescriptionEdit
from app.utils.email import send_appointment_confirmation_email
from datetime import datetime, date, timedelta
from sqlalchemy import and_, or_

bp = Blueprint('patient', __name__, url_prefix='/patient')

@bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.role != 'patient':
        flash('Access denied. Patients only.', 'error')
        return redirect(url_for('main.index'))
    
    # Enhanced dashboard with more statistics
    # Get recent appointments
    recent_appointments = Appointment.query.filter_by(
        patient_id=current_user.id
    ).order_by(Appointment.date.desc()).limit(5).all()
    
    # Get recent prescriptions with enhanced data
    recent_prescriptions = Prescription.query.filter_by(
        patient_id=current_user.id
    ).order_by(Prescription.created_at.desc()).limit(5).all()
    
    # Get upcoming appointments
    upcoming_appointments = Appointment.query.filter_by(
        patient_id=current_user.id
    ).filter(Appointment.date >= date.today()).order_by(Appointment.date.asc()).limit(3).all()
    
    # Get statistics
    total_appointments = Appointment.query.filter_by(patient_id=current_user.id).count()
    total_prescriptions = Prescription.query.filter_by(patient_id=current_user.id).count()
    active_prescriptions = Prescription.query.filter_by(
        patient_id=current_user.id, status='Active'
    ).count()
    upcoming_appointments_count = len(upcoming_appointments)
    
    # Get unique doctors count
    unique_doctors = db.session.query(Appointment.doctor_id).filter_by(
        patient_id=current_user.id
    ).distinct().count()
    
    # Get next appointment
    next_appointment = Appointment.query.filter_by(
        patient_id=current_user.id
    ).filter(Appointment.date >= date.today()).order_by(Appointment.date.asc()).first()
    
    return render_template('patient/dashboard.html',
                         recent_appointments=recent_appointments,
                         recent_prescriptions=recent_prescriptions,
                         upcoming_appointments=upcoming_appointments,
                         upcoming_appointments_count=upcoming_appointments_count,
                         total_appointments=total_appointments,
                         total_prescriptions=total_prescriptions,
                         active_prescriptions=active_prescriptions,
                         unique_doctors=unique_doctors,
                         next_appointment=next_appointment)


@bp.route('/reminders')
@login_required
def reminders():
    """View medication and appointment reminders"""
    if current_user.role != 'patient':
        flash('Access denied. Patients only.', 'error')
        return redirect(url_for('main.index'))
    
    # Get active prescriptions for medication reminders
    active_prescriptions = Prescription.query.filter_by(
        patient_id=current_user.id, status='Active'
    ).all()
    
    # Get upcoming appointments for appointment reminders
    upcoming_appointments = Appointment.query.filter_by(
        patient_id=current_user.id
    ).filter(Appointment.date >= date.today()).order_by(Appointment.date.asc()).all()
    
    # Create reminders list
    reminders = []
    
    # Add medication reminders
    for prescription in active_prescriptions:
        medications = PrescriptionMedication.query.filter_by(prescription_id=prescription.id).all()
        for medication in medications:
            reminders.append({
                'type': 'medication',
                'title': f'Take {medication.medication_name}',
                'description': f'Dosage: {medication.dosage}, Frequency: {medication.frequency}',
                'date': prescription.created_at.date() if prescription.created_at else date.today(),
                'doctor': prescription.doctor.first_name + ' ' + prescription.doctor.last_name
            })
    
    # Add appointment reminders
    for appointment in upcoming_appointments:
        reminders.append({
            'type': 'appointment',
            'title': f'Appointment with Dr. {appointment.doctor.first_name} {appointment.doctor.last_name}',
            'description': f'Time: {appointment.time}, Notes: {appointment.notes or "No notes"}',
            'date': appointment.date,
            'doctor': appointment.doctor.first_name + ' ' + appointment.doctor.last_name
        })
    
    # Sort reminders by date
    reminders.sort(key=lambda x: x['date'])
    
    return render_template('patient/reminders.html', reminders=reminders)


@bp.route('/prescription/<int:prescription_id>')
@login_required
def prescription_detail(prescription_id):
    """View detailed prescription information"""
    if current_user.role != 'patient':
        flash('Access denied. Patients only.', 'error')
        return redirect(url_for('main.index'))
    
    prescription = Prescription.query.filter_by(
        id=prescription_id, patient_id=current_user.id
    ).first_or_404()
    
    # Get prescription medications and lab tests
    medications = PrescriptionMedication.query.filter_by(prescription_id=prescription_id).all()
    lab_tests = LabTest.query.filter_by(prescription_id=prescription_id).all()
    
    # Get prescription edit history
    edits = PrescriptionEdit.query.filter_by(prescription_id=prescription_id).order_by(PrescriptionEdit.created_at.desc()).all()
    
    return render_template('patient/prescription_detail.html',
                         prescription=prescription,
                         medications=medications,
                         lab_tests=lab_tests,
                         edits=edits)


@bp.route('/doctors')
@login_required
def doctors():
    """View all doctors the patient has interacted with"""
    if current_user.role != 'patient':
        flash('Access denied. Patients only.', 'error')
        return redirect(url_for('main.index'))
    
    # Get doctors who have treated this patient
    doctors_query = db.session.query(User).join(
        Appointment, User.id == Appointment.doctor_id
    ).filter(
        and_(User.role == 'doctor', Appointment.patient_id == current_user.id)
    ).distinct()
    
    # Also include doctors who have prescribed medication
    doctors_with_prescriptions = db.session.query(User).join(
        Prescription, User.id == Prescription.doctor_id
    ).filter(
        and_(User.role == 'doctor', Prescription.patient_id == current_user.id)
    ).distinct()
    
    # Combine both queries
    all_doctors = doctors_query.union(doctors_with_prescriptions).all()
    
    # Get statistics for each doctor
    doctor_stats = {}
    for doctor in all_doctors:
        appointments_count = Appointment.query.filter_by(
            patient_id=current_user.id, doctor_id=doctor.id
        ).count()
        prescriptions_count = Prescription.query.filter_by(
            patient_id=current_user.id, doctor_id=doctor.id
        ).count()
        last_appointment = Appointment.query.filter_by(
            patient_id=current_user.id, doctor_id=doctor.id
        ).order_by(Appointment.date.desc()).first()
        
        doctor_stats[doctor.id] = {
            'appointments_count': appointments_count,
            'prescriptions_count': prescriptions_count,
            'last_appointment': last_appointment
        }
    
    return render_template('patient/doctors.html',
                         doctors=all_doctors,
                         doctor_stats=doctor_stats)


@bp.route('/medical_history')
@login_required
def medical_history():
    """View comprehensive medical history"""
    if current_user.role != 'patient':
        flash('Access denied. Patients only.', 'error')
        return redirect(url_for('main.index'))
    
    # Get all appointments with their details
    appointments = Appointment.query.filter_by(
        patient_id=current_user.id
    ).order_by(Appointment.date.desc()).all()
    
    # Get all prescriptions with medications and lab tests
    prescriptions = Prescription.query.filter_by(
        patient_id=current_user.id
    ).order_by(Prescription.created_at.desc()).all()
    
    # Get prescription medications and lab tests for each prescription
    prescription_details = {}
    for prescription in prescriptions:
        medications = PrescriptionMedication.query.filter_by(prescription_id=prescription.id).all()
        lab_tests = LabTest.query.filter_by(prescription_id=prescription.id).all()
        prescription_details[prescription.id] = {
            'medications': medications,
            'lab_tests': lab_tests
        }
    
    # Create a comprehensive timeline
    timeline = []
    
    # Add appointments to timeline
    for appointment in appointments:
        timeline.append({
            'date': appointment.date,
            'type': 'appointment',
            'data': appointment
        })
    
    # Add prescriptions to timeline
    for prescription in prescriptions:
        timeline.append({
            'date': prescription.created_at.date() if prescription.created_at else date.today(),
            'type': 'prescription',
            'data': prescription
        })
    
    # Sort timeline by date (newest first)
    timeline.sort(key=lambda x: x['date'], reverse=True)
    
    return render_template('patient/medical_history.html',
                         timeline=timeline,
                         prescription_details=prescription_details)


@bp.route('/profile')
@login_required
def profile():
    """View and edit patient profile"""
    if current_user.role != 'patient':
        flash('Access denied. Patients only.', 'error')
        return redirect(url_for('main.index'))
    
    # Get patient statistics
    total_appointments = Appointment.query.filter_by(patient_id=current_user.id).count()
    total_prescriptions = Prescription.query.filter_by(patient_id=current_user.id).count()
    
    # Get unique doctors count
    unique_doctors = db.session.query(Appointment.doctor_id).filter_by(
        patient_id=current_user.id
    ).distinct().count()
    
    # Get last visit
    last_appointment = Appointment.query.filter_by(
        patient_id=current_user.id
    ).order_by(Appointment.date.desc()).first()
    
    return render_template('patient/profile.html',
                         user=current_user,
                         total_appointments=total_appointments,
                         total_prescriptions=total_prescriptions,
                         unique_doctors=unique_doctors,
                         last_appointment=last_appointment)

@bp.route('/appointments')
@login_required
def appointments():
    if current_user.role != 'patient':
        flash('Access denied. Patients only.', 'error')
        return redirect(url_for('main.index'))
    
    # Enhanced appointments view with filtering
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', '')
    doctor_filter = request.args.get('doctor', '')
    date_filter = request.args.get('date_filter', '')
    
    query = Appointment.query.filter_by(patient_id=current_user.id)
    
    # Apply filters
    if status_filter:
        query = query.filter(Appointment.status == status_filter)
    
    if doctor_filter:
        query = query.filter(Appointment.doctor_id == doctor_filter)
    
    if date_filter:
        if date_filter == 'upcoming':
            query = query.filter(Appointment.date >= date.today())
        elif date_filter == 'past':
            query = query.filter(Appointment.date < date.today())
        elif date_filter == 'this_week':
            week_start = date.today() - timedelta(days=date.today().weekday())
            week_end = week_start + timedelta(days=6)
            query = query.filter(and_(Appointment.date >= week_start, Appointment.date <= week_end))
        elif date_filter == 'this_month':
            month_start = date.today().replace(day=1)
            next_month = month_start.replace(month=month_start.month + 1) if month_start.month < 12 else month_start.replace(year=month_start.year + 1, month=1)
            query = query.filter(and_(Appointment.date >= month_start, Appointment.date < next_month))
    
    appointments = query.order_by(Appointment.date.desc()).paginate(
        page=page, per_page=10, error_out=False
    )
    
    # Get doctors for filter dropdown
    doctors = db.session.query(User).join(
        Appointment, User.id == Appointment.doctor_id
    ).filter(
        and_(User.role == 'doctor', Appointment.patient_id == current_user.id)
    ).distinct().all()
    
    # Get appointment statistics
    total_appointments = Appointment.query.filter_by(patient_id=current_user.id).count()
    upcoming_appointments = Appointment.query.filter_by(
        patient_id=current_user.id
    ).filter(Appointment.date >= date.today()).count()
    
    return render_template('patient/appointments.html',
                         appointments=appointments,
                         doctors=doctors,
                         status_filter=status_filter,
                         doctor_filter=doctor_filter,
                         date_filter=date_filter,
                         total_appointments=total_appointments,
                         upcoming_appointments=upcoming_appointments)

@bp.route('/find-doctors', methods=['GET', 'POST'])
@login_required
def find_doctors():
    """Enhanced doctor listing page with search, filters, and booking"""
    if current_user.role != 'patient':
        flash('Access denied. Patients only.', 'error')
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        # Handle appointment booking
        doctor_id = request.form.get('doctor_id')
        appointment_date = request.form.get('appointment_date')
        appointment_time = request.form.get('appointment_time')
        appointment_type = request.form.get('appointment_type', 'in-person')
        reason = request.form.get('reason')
        
        if not all([doctor_id, appointment_date, appointment_time, reason]):
            flash('All fields are required', 'error')
        else:
            # Check if doctor exists
            doctor = User.query.filter_by(id=doctor_id, role='doctor').first()
            if not doctor:
                flash('Invalid doctor selected', 'error')
            else:
                # Create appointment
                appointment = Appointment(
                    patient_id=current_user.id,
                    doctor_id=doctor_id,
                    date=datetime.strptime(appointment_date, '%Y-%m-%d').date(),
                    time=datetime.strptime(appointment_time, '%H:%M').time(),
                    appointment_type=appointment_type,
                    reason=reason,
                    status='scheduled'
                )
                
                try:
                    db.session.add(appointment)
                    db.session.commit()
                    
                    # Send confirmation email to patient
                    try:
                        from app.utils.email import send_appointment_confirmation_email
                        send_appointment_confirmation_email(current_user, appointment, doctor)
                    except Exception as email_error:
                        print(f"Failed to send appointment confirmation email: {str(email_error)}")
                        # Don't fail the appointment booking if email fails
                    
                    flash(f'Appointment booked successfully with Dr. {doctor.first_name} {doctor.last_name}! Check your email for confirmation.', 'success')
                    return redirect(url_for('patient.appointments'))
                except Exception as e:
                    db.session.rollback()
                    flash('Error booking appointment. Please try again.', 'error')
    
    # GET request - show doctors with filters
    # Get filter parameters
    specialization = request.args.get('specialization', '')
    min_fee = request.args.get('min_fee', type=float)
    max_fee = request.args.get('max_fee', type=float)
    sort_by = request.args.get('sort', 'relevance')
    
    # Base query for active doctors
    query = User.query.filter_by(role='doctor', is_active=True)
    
    # Apply filters
    if specialization:
        query = query.filter(User.specialization.ilike(f'%{specialization}%'))
    
    if min_fee is not None:
        query = query.filter(User.consultation_fee >= min_fee)
    
    if max_fee is not None:
        query = query.filter(User.consultation_fee <= max_fee)
    
    # Apply sorting
    if sort_by == 'rating':
        query = query.order_by(User.rating.desc())
    elif sort_by == 'experience':
        query = query.order_by(User.experience.desc())
    elif sort_by == 'fee':
        query = query.order_by(User.consultation_fee.asc())
    else:  # relevance (default)
        query = query.order_by(User.rating.desc(), User.experience.desc())
    
    doctors = query.all()
    
    return render_template('patient/find_doctors.html', doctors=doctors)

@bp.route('/book-appointment', methods=['GET', 'POST'])
@login_required
def book_appointment():
    """Redirect to find-doctors page"""
    return redirect(url_for('patient.find_doctors'))

@bp.route('/prescriptions')
@login_required
def prescriptions():
    if current_user.role != 'patient':
        flash('Access denied. Patients only.', 'error')
        return redirect(url_for('main.index'))
    
    # Get prescriptions with enhanced filtering
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', '')
    doctor_filter = request.args.get('doctor', '')
    date_filter = request.args.get('date_filter', '')
    
    query = Prescription.query.filter_by(patient_id=current_user.id)
    
    # Apply filters
    if status_filter:
        query = query.filter(Prescription.status == status_filter)
    
    if doctor_filter:
        query = query.filter(Prescription.doctor_id == doctor_filter)
    
    if date_filter:
        if date_filter == 'last_week':
            week_ago = date.today() - timedelta(days=7)
            query = query.filter(Prescription.created_at >= week_ago)
        elif date_filter == 'last_month':
            month_ago = date.today() - timedelta(days=30)
            query = query.filter(Prescription.created_at >= month_ago)
        elif date_filter == 'last_3_months':
            three_months_ago = date.today() - timedelta(days=90)
            query = query.filter(Prescription.created_at >= three_months_ago)
    
    prescriptions = query.order_by(Prescription.created_at.desc()).paginate(
        page=page, per_page=10, error_out=False
    )
    
    # Get doctors for filter dropdown
    doctors = db.session.query(User).join(
        Prescription, User.id == Prescription.doctor_id
    ).filter(
        and_(User.role == 'doctor', Prescription.patient_id == current_user.id)
    ).distinct().all()
    
    # Get prescription statistics
    total_prescriptions = Prescription.query.filter_by(patient_id=current_user.id).count()
    active_prescriptions = Prescription.query.filter_by(
        patient_id=current_user.id, status='Active'
    ).count()
    
    return render_template('patient/prescriptions.html',
                         prescriptions=prescriptions,
                         doctors=doctors,
                         status_filter=status_filter,
                         doctor_filter=doctor_filter,
                         date_filter=date_filter,
                         total_prescriptions=total_prescriptions,
                         active_prescriptions=active_prescriptions)

# Real-time Appointment Status Routes

@bp.route('/appointment/<int:appointment_id>/status', methods=['GET'])
@login_required
def get_appointment_status(appointment_id):
    """Get current appointment status for patient"""
    if current_user.role != 'patient':
        return jsonify({'error': 'Access denied'}), 403
    
    appointment = Appointment.query.get_or_404(appointment_id)
    
    if appointment.patient_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Get doctor details
    doctor = User.query.get(appointment.doctor_id)
    
    return jsonify({
        'status': appointment.status,
        'started_at': appointment.started_at.strftime('%Y-%m-%d %H:%M:%S') if appointment.started_at else None,
        'completed_at': appointment.completed_at.strftime('%Y-%m-%d %H:%M:%S') if appointment.completed_at else None,
        'notes': appointment.notes,
        'doctor_name': f"Dr. {doctor.first_name} {doctor.last_name}",
        'doctor_phone': doctor.practice_phone,
        'practice_address': doctor.practice_address,
        'practice_city': doctor.practice_city,
        'practice_state': doctor.practice_state,
        'practice_zip_code': doctor.practice_zip_code,
        'practice_latitude': doctor.practice_latitude,
        'practice_longitude': doctor.practice_longitude
    })

@bp.route('/appointments/live')
@login_required
def live_appointments():
    """Get live appointments for today with real-time status"""
    if current_user.role != 'patient':
        flash('Access denied. Patients only.', 'error')
        return redirect(url_for('main.index'))
    
    today = date.today()
    appointments = db.session.query(Appointment, User).join(
        User, Appointment.doctor_id == User.id
    ).filter(
        Appointment.patient_id == current_user.id,
        Appointment.date == today
    ).order_by(Appointment.time.asc()).all()
    
    return render_template('patient/live_appointments.html', appointments=appointments, today=today)

@bp.route('/health-records')
@login_required
def health_records():
    """View comprehensive health records including medical history, test results, and vital signs"""
    if current_user.role != 'patient':
        flash('Access denied. Patients only.', 'error')
        return redirect(url_for('main.index'))
    
    # Get all appointments with doctor information for medical history
    medical_history = db.session.query(Appointment, User).join(
        User, Appointment.doctor_id == User.id
    ).filter(
        Appointment.patient_id == current_user.id,
        Appointment.status == 'completed'
    ).order_by(Appointment.date.desc()).all()
    
    # Get all prescriptions for medication history
    prescription_history = Prescription.query.filter_by(
        patient_id=current_user.id
    ).order_by(Prescription.created_at.desc()).all()
    
    # Group appointments by year for better organization
    appointments_by_year = {}
    for appointment, doctor in medical_history:
        year = appointment.date.year
        if year not in appointments_by_year:
            appointments_by_year[year] = []
        appointments_by_year[year].append((appointment, doctor))
    
    # Get health metrics (placeholder data - can be expanded with actual vital signs)
    health_metrics = {
        'blood_pressure': '120/80 mmHg',
        'heart_rate': '72 bpm',
        'temperature': '98.6°F',
        'weight': '70 kg',
        'height': '175 cm',
        'last_checkup': medical_history[0][0].date if medical_history else None
    }
    
    return render_template('patient/health_records.html',
                         medical_history=medical_history,
                         prescription_history=prescription_history,
                         appointments_by_year=appointments_by_year,
                         health_metrics=health_metrics)

@bp.route('/medical-documents')
@login_required
def medical_documents():
    """View and manage medical documents, test results, and reports"""
    if current_user.role != 'patient':
        flash('Access denied. Patients only.', 'error')
        return redirect(url_for('main.index'))
    
    # Placeholder for medical documents - can be expanded with file upload functionality
    documents = [
        {
            'name': 'Blood Test Results',
            'date': '2024-03-15',
            'type': 'Lab Report',
            'doctor': 'Dr. Smith',
            'status': 'Normal'
        },
        {
            'name': 'X-Ray Chest',
            'date': '2024-02-20',
            'type': 'Imaging',
            'doctor': 'Dr. Johnson',
            'status': 'Clear'
        },
        {
            'name': 'Annual Physical',
            'date': '2024-01-10',
            'type': 'Report',
            'doctor': 'Dr. Williams',
            'status': 'Complete'
        }
    ]
    
    return render_template('patient/medical_documents.html', documents=documents)
