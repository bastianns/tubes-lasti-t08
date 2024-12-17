# ./app/__init__.py

from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from config import Config

# Initialize extensions
db = SQLAlchemy()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    CORS(app)
    db.init_app(app)

    with app.app_context():
        # Import routes after db initialization
        from app.routes import main as main_blueprint
        app.register_blueprint(main_blueprint)
        
        # Create tables
        db.create_all()

    return app