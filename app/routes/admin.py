from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models.user import User
from app import db

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin/dashboard')
def dashboard():
    return render_template('admin/dashboard.html')

@admin_bp.route('/admin/users')
def manage_users():
    users = User.query.all()
    return render_template('admin/users.html', users=users)

@admin_bp.route('/admin/doctors')
def manage_doctors():
    doctors = User.query.filter_by(role='doctor').all()
    return render_template('admin/doctors.html', doctors=doctors)

@admin_bp.route('/admin/add_user', methods=['POST'])
def add_user():
    username = request.form.get('username')
    password = request.form.get('password')
    role = request.form.get('role')
    
    new_user = User(username=username, password=password, role=role)
    db.session.add(new_user)
    db.session.commit()
    
    flash('User added successfully!', 'success')
    return redirect(url_for('admin.manage_users'))

@admin_bp.route('/admin/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    user = User.query.get(user_id)
    if user:
        db.session.delete(user)
        db.session.commit()
        flash('User deleted successfully!', 'success')
    else:
        flash('User not found!', 'danger')
    return redirect(url_for('admin.manage_users'))

@admin_bp.route('/admin/add_doctor', methods=['POST'])
def add_doctor():
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    email = request.form.get('email')
    password = request.form.get('password')
    specialization = request.form.get('specialization')
    
    new_doctor = User(
        first_name=first_name,
        last_name=last_name,
        email=email,
        role='doctor',
        specialization=specialization
    )
    new_doctor.set_password(password)
    db.session.add(new_doctor)
    db.session.commit()
    
    flash('Doctor added successfully!', 'success')
    return redirect(url_for('admin.manage_doctors'))

@admin_bp.route('/admin/delete_doctor/<int:doctor_id>', methods=['POST'])
def delete_doctor(doctor_id):
    doctor = User.query.filter_by(id=doctor_id, role='doctor').first()
    if doctor:
        db.session.delete(doctor)
        db.session.commit()
        flash('Doctor deleted successfully!', 'success')
    else:
        flash('Doctor not found!', 'danger')
    return redirect(url_for('admin.manage_doctors'))