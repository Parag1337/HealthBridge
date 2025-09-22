from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.appointment import Appointment
from app.models.telemedicine import VideoConsultation
from app.models.scheduling import DoctorSchedule, SlotConfiguration
from datetime import datetime, date, timedelta, time
import secrets

bp = Blueprint('telemedicine', __name__, url_prefix='/telemedicine')

def get_doctor_available_slots(doctor_id, selected_date=None):
    """Get available time slots for a doctor based on their schedule settings"""
    # Get doctor's slot configuration
    slot_config = SlotConfiguration.query.filter_by(doctor_id=doctor_id).first()
    if not slot_config:
        # Default configuration if none exists
        slot_duration = 30
    else:
        slot_duration = slot_config.slot_duration_minutes
    
    # Get doctor's schedule for the day of week
    if selected_date:
        target_date = datetime.strptime(selected_date, '%Y-%m-%d').date()
        day_of_week = target_date.weekday()  # 0=Monday, 6=Sunday
    else:
        day_of_week = None
    
    # Get doctor's working hours for the day
    if day_of_week is not None:
        schedule = DoctorSchedule.query.filter_by(
            doctor_id=doctor_id, 
            day_of_week=day_of_week,
            is_active=True
        ).first()
        
        if schedule:
            # Generate time slots based on working hours
            slots = []
            current_time = datetime.combine(date.today(), schedule.start_time)
            end_time = datetime.combine(date.today(), schedule.end_time)
            
            while current_time < end_time:
                slots.append({
                    'value': current_time.strftime('%H:%M'),
                    'label': current_time.strftime('%I:%M %p')
                })
                current_time += timedelta(minutes=slot_duration)
            
            return slots
    
    # Default time slots if no schedule found
    default_slots = [
        {'value': '09:00', 'label': '9:00 AM'},
        {'value': '09:30', 'label': '9:30 AM'},
        {'value': '10:00', 'label': '10:00 AM'},
        {'value': '10:30', 'label': '10:30 AM'},
        {'value': '11:00', 'label': '11:00 AM'},
        {'value': '11:30', 'label': '11:30 AM'},
        {'value': '14:00', 'label': '2:00 PM'},
        {'value': '14:30', 'label': '2:30 PM'},
        {'value': '15:00', 'label': '3:00 PM'},
        {'value': '15:30', 'label': '3:30 PM'},
        {'value': '16:00', 'label': '4:00 PM'},
        {'value': '16:30', 'label': '4:30 PM'},
        {'value': '17:00', 'label': '5:00 PM'},
    ]
    return default_slots

@bp.route('/consultation/<int:appointment_id>')
@login_required
def video_consultation(appointment_id):
    """Join video consultation for an appointment"""
    appointment = Appointment.query.get_or_404(appointment_id)
    
    # Verify user can access this consultation
    if current_user.role == 'patient' and appointment.patient_id != current_user.id:
        flash('You can only join your own consultations.', 'error')
        return redirect(url_for('patient.dashboard'))
    elif current_user.role == 'doctor' and appointment.doctor_id != current_user.id:
        flash('You can only join consultations you are assigned to.', 'error')
        return redirect(url_for('doctor.dashboard'))
    
    # Check if appointment is telemedicine
    if not appointment.is_telemedicine():
        flash('This appointment is not a telemedicine consultation.', 'error')
        return redirect(url_for('appointment.view_appointments'))
    
    # Get or create video consultation
    consultation = appointment.video_consultation
    if not consultation:
        consultation = VideoConsultation(
            appointment_id=appointment.id,
            patient_id=appointment.patient_id,
            doctor_id=appointment.doctor_id
        )
        db.session.add(consultation)
        db.session.commit()
    
    return render_template('telemedicine/video_consultation.html', 
                         appointment=appointment, 
                         consultation=consultation)

