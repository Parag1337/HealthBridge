from flask import Blueprint, request, render_template, redirect, url_for, flash, current_app
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models.user import User
from datetime import datetime
import os
from werkzeug.utils import secure_filename
import uuid
from app.utils.visitor_tracking import log_visitor_info, log_security_event

bp = Blueprint('auth', __name__, url_prefix='/auth')

def save_profile_photo(file):
    """Save uploaded profile photo and return filename"""
    if file and file.filename:
        # Check file extension
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
        filename = secure_filename(file.filename)
        if '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions:
            # Generate unique filename
            unique_filename = f"{uuid.uuid4()}_{filename}"
            
            # Create upload directory if it doesn't exist
            upload_dir = os.path.join(current_app.root_path, 'static', 'uploads', 'profiles')
            os.makedirs(upload_dir, exist_ok=True)
            
            # Save file
            file_path = os.path.join(upload_dir, unique_filename)
            file.save(file_path)
            
            return unique_filename
    return None

def allowed_file(filename):
    """Check if file extension is allowed for uploads"""
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_profile_photo(file):
    """Save uploaded profile photo and return filename"""
    if file and allowed_file(file.filename):
        # Generate unique filename
        filename = secure_filename(file.filename)
        name, ext = os.path.splitext(filename)
        unique_filename = f"{uuid.uuid4().hex}{ext}"
        
        # Create upload directory if it doesn't exist
        upload_dir = os.path.join(current_app.root_path, 'static', 'uploads', 'profiles')
        os.makedirs(upload_dir, exist_ok=True)
        
        # Save file
        file_path = os.path.join(upload_dir, unique_filename)
        file.save(file_path)
        
        return unique_filename
    return None

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        # Log visitor accessing registration page
        log_visitor_info("registration_page")
        return render_template('auth/register.html')
    
    # Handle POST request for registration
    user_type = request.form.get('user_type')
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    email = request.form.get('email')
    password = request.form.get('password')
    confirm_password = request.form.get('confirm_password')
    phone = request.form.get('phone')
    
    # Log registration attempt
    log_security_event("registration_attempt", {
        "email": email,
        "user_type": user_type,
        "name": f"{first_name} {last_name}" if first_name and last_name else None
    })
    
    # Validation
    if not all([user_type, first_name, last_name, email, password, confirm_password]):
        flash('All fields are required', 'error')
        log_security_event("registration_failed", {
            "reason": "missing_fields",
            "email": email,
            "user_type": user_type
        })
        return render_template('auth/register.html')
    
    if password != confirm_password:
        flash('Passwords do not match', 'error')
        log_security_event("registration_failed", {
            "reason": "password_mismatch",
            "email": email,
            "user_type": user_type
        })
        return render_template('auth/register.html')
    
    if len(password) < 6:
        flash('Password must be at least 6 characters long', 'error')
        log_security_event("registration_failed", {
            "reason": "weak_password",
            "email": email,
            "user_type": user_type
        })
        return render_template('auth/register.html')
    
    # Check if user already exists
    if User.query.filter_by(email=email).first():
        flash('Email already registered', 'error')
        log_security_event("registration_failed", {
            "reason": "email_exists",
            "email": email,
            "user_type": user_type
        })
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
        
        # Log successful registration
        log_security_event("registration_success", {
            "user_id": user.id,
            "email": email,
            "user_type": user_type,
            "name": f"{first_name} {last_name}"
        })
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('auth.login'))
    except Exception as e:
        db.session.rollback()
        
        # Log registration failure
        log_security_event("registration_failed", {
            "reason": "database_error",
            "email": email,
            "user_type": user_type,
            "error": str(e)
        })
        
        flash('Registration failed. Please try again.', 'error')
        return render_template('auth/register.html')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        # Log visitor accessing login page
        log_visitor_info("login_page")
        return render_template('auth/login.html')
    
    # Handle POST request for login
    email = request.form.get('email')
    password = request.form.get('password')
    user_type = request.form.get('user_type')
    remember_me = request.form.get('remember_me')
    
    # Log login attempt
    log_security_event("login_attempt", {
        "email": email,
        "user_type": user_type,
        "remember_me": bool(remember_me)
    })
    
    if not all([email, password, user_type]):
        flash('All fields are required', 'error')
        log_security_event("login_failed", {
            "reason": "missing_fields",
            "email": email,
            "user_type": user_type
        })
        return render_template('auth/login.html')
    
    # Find user by email and role
    user = User.query.filter_by(email=email, role=user_type).first()
    
    if user and user.check_password(password):
        login_user(user, remember=bool(remember_me))
        flash(f'Welcome back, {user.first_name}!', 'success')
        
        # Log successful login
        log_security_event("login_success", {
            "user_id": user.id,
            "email": email,
            "user_type": user_type,
            "user_name": f"{user.first_name} {user.last_name}"
        })
        
        # Redirect based on user type
        if user_type == 'patient':
            return redirect(url_for('patient.dashboard'))
        elif user_type == 'doctor':
            return redirect(url_for('doctor.home'))
        else:
            return redirect(url_for('main.index'))
    else:
        flash('Invalid email, password, or user type', 'error')
        log_security_event("login_failed", {
            "reason": "invalid_credentials",
            "email": email,
            "user_type": user_type,
            "user_exists": user is not None
        })
        return render_template('auth/login.html')

