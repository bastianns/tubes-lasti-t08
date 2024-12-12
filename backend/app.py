from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from models import db, Inventory, Transaksi
import os

# Inisialisasi Aplikasi Flask
app = Flask(__name__)

# Konfigurasi PostgreSQL
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
    'DATABASE_URL', 
    'postgresql://apotek_user:password@localhost/apotek_db'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Aktifkan CORS
CORS(app)

# Inisialisasi Database
db.init_app(app)

# Endpoint untuk mendapatkan semua inventory
@app.route('/inventory', methods=['GET'])
def get_inventory():
    try:
        inventory_list = Inventory.query.all()
        return jsonify([{
            'sku': item.sku,
            'batch_number': item.batch_number,
            'nama_item': item.nama_item,
            'kategori': item.kategori,
            'stok_tersedia': item.stok_tersedia,
            'stok_minimum': item.stok_minimum
        } for item in inventory_list]), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Gagal mengambil data inventory', 'details': str(e)}), 500

# Endpoint untuk memperbarui stok inventory
@app.route('/transaksi', methods=['POST'])
def update_stok():
    try:
        data = request.json
        
        #Gunakan session untuk transaksi database
        with db.session.begin():
            inventory = Inventory.query.filter_by(
                sku=data['sku'], 
                batch_number=data['batch_number']
            ).with_for_update().first()
            
            if not inventory:
                return jsonify({'error': 'Item tidak ditemukan'}), 404
            
            # Buat transaksi baru
            transaksi = Transaksi(
                sku=data['sku'],
                batch_number=data['batch_number'],
                jenis_transaksi=data['jenis_transaksi'],
                jumlah=data['jumlah'],
                amount=data['amount']
            )
            
            # Update stok inventory
            if data['jenis_transaksi'] == 'penambahan':
                inventory.stok_tersedia += data['jumlah']
            elif data['jenis_transaksi'] == 'pengurangan':
                if inventory.stok_tersedia < data['jumlah']:
                    return jsonify({'error': 'Stok tidak mencukupi'}), 400
                inventory.stok_tersedia -= data['jumlah']
            else:
                return jsonify({'error': 'Jenis transaksi tidak valid'}), 400
            
            db.session.add(transaksi)
        
        return jsonify({
            'message': 'Stok berhasil diperbarui',
            'stok_baru': inventory.stok_tersedia
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Gagal memperbarui stok', 'details': str(e)}), 500

# Endpoint untuk menambahkan item baru
@app.route('/inventory', methods=['POST'])
def add_inventory():
    try:
        data = request.json
        with db.session.begin():
            inventory = Inventory(
                sku=data['sku'],
                batch_number=data['batch_number'],
                nama_item=data['nama_item'],
                kategori=data['kategori'],
                stok_tersedia=data.get('stok_tersedia', 0),
                stok_minimum=data.get('stok_minimum', 10)
            )
            db.session.add(inventory)
        
        return jsonify({
            'message': 'Item berhasil ditambahkan', 
            'sku': inventory.sku, 
            'batch_number': inventory.batch_number
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Gagal menambahkan item', 'details': str(e)}), 500

# Inisialisasi database (jalankan saat pertama kali)
with app.app_context():
    db.create_all()

# Jalankan Aplikasi
if __name__ == '__main__':
    app.run(debug=True)