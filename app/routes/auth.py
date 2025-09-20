from flask import Blueprint, request, render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models.user import User
from datetime import datetime

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('auth/register.html')
    
    # Handle POST request for registration
    user_type = request.form.get('user_type')
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    email = request.form.get('email')
    password = request.form.get('password')
    confirm_password = request.form.get('confirm_password')
    phone = request.form.get('phone')
    
    # Validation
    if not all([user_type, first_name, last_name, email, password, confirm_password]):
        flash('All fields are required', 'error')
        return render_template('auth/register.html')
    
    if password != confirm_password:
        flash('Passwords do not match', 'error')
        return render_template('auth/register.html')
    
    if len(password) < 6:
        flash('Password must be at least 6 characters long', 'error')
        return render_template('auth/register.html')
    
    # Check if user already exists
    if User.query.filter_by(email=email).first():
        flash('Email already registered', 'error')
        return render_template('auth/register.html')
    
    # Create new user
    user = User(
        email=email,
        first_name=first_name,
        last_name=last_name,
        phone=phone,
        role=user_type
    )
    user.set_password(password)
    
    # Add additional fields based on user type
    if user_type == 'patient':
        user.date_of_birth = datetime.strptime(request.form.get('date_of_birth'), '%Y-%m-%d').date() if request.form.get('date_of_birth') else None
        user.gender = request.form.get('gender')
        user.address = request.form.get('address')
    elif user_type == 'doctor':
        user.specialization = request.form.get('specialization')
        user.license_number = request.form.get('license_number')
        user.qualification = request.form.get('qualification')
        user.experience = int(request.form.get('experience', 0))
    
    try:
        db.session.add(user)
        db.session.commit()
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('auth.login'))
    except Exception as e:
        db.session.rollback()
        flash('Registration failed. Please try again.', 'error')
        return render_template('auth/register.html')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('auth/login.html')
    
    # Handle POST request for login
    email = request.form.get('email')
    password = request.form.get('password')
    user_type = request.form.get('user_type')
    remember_me = request.form.get('remember_me')
    
    if not all([email, password, user_type]):
        flash('All fields are required', 'error')
        return render_template('auth/login.html')
    
    # Find user by email and role
    user = User.query.filter_by(email=email, role=user_type).first()
    
    if user and user.check_password(password):
        login_user(user, remember=bool(remember_me))
        flash(f'Welcome back, {user.first_name}!', 'success')
        
        # Redirect based on user type
        if user_type == 'patient':
            return redirect(url_for('patient.dashboard'))
        elif user_type == 'doctor':
            return redirect(url_for('doctor.dashboard'))
        else:
            return redirect(url_for('main.index'))
    else:
        flash('Invalid email, password, or user type', 'error')
        return render_template('auth/login.html')

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out', 'info')
    return redirect(url_for('main.index'))