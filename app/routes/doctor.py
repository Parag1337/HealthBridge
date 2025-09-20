from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.user import User
from app.models.appointment import Appointment
from app.models.prescription import Prescription
from app.models.prescription_components import PrescriptionMedication, LabTest, PrescriptionEdit
from app.utils.email import send_prescription_email
from datetime import datetime, date, timedelta
from sqlalchemy import and_, or_

bp = Blueprint('doctor', __name__, url_prefix='/doctor')

@bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.role != 'doctor':
        flash('Access denied. Doctors only.', 'error')
        return redirect(url_for('main.index'))
    
    # Get today's appointments with patient details
    today_appointments = db.session.query(Appointment, User).join(
        User, Appointment.patient_id == User.id
    ).filter(
        Appointment.doctor_id == current_user.id,
        Appointment.date == date.today()
    ).order_by(Appointment.time.asc()).all()
    
    # Get upcoming appointments (next 7 days)
    upcoming_appointments = db.session.query(Appointment, User).join(
        User, Appointment.patient_id == User.id
    ).filter(
        Appointment.doctor_id == current_user.id,
        Appointment.date > date.today(),
        Appointment.date <= date.today() + timedelta(days=7)
    ).order_by(Appointment.date.asc(), Appointment.time.asc()).limit(10).all()
    
    # Get total statistics
    total_patients = db.session.query(Appointment.patient_id).filter_by(
        doctor_id=current_user.id
    ).distinct().count()
    
    total_appointments_today = len(today_appointments)
    completed_today = len([apt for apt, patient in today_appointments if apt.status == 'completed'])
    
    # Get current appointment (next scheduled or in-progress)
    current_time = datetime.now().time()
    current_appointment = None
    next_appointment = None
    
    for apt, patient in today_appointments:
        if apt.status in ['scheduled', 'in-progress'] and apt.time <= current_time:
            current_appointment = (apt, patient)
            break
    
    # Get next waiting appointment
    for apt, patient in today_appointments:
        if apt.status == 'scheduled' and apt.time > current_time:
            next_appointment = (apt, patient)
            break
    
    return render_template('doctor/dashboard.html',
                         today_appointments=today_appointments,
                         upcoming_appointments=upcoming_appointments,
                         total_patients=total_patients,
                         total_appointments_today=total_appointments_today,
                         completed_today=completed_today,
                         current_appointment=current_appointment,
                         next_appointment=next_appointment,
                         current_time=current_time)

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
