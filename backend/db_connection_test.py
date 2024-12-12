from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
import os

def test_database_connection(database_url):
    try:
        engine = create_engine(database_url)
        with engine.connect() as connection:
            print("Koneksi database berhasil!")
            return True
    except OperationalError as e:
        print(f"Koneksi database gagal: {e}")
        return False

# Gunakan environment variable atau default URL
database_url = os.getenv('DATABASE_URL', 'postgresql://apotek_user:password@localhost/apotek_db')
test_database_connection(database_url)

# Jalankan script ini secara manual
if __name__ == '__main__':
    test_database_connection(database_url)