@bp.route('/logout')
@login_required
def logout():
    # Log logout event
    log_security_event("logout", {
        "user_id": current_user.id,
        "user_type": current_user.role,
        "user_name": f"{current_user.first_name} {current_user.last_name}"
    })
    
    logout_user()
    flash('You have been logged out', 'info')
    return redirect(url_for('main.index'))

@bp.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if request.method == 'GET':
        return render_template('auth/edit_profile.html', user=current_user)
    
    # Handle POST request for profile update
    try:
        # Update basic info
        current_user.first_name = request.form.get('first_name')
        current_user.last_name = request.form.get('last_name')
        current_user.email = request.form.get('email')
        current_user.phone = request.form.get('phone')
        
        # Update role-specific fields
        if current_user.role == 'patient':
            if request.form.get('date_of_birth'):
                current_user.date_of_birth = datetime.strptime(request.form.get('date_of_birth'), '%Y-%m-%d').date()
            current_user.gender = request.form.get('gender')
            current_user.address = request.form.get('address')
            current_user.emergency_contact = request.form.get('emergency_contact')
            current_user.blood_type = request.form.get('blood_type')
            current_user.allergies = request.form.get('allergies')
            
        elif current_user.role == 'doctor':
            # Handle profile photo upload
            profile_photo = request.files.get('profile_photo')
            if profile_photo and profile_photo.filename:
                new_filename = save_profile_photo(profile_photo)
                if new_filename:
                    # Delete old photo if exists
                    if current_user.profile_photo:
                        old_path = os.path.join(current_app.root_path, 'static', 'uploads', 'profiles', current_user.profile_photo)
                        if os.path.exists(old_path):
                            os.remove(old_path)
                    current_user.profile_photo = new_filename
                else:
                    flash('Invalid file format. Please upload JPG, PNG, or GIF files only.', 'error')
                    return render_template('auth/edit_profile.html', user=current_user)
            
            # Update doctor fields
            current_user.specialization = request.form.get('specialization')
            current_user.license_number = request.form.get('license_number')
            current_user.qualification = request.form.get('qualification')
            if request.form.get('experience'):
                current_user.experience = int(request.form.get('experience'))
            if request.form.get('consultation_fee'):
                current_user.consultation_fee = float(request.form.get('consultation_fee'))
            current_user.about = request.form.get('about')
            current_user.address = request.form.get('address')
        
        # Handle password change if provided
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        if new_password:
            if new_password != confirm_password:
                flash('New passwords do not match', 'error')
                return render_template('auth/edit_profile.html', user=current_user)
            
            if len(new_password) < 6:
                flash('Password must be at least 6 characters long', 'error')
                return render_template('auth/edit_profile.html', user=current_user)
            
            current_user.set_password(new_password)
        
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        
        # Redirect based on user type
        if current_user.role == 'doctor':
            return redirect(url_for('doctor.home'))
        else:
            return redirect(url_for('patient.dashboard'))
            
    except Exception as e:
        db.session.rollback()
        flash('Failed to update profile. Please try again.', 'error')
        return render_template('auth/edit_profile.html', user=current_user)