from flask import Blueprint, render_template

bp = Blueprint('main', __name__)

@bp.route('/')
@bp.route('/index')
def index():
    """Homepage route"""
    return render_template('index.html')

@bp.route('/about')
def about():
    """About page route"""
    return render_template('about.html')