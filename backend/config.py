# backend/config.py
import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

def get_database_url():
    """Determine the correct database URL based on environment"""
    is_docker = os.environ.get('DOCKER_ENV', '').lower() == 'true'
    
    db_user = os.getenv('DB_USER', 'apotek_user')
    db_pass = os.getenv('DB_PASSWORD', 'password')
    db_name = os.getenv('DB_NAME', 'apotek_db')
    db_port = os.getenv('DB_PORT', '5432')
    
    db_host = 'postgres' if is_docker else 'localhost'
    
    return f'postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}'

class Config:
    SQLALCHEMY_DATABASE_URI = get_database_url()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    SQLALCHEMY_ENGINE_OPTIONS = {
        "connect_args": {
            "options": "-c search_path=public"
        }
    }

    SECRET_KEY = os.getenv('SECRET_KEY', 'your-dev-secret-key-change-in-production')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'your-jwt-secret-key-change-in-production')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)