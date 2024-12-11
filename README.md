# Panduan Penggunaan

## Deskripsi Proyek
Proyek ini merupakan sebuah aplikasi Python yang membutuhkan serangkaian testing untuk memastikan fungsionalitasnya berjalan dengan baik. Terdapat beberapa file yang memiliki peran penting dalam proses testing aplikasi ini.

## Struktur File
Berikut adalah struktur file yang ada dalam proyek ini:

| Nama File | Jenis | Deskripsi |
| --- | --- | --- |
| `.pytest_cache` | Direktori | Direktori cache untuk pytest, digunakan untuk mempercepat eksekusi test. |
| `_pycache_` | Direktori | Direktori cache untuk Python, digunakan untuk mempercepat proses import modul. |
| `lasti` | Direktori | Direktori utama untuk kode sumber aplikasi. |
| `.env` | File ENV | File konfigurasi lingkungan, berisi variabel-variabel lingkungan yang dibutuhkan aplikasi. |
| `.gitignore` | File Git | File yang mendefinisikan file/direktori yang akan diabaikan oleh Git. |
| `apotek_db_backup` | File Teks SQL | File backup database PostgreSQL untuk aplikasi apotek. |
| `app.py` | File Kode Python | File utama aplikasi Flask. |
| `config.py` | File Kode Python | File konfigurasi aplikasi. |
| `db_connection_test.py` | File Kode Python | Skrip untuk menguji koneksi database. |
| `docker-compose.yml` | File YAML | Konfigurasi Docker Compose untuk menjalankan aplikasi. |
| `models.py` | File Kode Python | File yang mendefinisikan model-model database. |
| `requirements.txt` | File Teks | Daftar dependensi Python yang dibutuhkan aplikasi. |
| `test_app.py` | File Kode Python | Skrip untuk menjalankan test unit aplikasi. |

## Cara Menjalankan Testing
Untuk menjalankan test unit pada aplikasi, ikuti langkah-langkah berikut:

1. Pastikan Anda telah menginstal `pytest` dengan menjalankan perintah `pip install pytest`.
2. Periksa koneksi database dengan menjalankan skrip `db_connection_test.py`.
3. Jalankan semua test dengan menjalankan perintah `pytest test_app.py`.
4. Untuk menjalankan test spesifik, gunakan perintah `pytest test_app.py::nama_fungsi_test`.

## Kegunaan File-file
- `.pytest_cache` dan `_pycache_`: Direktori cache yang digunakan untuk mempercepat eksekusi test dan proses import modul.
- `.env`: File konfigurasi lingkungan yang menyimpan variabel-variabel lingkungan yang dibutuhkan aplikasi, seperti koneksi database.
- `.gitignore`: File yang mendefinisikan file/direktori yang akan diabaikan oleh Git, seperti file cache dan konfigurasi lingkungan.
- `apotek_db_backup`: File backup database PostgreSQL untuk aplikasi apotek.
- `app.py`: File utama aplikasi Flask yang berisi rute-rute dan logika bisnis aplikasi.
- `config.py`: File konfigurasi aplikasi, seperti koneksi database dan kunci rahasia.
- `db_connection_test.py`: Skrip untuk menguji koneksi database sebelum menjalankan test unit.
- `docker-compose.yml`: Konfigurasi Docker Compose untuk menjalankan aplikasi.
- `models.py`: File yang mendefinisikan model-model database yang digunakan oleh aplikasi.
- `requirements.txt`: Daftar dependensi Python yang dibutuhkan aplikasi.
- `test_app.py`: Skrip untuk menjalankan test unit aplikasi.

Jika Anda memiliki pertanyaan atau membutuhkan bantuan lebih lanjut, jangan ragu untuk menghubungi saya.