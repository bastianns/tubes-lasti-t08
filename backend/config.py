# config.py
from os import environ

class Config:
    # PostgreSQL Database Configuration
    SQLALCHEMY_DATABASE_URI = environ.get('DATABASE_URL', 
        'postgresql://apotek_user:password@localhost/apotek_db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = environ.get('SECRET_KEY', 'your_secret_key')