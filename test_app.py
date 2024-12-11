import pytest
from app import app, db
from models import Inventory, Transaksi
import json
import os

@pytest.fixture
def client():
    # Gunakan database utama, tapi dalam mode testing
    app.config['TESTING'] = True
    
    # Optional: Tambahkan prefix atau skema khusus untuk testing
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
        'DATABASE_URL', 
        'postgresql://apotek_user:password@localhost/apotek_db'
    )
    
    with app.test_client() as client:
        with app.app_context():
            # Pastikan Anda tidak secara tidak sengaja menghapus semua data
            yield client

def test_add_inventory(client):
    # Test menambahkan item baru ke inventory
    inventory_data = {
        'sku': 'TEST001',
        'batch_number': 'BATCH001',
        'nama_item': 'Test Item',
        'kategori': 'Test Kategori',
        'stok_tersedia': 100,
        'stok_minimum': 10
    }
    
    response = client.post('/inventory', 
                           data=json.dumps(inventory_data),
                           content_type='application/json')
    
    # Verifikasi respon
    assert response.status_code == 201
    assert response.json['message'] == 'Item berhasil ditambahkan'

def test_update_stok_penambahan(client):
    # Persiapan: Tambah item terlebih dahulu (jika belum ada)
    with app.app_context():
        # Cek apakah item sudah ada
        existing_item = Inventory.query.filter_by(
            sku='TEST002', 
            batch_number='BATCH002'
        ).first()
        
        if not existing_item:
            inventory = Inventory(
                sku='TEST002', 
                batch_number='BATCH002', 
                nama_item='Test Item 2', 
                kategori='Test', 
                stok_tersedia=50, 
                stok_minimum=10
            )
            db.session.add(inventory)
            db.session.commit()
    
    # Test penambahan stok
    transaksi_data = {
        'sku': 'TEST002',
        'batch_number': 'BATCH002',
        'jenis_transaksi': 'penambahan',
        'jumlah': 20,
        'amount': 200000
    }
    
    response = client.post('/transaksi', 
                           data=json.dumps(transaksi_data),
                           content_type='application/json')
    
    # Verifikasi respon
    assert response.status_code == 200
    
    # Optional: Verifikasi stok terupdate di database
    with app.app_context():
        updated_item = Inventory.query.filter_by(
            sku='TEST002', 
            batch_number='BATCH002'
        ).first()
        assert updated_item is not None

def test_get_inventory(client):
    response = client.get('/inventory')
    
    # Verifikasi respon
    assert response.status_code == 200
    assert isinstance(response.json, list)