from flask import Blueprint, request, jsonify
from app.models.appointment import Appointment
from app.utils.database import db

appointment_bp = Blueprint('appointment', __name__)

@appointment_bp.route('/appointments', methods=['POST'])
def book_appointment():
    data = request.get_json()
    new_appointment = Appointment(
        date=data['date'],
        time=data['time'],
        patient_id=data['patient_id'],
        doctor_id=data['doctor_id']
    )
    db.session.add(new_appointment)
    db.session.commit()
    return jsonify({'message': 'Appointment booked successfully!'}), 201

@appointment_bp.route('/appointments/<int:appointment_id>', methods=['GET'])
def view_appointment(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)
    return jsonify({
        'id': appointment.id,
        'date': appointment.date,
        'time': appointment.time,
        'patient_id': appointment.patient_id,
        'doctor_id': appointment.doctor_id
    }), 200

@appointment_bp.route('/appointments', methods=['GET'])
def list_appointments():
    appointments = Appointment.query.all()
    return jsonify([{
        'id': appointment.id,
        'date': appointment.date,
        'time': appointment.time,
        'patient_id': appointment.patient_id,
        'doctor_id': appointment.doctor_id
    } for appointment in appointments]), 200