# backend/__init__.py

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from config import Config

# Initialize SQLAlchemy outside of create_app to avoid circular imports
db = SQLAlchemy()

def create_app(config_class=Config):
    """
    Application factory function that creates and configures the Flask app.
    This pattern allows for better testing and multiple instances of your app.
    """
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions with app
    db.init_app(app)
    CORS(app)
    
    # Register blueprints
    from .routes import main as main_blueprint
    app.register_blueprint(main_blueprint)
    
    # Create database tables if they don't exist
    with app.app_context():
        db.create_all()
    
    return app