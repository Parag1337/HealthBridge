from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

# Initialize the database
db = SQLAlchemy()

def init_db(app: Flask):
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'mysql://username:password@localhost/db_name')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)