@bp.route('/consultation/<int:consultation_id>/join', methods=['POST'])
@login_required
def join_consultation(consultation_id):
    """Mark user as joined to consultation"""
    consultation = VideoConsultation.query.get_or_404(consultation_id)
    
    # Verify user can join this consultation
    if current_user.role == 'patient' and consultation.patient_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    elif current_user.role == 'doctor' and consultation.doctor_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Mark user as joined
    if current_user.role == 'patient':
        consultation.patient_join()
    else:
        consultation.doctor_join()
    
    # If both users have joined and consultation is scheduled, start it
    if (consultation.patient_joined_at and consultation.doctor_joined_at and 
        consultation.status == 'scheduled'):
        consultation.start_consultation()
        # Also start the appointment
        consultation.appointment.start_appointment()
    
    return jsonify({
        'success': True,
        'status': consultation.status,
        'room_id': consultation.room_id
    })

@bp.route('/consultation/<int:consultation_id>/end', methods=['POST'])
@login_required
def end_consultation(consultation_id):
    """End video consultation"""
    consultation = VideoConsultation.query.get_or_404(consultation_id)
    
    # Verify user can end this consultation
    if (current_user.role == 'patient' and consultation.patient_id != current_user.id and
        current_user.role == 'doctor' and consultation.doctor_id != current_user.id):
        return jsonify({'error': 'Unauthorized'}), 403
    
    # End the consultation
    consultation.end_consultation()
    
    # Complete the appointment if it's still in progress
    if consultation.appointment.status == 'in-progress':
        consultation.appointment.complete_appointment()
    
    return jsonify({
        'success': True,
        'status': consultation.status,
        'duration_minutes': consultation.duration_minutes
    })

@bp.route('/consultation/<int:appointment_id>/details')
@login_required
def consultation_details(appointment_id):
    """Get video consultation details for AJAX modal"""
    appointment = Appointment.query.get_or_404(appointment_id)
    consultation = appointment.video_consultation
    
    if not consultation:
        return jsonify({'error': 'No video consultation found'}), 404
    
    # Verify user can access this consultation
    if (current_user.role == 'patient' and appointment.patient_id != current_user.id and
        current_user.role == 'doctor' and appointment.doctor_id != current_user.id):
        return jsonify({'error': 'Unauthorized'}), 403
    
    details_html = f"""
    <div class="row">
        <div class="col-md-6">
            <h6 class="text-primary">Video Consultation Details</h6>
            <p><strong>Room ID:</strong> <code>{consultation.room_id}</code></p>
            <p><strong>Platform:</strong> {consultation.platform.title()}</p>
            <p><strong>Status:</strong> <span class="badge bg-{'success' if consultation.status == 'completed' else 'secondary'}">{consultation.status.title()}</span></p>
            {f'<p><strong>Duration:</strong> {consultation.duration_minutes} minutes</p>' if consultation.duration_minutes else ''}
            {f'<p><strong>Connection Quality:</strong> {consultation.connection_quality.title()}</p>' if consultation.connection_quality else ''}
        </div>
        <div class="col-md-6">
            <h6 class="text-primary">Session Information</h6>
            {f'<p><strong>Started:</strong> {consultation.actual_start_time.strftime("%B %d, %Y at %I:%M %p")}</p>' if consultation.actual_start_time else '<p><strong>Status:</strong> Not started</p>'}
            {f'<p><strong>Ended:</strong> {consultation.actual_end_time.strftime("%B %d, %Y at %I:%M %p")}</p>' if consultation.actual_end_time else ''}
            {f'<p><strong>Patient Joined:</strong> {consultation.patient_joined_at.strftime("%I:%M %p")}</p>' if consultation.patient_joined_at else '<p><strong>Patient:</strong> Not joined</p>'}
            {f'<p><strong>Doctor Joined:</strong> {consultation.doctor_joined_at.strftime("%I:%M %p")}</p>' if consultation.doctor_joined_at else '<p><strong>Doctor:</strong> Not joined</p>'}
            <p><strong>Recording:</strong> {'Enabled' if consultation.recording_enabled else 'Disabled'}</p>
        </div>
    </div>
    
    <div class="mt-3">
        <h6 class="text-primary">Actions</h6>
        <div class="d-flex gap-2">
            {f'<a href="/telemedicine/consultation/{appointment.id}" class="btn btn-primary btn-sm"><i class="fas fa-video"></i> Join Video Call</a>' if consultation.status in ['scheduled', 'active'] else ''}
            {f'<button class="btn btn-success btn-sm" onclick="copyRoomId()"><i class="fas fa-copy"></i> Copy Room ID</button>'}
        </div>
    </div>
    
    <script>
    function copyRoomId() {{
        navigator.clipboard.writeText('{consultation.room_id}').then(() => {{
            alert('Room ID copied to clipboard');
        }});
    }}
    </script>
    """
    
    return jsonify({'html': details_html})

