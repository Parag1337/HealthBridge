from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.user import User
from app.models.appointment import Appointment
from app.models.prescription import Prescription
from app.models.prescription_components import PrescriptionMedication, LabTest, PrescriptionEdit
from app.models.scheduling import DoctorSchedule, SlotConfiguration, AvailabilityOverride, TimeSlot, RecurringSchedule
from app.utils.email import send_prescription_email
from datetime import datetime, date, timedelta, time
from sqlalchemy import and_, or_

bp = Blueprint('doctor', __name__, url_prefix='/doctor')

@bp.route('/home')
@login_required
def home():
    """Minimal focused home page for doctors"""
    if current_user.role != 'doctor':
        flash('Access denied. Doctors only.', 'error')
        return redirect(url_for('main.index'))
    
    today = date.today()
    
    # Get today's appointments with patient details
    today_appointments = db.session.query(Appointment, User).join(
        User, Appointment.patient_id == User.id
    ).filter(
        Appointment.doctor_id == current_user.id,
        Appointment.date == today
    ).order_by(Appointment.time.asc()).all()
    
    # Get current patients (patients with appointments in last 30 days)
    thirty_days_ago = today - timedelta(days=30)
    recent_patient_ids = db.session.query(Appointment.patient_id).filter(
        Appointment.doctor_id == current_user.id,
        Appointment.date >= thirty_days_ago
    ).distinct().subquery()
    
    current_patients = db.session.query(User).join(recent_patient_ids, User.id == recent_patient_ids.c.patient_id).all()
    
    # Next appointment
    next_appointment = None
    current_time = datetime.now().time()
    for apt, patient in today_appointments:
        if apt.status == 'scheduled' and apt.time >= current_time:
            next_appointment = (apt, patient)
            break
    
    # Statistics
    total_today = len(today_appointments)
    completed_today = len([apt for apt, patient in today_appointments if apt.status == 'completed'])
    pending_today = len([apt for apt, patient in today_appointments if apt.status == 'scheduled'])
    
    return render_template('doctor/home.html',
                         today_appointments=today_appointments,
                         current_patients=current_patients[:6],  # Show only 6 recent patients
                         next_appointment=next_appointment,
                         total_today=total_today,
                         completed_today=completed_today,
                         pending_today=pending_today,
                         today=today)

@bp.route('/dashboard')
@login_required
def dashboard():
    """Redirect dashboard to home page"""
    return redirect(url_for('doctor.home'))

@bp.route('/complete-appointment/<int:appointment_id>', methods=['POST'])
@login_required
def complete_appointment(appointment_id):
    if current_user.role != 'doctor':
        return jsonify({'error': 'Access denied'}), 403
    
    appointment = Appointment.query.filter_by(
        id=appointment_id,
        doctor_id=current_user.id
    ).first()
    
    if not appointment:
        return jsonify({'error': 'Appointment not found'}), 404
    
    appointment.status = 'completed'
    
    try:
        db.session.commit()
        return jsonify({'success': True, 'message': 'Appointment completed successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to complete appointment'}), 500

