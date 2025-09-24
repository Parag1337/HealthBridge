from flask import Blueprint
from .chatbot import chatbot_bp

# Initialize the routes blueprint
routes_bp = Blueprint('routes', __name__)

# Import routes to register them with the blueprint
from . import main, auth, patient, doctor, telemedicine
# from . import admin  # Admin routes not yet integrated

# Register the blueprint with the main application in app/__init__.py
