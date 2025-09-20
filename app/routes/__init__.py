from flask import Blueprint

# Initialize the routes blueprint
routes_bp = Blueprint('routes', __name__)

# Import routes to register them with the blueprint
from . import main, auth
# Temporarily disabled until we fix other route modules:
# from . import patient, doctor, appointment, prescription, admin

# Register the blueprint with the main application in app/__init__.py