@bp.route('/call-next-patient', methods=['POST'])
@login_required
def call_next_patient():
    if current_user.role != 'doctor':
        return jsonify({'error': 'Access denied'}), 403
    
    # Find next scheduled appointment for today
    next_appointment = Appointment.query.filter_by(
        doctor_id=current_user.id,
        date=date.today(),
        status='scheduled'
    ).order_by(Appointment.time.asc()).first()
    
    if not next_appointment:
        return jsonify({'error': 'No more patients waiting'}), 404
    
    # Mark as in-progress
    next_appointment.status = 'in-progress'
    
    try:
        db.session.commit()
        patient = User.query.get(next_appointment.patient_id)
        return jsonify({
            'success': True,
            'message': f'Called {patient.first_name} {patient.last_name}',
            'appointment_id': next_appointment.id,
            'patient_name': f'{patient.first_name} {patient.last_name}'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to call next patient'}), 500

@bp.route('/start-appointment/<int:appointment_id>', methods=['POST'])
@login_required
def start_appointment(appointment_id):
    if current_user.role != 'doctor':
        return jsonify({'error': 'Access denied'}), 403
    
    appointment = Appointment.query.filter_by(
        id=appointment_id,
        doctor_id=current_user.id
    ).first()
    
    if not appointment:
        return jsonify({'error': 'Appointment not found'}), 404
    
    appointment.status = 'in-progress'
    
    try:
        db.session.commit()
        patient = User.query.get(appointment.patient_id)
        return jsonify({
            'success': True,
            'message': f'Started appointment with {patient.first_name} {patient.last_name}',
            'appointment_id': appointment.id
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to start appointment'}), 500

@bp.route('/patients')
@login_required
def patients():
    """View all patients who have had appointments with this doctor"""
    if current_user.role != 'doctor':
        flash('Access denied. Doctors only.', 'error')
        return redirect(url_for('main.index'))
    
    # Get all unique patients who have had appointments with this doctor
    # Fixed: Use distinct() properly and access the correct column name
    patient_ids_subquery = db.session.query(Appointment.patient_id).filter_by(
        doctor_id=current_user.id
    ).distinct().subquery()
    
    patients = db.session.query(User).join(
        patient_ids_subquery, User.id == patient_ids_subquery.c.patient_id
    ).all()
    
    # Get last appointment date for each patient
    patients_data = []
    for patient in patients:
        last_appointment = Appointment.query.filter_by(
            doctor_id=current_user.id,
            patient_id=patient.id
        ).order_by(Appointment.date.desc()).first()
        
        # Get total appointment count for this patient
        appointment_count = Appointment.query.filter_by(
            doctor_id=current_user.id,
            patient_id=patient.id
        ).count()
        
        patients_data.append({
            'patient': patient,
            'last_appointment': last_appointment,
            'appointment_count': appointment_count
        })
    
    return render_template('doctor/patients.html', patients_data=patients_data)

@bp.route('/current-patients')
@login_required
def current_patients():
    """View patients with upcoming or recent appointments"""
    if current_user.role != 'doctor':
        flash('Access denied. Doctors only.', 'error')
        return redirect(url_for('main.index'))
    
    # Get patients with appointments in the last 30 days or upcoming appointments
    from datetime import timedelta
    thirty_days_ago = date.today() - timedelta(days=30)
    
    recent_appointments = Appointment.query.filter(
        and_(
            Appointment.doctor_id == current_user.id,
            or_(
                Appointment.date >= thirty_days_ago,
                Appointment.date >= date.today()
            )
        )
    ).order_by(Appointment.date.desc()).all()
    
    # Group by patient
    patients_dict = {}
    for appointment in recent_appointments:
        patient_id = appointment.patient_id
        if patient_id not in patients_dict:
            patients_dict[patient_id] = {
                'patient': appointment.patient,
                'appointments': []
            }
        patients_dict[patient_id]['appointments'].append(appointment)
    
    current_patients_data = list(patients_dict.values())
    
    return render_template('doctor/current_patients.html', 
                         patients_data=current_patients_data,
                         today=date.today())

@bp.route('/prescriptions')
@login_required
def prescriptions():
    """View all prescriptions created by this doctor"""
    if current_user.role != 'doctor':
        flash('Access denied. Doctors only.', 'error')
        return redirect(url_for('main.index'))
    
    page = request.args.get('page', 1, type=int)
    prescriptions = Prescription.query.filter_by(
        doctor_id=current_user.id
    ).order_by(Prescription.created_at.desc()).paginate(
        page=page, per_page=10, error_out=False
    )
    
    return render_template('doctor/prescriptions.html', prescriptions=prescriptions)

@bp.route('/create-prescription/<int:patient_id>', methods=['GET', 'POST'])
@login_required
def create_prescription(patient_id):
    """Create a new prescription for a patient with multiple medications and lab tests"""
    if current_user.role != 'doctor':
        flash('Access denied. Doctors only.', 'error')
        return redirect(url_for('main.index'))
    
    # Verify that this patient has had appointments with this doctor
    patient = User.query.filter_by(id=patient_id, role='patient').first()
    if not patient:
        flash('Patient not found.', 'error')
        return redirect(url_for('doctor.patients'))
    
    # Check if doctor has treated this patient
    appointment_exists = Appointment.query.filter_by(
        doctor_id=current_user.id,
        patient_id=patient_id
    ).first()
    
    if not appointment_exists:
        flash('You can only prescribe medications to your patients.', 'error')
        return redirect(url_for('doctor.patients'))
    
    if request.method == 'GET':
        return render_template('doctor/create_prescription.html', patient=patient)
    
    # Handle POST request
    try:
        from app.models.prescription_components import PrescriptionMedication, LabTest
        
        # Get basic prescription data
        prescribed_date_str = request.form.get('prescribed_date')
        status = request.form.get('status', 'Active')
        notes = request.form.get('notes', '')
        
        # Parse prescribed date
        try:
            if prescribed_date_str:
                prescribed_date = datetime.strptime(prescribed_date_str, '%Y-%m-%d').date()
            else:
                prescribed_date = date.today()
        except ValueError:
            prescribed_date = date.today()
        
        # Process medications
        medications_data = []
        form_keys = list(request.form.keys())
        
        # Extract medication indices
        medication_indices = set()
        for key in form_keys:
            if key.startswith('medications[') and '][name]' in key:
                index = key.split('[')[1].split(']')[0]
                medication_indices.add(int(index))
        
        # Validate at least one medication
        if not medication_indices:
            flash('At least one medication is required.', 'error')
            return render_template('doctor/create_prescription.html', patient=patient)
        
        # Collect medication data
        for index in medication_indices:
            med_name = request.form.get(f'medications[{index}][name]')
            med_dosage = request.form.get(f'medications[{index}][dosage]')
            med_frequency = request.form.get(f'medications[{index}][frequency]')
            med_duration = request.form.get(f'medications[{index}][duration]')
            med_instructions = request.form.get(f'medications[{index}][instructions]', '')
            
            # Validate required fields
            if not med_name or not med_dosage or not med_frequency or not med_duration:
                flash(f'Please fill in all required fields for medication #{index + 1}.', 'error')
                return render_template('doctor/create_prescription.html', patient=patient)
            
            medications_data.append({
                'name': med_name,
                'dosage': med_dosage,
                'frequency': med_frequency,
                'duration': med_duration,
                'instructions': med_instructions
            })
        
        # Process lab tests
        lab_tests_data = []
        lab_test_indices = set()
        for key in form_keys:
            if key.startswith('lab_tests[') and '][name]' in key:
                index = key.split('[')[1].split(']')[0]
                lab_test_indices.add(int(index))
        
        # Collect lab test data
        for index in lab_test_indices:
            test_name = request.form.get(f'lab_tests[{index}][name]')
            test_type = request.form.get(f'lab_tests[{index}][type]')
            suggested_date_str = request.form.get(f'lab_tests[{index}][suggested_date]')
            priority = request.form.get(f'lab_tests[{index}][priority]', 'Normal')
            test_instructions = request.form.get(f'lab_tests[{index}][instructions]', '')
            
            # Validate required fields
            if not test_name or not test_type:
                flash(f'Please fill in all required fields for lab test #{index + 1}.', 'error')
                return render_template('doctor/create_prescription.html', patient=patient)
            
            # Parse suggested date
            suggested_date = None
            if suggested_date_str:
                try:
                    suggested_date = datetime.strptime(suggested_date_str, '%Y-%m-%d').date()
                except ValueError:
                    flash(f'Invalid suggested date for lab test #{index + 1}.', 'error')
                    return render_template('doctor/create_prescription.html', patient=patient)
            
            lab_tests_data.append({
                'name': test_name,
                'type': test_type,
                'suggested_date': suggested_date,
                'priority': priority,
                'instructions': test_instructions
            })
        
        # Create prescription with backward compatibility
        first_medication = medications_data[0]
        prescription = Prescription(
            patient_id=patient_id,
            doctor_id=current_user.id,
            medication_name=first_medication['name'],  # For backward compatibility
            dosage=first_medication['dosage'],  # For backward compatibility
            frequency=first_medication['frequency'],  # For backward compatibility
            duration=first_medication['duration'],  # For backward compatibility
            instructions=first_medication['instructions'],  # For backward compatibility
            prescribed_date=prescribed_date,
            status=status,
            notes=notes
        )
        
        db.session.add(prescription)
        db.session.flush()  # Get the prescription ID
        
        # Add all medications
        for med_data in medications_data:
            medication = PrescriptionMedication(
                prescription_id=prescription.id,
                medication_name=med_data['name'],
                dosage=med_data['dosage'],
                frequency=med_data['frequency'],
                duration=med_data['duration'],
                instructions=med_data['instructions']
            )
            db.session.add(medication)
        
        # Add lab tests
        for test_data in lab_tests_data:
            lab_test = LabTest(
                prescription_id=prescription.id,
                test_name=test_data['name'],
                test_type=test_data['type'],
                suggested_date=test_data['suggested_date'],
                priority=test_data['priority'],
                instructions=test_data['instructions'],
                status='Pending',
                ordered_by=current_user.id
            )
            db.session.add(lab_test)
        
        db.session.commit()
        
        # Get the created medications and lab tests for email
        created_medications = PrescriptionMedication.query.filter_by(prescription_id=prescription.id).all()
        created_lab_tests = LabTest.query.filter_by(prescription_id=prescription.id).all()
        
        # Send prescription email to patient
        try:
            send_prescription_email(patient, prescription, current_user, created_medications, created_lab_tests)
        except Exception as email_error:
            print(f"Failed to send prescription email: {str(email_error)}")
            # Don't fail the prescription creation if email fails
        
        med_count = len(medications_data)
        test_count = len(lab_tests_data)
        
        success_msg = f'Prescription created successfully for {patient.first_name} {patient.last_name} with {med_count} medication(s)'
        if test_count > 0:
            success_msg += f' and {test_count} lab test(s)'
        success_msg += '! Patient has been notified via email.'
        
        flash(success_msg, 'success')
        return redirect(url_for('doctor.prescriptions'))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error creating prescription: {str(e)}', 'error')
        return render_template('doctor/create_prescription.html', patient=patient)


@bp.route('/prescription/<int:prescription_id>')
@login_required
def prescription_detail(prescription_id):
    """View detailed prescription information with PDF export capability"""
    if current_user.role != 'doctor':
        flash('Access denied. Doctors only.', 'error')
        return redirect(url_for('main.index'))
    
    prescription = Prescription.query.filter_by(
        id=prescription_id, doctor_id=current_user.id
    ).first_or_404()
    
    # Get prescription medications and lab tests
    medications = PrescriptionMedication.query.filter_by(prescription_id=prescription_id).all()
    lab_tests = LabTest.query.filter_by(prescription_id=prescription_id).all()
    
    # Get prescription edit history
    edits = PrescriptionEdit.query.filter_by(prescription_id=prescription_id).order_by(PrescriptionEdit.created_at.desc()).all()
    
    return render_template('doctor/prescription_detail.html',
                         prescription=prescription,
                         medications=medications,
                         lab_tests=lab_tests,
                         edits=edits)

# Appointment Status Management Routes

@bp.route('/appointment/<int:appointment_id>/start-session', methods=['POST'])
@login_required
def start_appointment_session(appointment_id):
    """Start an appointment - change status to in-progress"""
    if current_user.role != 'doctor':
        return jsonify({'error': 'Access denied'}), 403
    
    appointment = Appointment.query.get_or_404(appointment_id)
    
    if appointment.doctor_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    if appointment.status != 'scheduled':
        return jsonify({'error': 'Appointment cannot be started'}), 400
    
    try:
        appointment.status = 'in-progress'
        appointment.started_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Appointment started successfully',
            'status': 'in-progress',
            'started_at': appointment.started_at.strftime('%Y-%m-%d %H:%M:%S')
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/appointment/<int:appointment_id>/complete-session', methods=['POST'])
@login_required
def complete_appointment_session(appointment_id):
    """Complete an appointment - change status to completed"""
    if current_user.role != 'doctor':
        return jsonify({'error': 'Access denied'}), 403
    
    appointment = Appointment.query.get_or_404(appointment_id)
    
    if appointment.doctor_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    if appointment.status not in ['scheduled', 'in-progress']:
        return jsonify({'error': 'Appointment cannot be completed'}), 400
    
    notes = request.json.get('notes', '') if request.is_json else request.form.get('notes', '')
    
    try:
        appointment.status = 'completed'
        appointment.completed_at = datetime.utcnow()
        if notes:
            appointment.notes = notes
        
        # Set started_at if not already set
        if not appointment.started_at:
            appointment.started_at = appointment.completed_at
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Appointment completed successfully',
            'status': 'completed',
            'completed_at': appointment.completed_at.strftime('%Y-%m-%d %H:%M:%S')
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/appointment/<int:appointment_id>/status', methods=['GET'])
@login_required
def get_appointment_status(appointment_id):
    """Get current appointment status"""
    appointment = Appointment.query.get_or_404(appointment_id)
    
    # Allow both doctor and patient to check status
    if appointment.doctor_id != current_user.id and appointment.patient_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    return jsonify({
        'status': appointment.status,
        'started_at': appointment.started_at.strftime('%Y-%m-%d %H:%M:%S') if appointment.started_at else None,
        'completed_at': appointment.completed_at.strftime('%Y-%m-%d %H:%M:%S') if appointment.completed_at else None,
        'notes': appointment.notes
    })

@bp.route('/practice-settings', methods=['GET', 'POST'])
@login_required
def practice_settings():
    """Manage doctor's practice information"""
    if current_user.role != 'doctor':
        flash('Access denied. Doctors only.', 'error')
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        try:
            current_user.practice_address = request.form.get('practice_address')
            current_user.practice_city = request.form.get('practice_city')
            current_user.practice_state = request.form.get('practice_state')
            current_user.practice_zip_code = request.form.get('practice_zip_code')
            current_user.practice_phone = request.form.get('practice_phone')
            
            # Handle latitude and longitude
            lat = request.form.get('practice_latitude')
            lng = request.form.get('practice_longitude')
            
            current_user.practice_latitude = float(lat) if lat else None
            current_user.practice_longitude = float(lng) if lng else None
            
            db.session.commit()
            flash('Practice information updated successfully!', 'success')
            return redirect(url_for('doctor.practice_settings'))
            
        except ValueError as e:
            flash('Invalid latitude or longitude format.', 'error')
        except Exception as e:
            db.session.rollback()
            flash('Failed to update practice information. Please try again.', 'error')
    
    return render_template('doctor/practice_settings.html')

@bp.route('/appointments')
@login_required
def appointments():
    """View today's appointments"""
    if current_user.role != 'doctor':
        flash('Access denied. Doctors only.', 'error')
        return redirect(url_for('main.index'))
    
    today = date.today()
    
    # Get today's appointments with patient details
    today_appointments = db.session.query(Appointment, User).join(
        User, Appointment.patient_id == User.id
    ).filter(
        Appointment.doctor_id == current_user.id,
        Appointment.date == today
    ).order_by(Appointment.time.asc()).all()
    
    # Separate by status for the enhanced template
    scheduled_appointments = [(apt, patient) for apt, patient in today_appointments if apt.status == 'scheduled']
    in_progress_appointments = [(apt, patient) for apt, patient in today_appointments if apt.status == 'in-progress']
    completed_appointments = [(apt, patient) for apt, patient in today_appointments if apt.status == 'completed']
    
    # Get current time for display
    current_time = datetime.now().strftime('%I:%M %p')
    
    return render_template('doctor/appointments.html',
                         scheduled_appointments=scheduled_appointments,
                         in_progress_appointments=in_progress_appointments,
                         completed_appointments=completed_appointments,
                         scheduled_count=len(scheduled_appointments),
                         in_progress_count=len(in_progress_appointments),
                         completed_count=len(completed_appointments),
                         total_count=len(today_appointments),
                         current_time=current_time,
                         today=today)

@bp.route('/appointment/<int:appointment_id>/start', methods=['POST'])
@login_required
def start_appointment_new(appointment_id):
    """Start an appointment (new enhanced version)"""
    if current_user.role != 'doctor':
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    appointment = Appointment.query.get_or_404(appointment_id)
    
    if appointment.doctor_id != current_user.id:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    if appointment.status != 'scheduled':
        return jsonify({'success': False, 'message': 'Appointment cannot be started'}), 400
    
    # Update appointment status
    appointment.status = 'in-progress'
    appointment.started_at = datetime.utcnow()
    
    try:
        db.session.commit()
        return jsonify({'success': True, 'message': 'Appointment started successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Failed to start appointment'}), 500

@bp.route('/appointment/<int:appointment_id>/complete', methods=['POST'])
@login_required
def complete_appointment_new(appointment_id):
    """Complete an appointment (new enhanced version)"""
    if current_user.role != 'doctor':
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    appointment = Appointment.query.get_or_404(appointment_id)
    
    if appointment.doctor_id != current_user.id:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    if appointment.status != 'in-progress':
        return jsonify({'success': False, 'message': 'Appointment cannot be completed'}), 400
    
    # Update appointment status
    appointment.status = 'completed'
    appointment.completed_at = datetime.utcnow()
    
    try:
        db.session.commit()
        return jsonify({'success': True, 'message': 'Appointment completed successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Failed to complete appointment'}), 500

# Scheduling Management Routes

@bp.route('/schedule-settings', methods=['GET', 'POST'])
@login_required
def schedule_settings():
    """Manage doctor's schedule settings and working hours"""
    if current_user.role != 'doctor':
        flash('Access denied. Doctors only.', 'error')
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        try:
            # Get or create slot configuration
            slot_config = SlotConfiguration.query.filter_by(doctor_id=current_user.id).first()
            if not slot_config:
                slot_config = SlotConfiguration(doctor_id=current_user.id)
                db.session.add(slot_config)
            
            # Update slot configuration
            slot_config.slot_duration_minutes = int(request.form.get('slot_duration_minutes', 30))
            slot_config.buffer_time_minutes = int(request.form.get('buffer_time_minutes', 5))
            slot_config.max_patients_per_day = int(request.form.get('max_patients_per_day', 20))
            slot_config.advance_booking_days = int(request.form.get('advance_booking_days', 30))
            slot_config.last_minute_booking_hours = int(request.form.get('last_minute_booking_hours', 2))
            slot_config.auto_generate_slots = request.form.get('auto_generate_slots') == 'on'
            slot_config.updated_at = datetime.utcnow()
            
            # Clear existing schedules for this doctor
            DoctorSchedule.query.filter_by(doctor_id=current_user.id).delete()
            
            # Process weekly schedule
            days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
            for day_index, day_name in enumerate(days):
                is_working = request.form.get(f'{day_name}_working') == 'on'
                if is_working:
                    start_time_str = request.form.get(f'{day_name}_start_time')
                    end_time_str = request.form.get(f'{day_name}_end_time')
                    
                    if start_time_str and end_time_str:
                        start_time = datetime.strptime(start_time_str, '%H:%M').time()
                        end_time = datetime.strptime(end_time_str, '%H:%M').time()
                        
                        schedule = DoctorSchedule(
                            doctor_id=current_user.id,
                            day_of_week=day_index,
                            start_time=start_time,
                            end_time=end_time,
                            is_active=True
                        )
                        db.session.add(schedule)
            
            db.session.commit()
            flash('Schedule settings updated successfully!', 'success')
            return redirect(url_for('doctor.schedule_settings'))
            
        except (ValueError, TypeError) as e:
            flash('Invalid time format or numeric values. Please check your input.', 'error')
        except Exception as e:
            db.session.rollback()
            flash(f'Failed to update schedule settings: {str(e)}', 'error')
    
    # Get current settings
    slot_config = SlotConfiguration.query.filter_by(doctor_id=current_user.id).first()
    schedules = DoctorSchedule.query.filter_by(doctor_id=current_user.id, is_active=True).all()
    
    # Convert schedules to a more convenient format
    weekly_schedule = {}
    for schedule in schedules:
        weekly_schedule[schedule.day_of_week] = {
            'start_time': schedule.start_time,
            'end_time': schedule.end_time
        }
    
    return render_template('doctor/schedule_settings.html', 
                         slot_config=slot_config, 
                         weekly_schedule=weekly_schedule)

@bp.route('/availability-overrides', methods=['GET', 'POST'])
@login_required
def availability_overrides():
    """Manage doctor's availability exceptions and overrides"""
    if current_user.role != 'doctor':
        flash('Access denied. Doctors only.', 'error')
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        try:
            override_date_str = request.form.get('override_date')
            override_type = request.form.get('override_type')
            reason = request.form.get('reason', '')
            
            if not override_date_str or not override_type:
                flash('Date and override type are required.', 'error')
                return redirect(url_for('doctor.availability_overrides'))
            
            override_date = datetime.strptime(override_date_str, '%Y-%m-%d').date()
            
            # Check if override already exists for this date
            existing = AvailabilityOverride.query.filter_by(
                doctor_id=current_user.id,
                date=override_date,
                is_active=True
            ).first()
            
            if existing:
                flash(f'Override already exists for {override_date}. Please edit or delete the existing one.', 'error')
                return redirect(url_for('doctor.availability_overrides'))
            
            # Create new override
            override = AvailabilityOverride(
                doctor_id=current_user.id,
                date=override_date,
                override_type=override_type,
                reason=reason
            )
            
            # Handle custom hours
            if override_type == 'custom_hours':
                start_time_str = request.form.get('start_time')
                end_time_str = request.form.get('end_time')
                
                if not start_time_str or not end_time_str:
                    flash('Start and end times are required for custom hours.', 'error')
                    return redirect(url_for('doctor.availability_overrides'))
                
                override.start_time = datetime.strptime(start_time_str, '%H:%M').time()
                override.end_time = datetime.strptime(end_time_str, '%H:%M').time()
            
            db.session.add(override)
            db.session.commit()
            
            flash(f'Availability override created for {override_date}!', 'success')
            return redirect(url_for('doctor.availability_overrides'))
            
        except ValueError as e:
            flash('Invalid date or time format.', 'error')
        except Exception as e:
            db.session.rollback()
            flash(f'Failed to create override: {str(e)}', 'error')
    
    # Get current and future overrides
    current_overrides = AvailabilityOverride.query.filter_by(
        doctor_id=current_user.id,
        is_active=True
    ).filter(
        AvailabilityOverride.date >= date.today()
    ).order_by(AvailabilityOverride.date.asc()).all()
    
    return render_template('doctor/availability_overrides.html', overrides=current_overrides)

@bp.route('/delete-override/<int:override_id>', methods=['POST'])
@login_required
def delete_override(override_id):
    """Delete an availability override"""
    if current_user.role != 'doctor':
        return jsonify({'error': 'Access denied'}), 403
    
    override = AvailabilityOverride.query.filter_by(
        id=override_id,
        doctor_id=current_user.id
    ).first()
    
    if not override:
        return jsonify({'error': 'Override not found'}), 404
    
    try:
        override.is_active = False
        db.session.commit()
        return jsonify({'success': True, 'message': 'Override deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/schedule-overview')
@login_required
def schedule_overview():
    """View doctor's complete schedule overview"""
    if current_user.role != 'doctor':
        flash('Access denied. Doctors only.', 'error')
        return redirect(url_for('main.index'))
    
    # Get slot configuration
    slot_config = SlotConfiguration.query.filter_by(doctor_id=current_user.id).first()
    
    # Get weekly schedule
    schedules = DoctorSchedule.query.filter_by(doctor_id=current_user.id, is_active=True).all()
    weekly_schedule = {}
    for schedule in schedules:
        weekly_schedule[schedule.day_of_week] = {
            'start_time': schedule.start_time,
            'end_time': schedule.end_time
        }
    
    # Get upcoming overrides
    upcoming_overrides = AvailabilityOverride.query.filter_by(
        doctor_id=current_user.id,
        is_active=True
    ).filter(
        AvailabilityOverride.date >= date.today()
    ).order_by(AvailabilityOverride.date.asc()).limit(10).all()
    
    # Get upcoming appointments for next 7 days
    next_week = date.today() + timedelta(days=7)
    upcoming_appointments = Appointment.query.filter_by(
        doctor_id=current_user.id
    ).filter(
        and_(
            Appointment.date >= date.today(),
            Appointment.date <= next_week
        )
    ).order_by(Appointment.date.asc(), Appointment.time.asc()).all()
    
    # Group appointments by date
    appointments_by_date = {}
    for appointment in upcoming_appointments:
        if appointment.date not in appointments_by_date:
            appointments_by_date[appointment.date] = []
        appointments_by_date[appointment.date].append(appointment)
    
    return render_template('doctor/schedule_overview.html',
                         slot_config=slot_config,
                         weekly_schedule=weekly_schedule,
                         upcoming_overrides=upcoming_overrides,
                         appointments_by_date=appointments_by_date)
