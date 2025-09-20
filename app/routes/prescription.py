from flask import Blueprint, request, jsonify
from app.models.prescription import Prescription
from app.utils.database import db

prescription_bp = Blueprint('prescription', __name__)

@prescription_bp.route('/prescriptions', methods=['POST'])
def create_prescription():
    data = request.get_json()
    new_prescription = Prescription(
        patient_id=data['patient_id'],
        doctor_id=data['doctor_id'],
        medication=data['medication'],
        dosage=data['dosage'],
        instructions=data['instructions']
    )
    db.session.add(new_prescription)
    db.session.commit()
    return jsonify({'message': 'Prescription created successfully!'}), 201

@prescription_bp.route('/prescriptions/<int:patient_id>', methods=['GET'])
def get_prescriptions(patient_id):
    prescriptions = Prescription.query.filter_by(patient_id=patient_id).all()
    return jsonify([prescription.to_dict() for prescription in prescriptions]), 200

def register_routes(app):
    app.register_blueprint(prescription_bp)