@bp.route('/test-connection')
@login_required
def test_connection():
    """Test network connection for video consultations"""
    import time
    start_time = time.time()
    
    # Simple ping test (in real implementation, you'd do more comprehensive tests)
    try:
        # Simulate network test
        time.sleep(0.1)  # Simulate network delay
        latency = int((time.time() - start_time) * 1000)
        
        if latency < 100:
            status = 'Excellent'
        elif latency < 200:
            status = 'Good'
        elif latency < 500:
            status = 'Fair'
        else:
            status = 'Poor'
        
        return jsonify({
            'status': status,
            'latency': latency
        })
    
    except Exception as e:
        return jsonify({
            'status': 'Error',
            'latency': 0,
            'error': str(e)
        }), 500

@bp.route('/book-online-appointment', methods=['GET', 'POST'])
@login_required
def book_online_appointment():
    """Book a telemedicine appointment"""
    if request.method == 'POST':
        try:
            # Get form data
            doctor_id = request.form['doctor_id']
            appointment_date = datetime.strptime(request.form['date'], '%Y-%m-%d').date()
            appointment_time = datetime.strptime(request.form['time'], '%H:%M').time()
            reason = request.form.get('reason', '')
            
            # Create appointment
            appointment = Appointment(
                patient_id=current_user.id,
                doctor_id=doctor_id,
                date=appointment_date,
                time=appointment_time,
                reason=reason,
                appointment_type='telemedicine',  # Set as telemedicine
                status='scheduled'
            )
            
            db.session.add(appointment)
            db.session.flush()  # Get appointment ID
            
            # Create video consultation
            consultation = VideoConsultation(
                appointment_id=appointment.id,
                patient_id=current_user.id,
                doctor_id=doctor_id
            )
            
            db.session.add(consultation)
            db.session.commit()
            
            flash('Online appointment booked successfully! You will receive video call details closer to your appointment time.', 'success')
            return redirect(url_for('patient.dashboard'))
            
        except Exception as e:
            db.session.rollback()
            flash('Failed to book online appointment. Please try again.', 'error')
            return redirect(url_for('telemedicine.book_online_appointment'))
    
    # Get available doctors for online consultations
    from app.models.user import User
    doctors = User.query.filter_by(role='doctor', is_active=True).all()
    
    # Calculate date range for appointment booking
    from datetime import datetime, timedelta
    today = datetime.now()
    min_date = (today + timedelta(days=1)).strftime('%Y-%m-%d')  # Tomorrow
    max_date = (today + timedelta(days=30)).strftime('%Y-%m-%d')  # 30 days from now
    
    return render_template('telemedicine/book_online.html', 
                         doctors=doctors,
                         min_date=min_date,
                         max_date=max_date)

@bp.route('/my-consultations')
@login_required
def my_consultations():
    """View all video consultations for current user"""
    if current_user.role == 'patient':
        consultations = VideoConsultation.query.filter_by(
            patient_id=current_user.id
        ).order_by(VideoConsultation.created_at.desc()).all()
    elif current_user.role == 'doctor':
        consultations = VideoConsultation.query.filter_by(
            doctor_id=current_user.id
        ).order_by(VideoConsultation.created_at.desc()).all()
    else:
        flash('Access denied.', 'error')
        return redirect(url_for('main.index'))
    
    return render_template('telemedicine/consultations.html', consultations=consultations)

@bp.route('/api/doctor-slots/<int:doctor_id>')
@login_required
def get_doctor_slots_api(doctor_id):
    """API endpoint to get available time slots for a doctor"""
    selected_date = request.args.get('date')
    slots = get_doctor_available_slots(doctor_id, selected_date)
    
    return jsonify({'slots': slots})