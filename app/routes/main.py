from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user

bp = Blueprint('main', __name__)

@bp.route('/')
@bp.route('/index')
def index():
    """Homepage route - redirects logged-in users to their dashboard"""
    if current_user.is_authenticated:
        if current_user.role == 'patient':
            return redirect(url_for('patient.dashboard'))
        elif current_user.role == 'doctor':
            return redirect(url_for('doctor.dashboard'))
        elif current_user.role == 'admin':
            return redirect(url_for('admin.dashboard'))
    
    return render_template('index.html')

@bp.route('/about')
def about():
    """About page route"""
    return render_template('about.html')