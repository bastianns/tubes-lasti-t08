# ./config.py

import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Database Configuration
    SQLALCHEMY_DATABASE_URI = 'postgresql://apotek_user:password@postgres:5432/apotek_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # App Configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-dev-secret-key-change-in-production')
    
    # JWT Configuration for Login
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'your-jwt-secret-key-change-in-production')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)