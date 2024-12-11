import os

# Konfigurasi Flask
SQLALCHEMY_DATABASE_URI = 'postgresql://apotek_user:password@localhost/apotek_db'
SQLALCHEMY_TRACK_MODIFICATIONS = False
SECRET_KEY = os.getenv('SECRET_KEY', 'mysecretkey')  # Untuk keamanan (JWT atau CSRF)
