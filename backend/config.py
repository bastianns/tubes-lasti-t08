# config.py
import os
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    # Database Configuration
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Database connection settings
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 5,
        'max_overflow': 10,
        'pool_timeout': 30,
        'pool_recycle': 1800,  # Recycle connections after 30 minutes
    }
    
    # App Configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key-please-change')
    
    # JWT Configuration
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-key-please-change')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    
    # Flask Environment
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')