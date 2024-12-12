# app.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from config import Config
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize extensions
db = SQLAlchemy()

def create_app(config_class=Config):
    """
    Application factory function that creates and configures the Flask app.
    Includes proper error handling and database initialization.
    """
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions
    db.init_app(app)
    CORS(app)
    
    # Import and register blueprints
    from routes import main as main_blueprint
    app.register_blueprint(main_blueprint)
    
    # Create database tables within application context
    with app.app_context():
        try:
            db.create_all()
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Error creating database tables: {str(e)}")
    
    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return {
            'error': 'Not found',
            'message': 'The requested URL was not found on the server.'
        }, 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()  # Roll back db session in case of error
        return {
            'error': 'Internal server error',
            'message': str(error)
        }, 500

    return app

# Create the application instance
app = create_app()

if __name__ == '__main__':
    app.run()