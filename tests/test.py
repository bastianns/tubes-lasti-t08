# ./tests/test.py

import unittest
import json
import sys
import os

from datetime import datetime, timezone
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from sqlalchemy import text
from app.models import User, Inventory, Transaksi

class ApotekTestCase(unittest.TestCase):
    def setUp(self):
        """Set up test environment before each test"""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://apotek_user:password@localhost:5432/apotek_test_db'
        self.client = self.app.test_client()
        
        with self.app.app_context():
            db.create_all()
            
            # Add test user
            user = User(username='test_user')
            user.set_password('test123')
            db.session.add(user)
            
            # Add test inventory items
            inventory_items = [
                Inventory(
                    sku='TEST001',
                    batch_number='B001',
                    nama_item='Test Medicine',
                    kategori='Test Category',
                    stok_tersedia=50,
                    stok_minimum=10,
                    harga=10000
                ),
                Inventory(
                    sku='TEST002',
                    batch_number='B001',
                    nama_item='Low Stock Item',
                    kategori='Test Category',
                    stok_tersedia=5,
                    stok_minimum=10,
                    harga=15000
                )
            ]
            for item in inventory_items:
                db.session.add(item)
            
            db.session.commit()

    def tearDown(self):
        """Clean up after each test"""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def get_auth_token(self):
        """Helper method to get authentication token"""
        response = self.client.post('/login', json={
            'username': 'test_user',
            'password': 'test123'
        })
        return response.json['token']

    def test_health_check(self):
        """Test database health check endpoint"""
        response = self.client.get('/health')
        print(f"Health check response: {response.data.decode()}")  # Debug print
        
        with self.app.app_context():
            try:
                # Test database connection explicitly
                db.session.execute(text('SELECT 1'))
                db.session.commit()
                print("Database connection test successful")
            except Exception as e:
                print(f"Database connection test failed: {str(e)}")
                
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['status'], 'healthy')
        self.assertEqual(response.json['database'], 'connected')

    def test_login(self):
        """Test login functionality"""
        # Test successful login
        response = self.client.post('/login', json={
            'username': 'test_user',
            'password': 'test123'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('token', response.json)

        # Test failed login
        response = self.client.post('/login', json={
            'username': 'test_user',
            'password': 'wrong_password'
        })
        self.assertEqual(response.status_code, 401)

    def test_logout(self):
        """Test logout functionality"""
        # First login to get a token
        response = self.client.post('/login', json={
            'username': 'test_user',
            'password': 'test123'
        })
        token = response.json['token']
        
        # Test logout
        response = self.client.post('/logout', 
            headers={'Authorization': f'Bearer {token}'})
        self.assertEqual(response.status_code, 200)
        
        # Try to use the token after logout
        response = self.client.get('/inventory',
            headers={'Authorization': f'Bearer {token}'})
        self.assertEqual(response.status_code, 401)

    def test_get_inventory(self):
        """Test getting all inventory items"""
        token = self.get_auth_token()
        
        # Test getting all items
        response = self.client.get('/inventory',
            headers={'Authorization': f'Bearer {token}'})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(isinstance(response.json, list))
        self.assertEqual(len(response.json), 2)  # We added 2 items in setUp
        
        # Test category filter
        response = self.client.get('/inventory?category=Test Category',
            headers={'Authorization': f'Bearer {token}'})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(all(item['kategori'] == 'Test Category' 
                        for item in response.json))
        
        # Test search filter
        response = self.client.get('/inventory?search=Low',
            headers={'Authorization': f'Bearer {token}'})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(any(item['nama_item'] == 'Low Stock Item' 
                        for item in response.json))

    def test_low_stock(self):
        """Test low stock inventory endpoint"""
        token = self.get_auth_token()
        
        response = self.client.get('/inventory/low-stock', 
            headers={'Authorization': f'Bearer {token}'})
        
        self.assertEqual(response.status_code, 200)
        data = response.json
        self.assertTrue(isinstance(data, list))
        self.assertTrue(any(item['sku'] == 'TEST002' for item in data))
        
        # Verify low stock item is included
        low_stock_item = next(item for item in data if item['sku'] == 'TEST002')
        self.assertTrue(low_stock_item['stok_tersedia'] <= low_stock_item['stok_minimum'])

    def test_update_inventory(self):
        """Test inventory update endpoint"""
        token = self.get_auth_token()
        
        update_data = {
            'stok_tersedia': 60,
            'harga': 12000
        }
        
        response = self.client.put('/inventory/TEST001',
            headers={'Authorization': f'Bearer {token}'},
            json=update_data
        )
        self.assertEqual(response.status_code, 200)
        
        # Verify the update
        with self.app.app_context():
            updated_item = Inventory.query.filter_by(sku='TEST001').first()
            self.assertEqual(updated_item.stok_tersedia, 60)
            self.assertEqual(updated_item.harga, 12000)

    def test_transactions(self):
        """Test transaction endpoints"""
        token = self.get_auth_token()
        
        # Test creating a new transaction
        transaction_data = {
            'sku': 'TEST001',
            'batch_number': 'B001',
            'jenis_transaksi': 'pengurangan',
            'jumlah': 5,
            'amount': 50000
        }
        
        response = self.client.post('/transactions',
            headers={'Authorization': f'Bearer {token}'},
            json=transaction_data
        )
        self.assertEqual(response.status_code, 201)
        
        # Test getting all transactions
        response = self.client.get('/transactions',
            headers={'Authorization': f'Bearer {token}'})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(isinstance(response.json, list))
        self.assertEqual(len(response.json), 1)

    def test_monthly_sales(self):
        """Test monthly sales calculation endpoint"""
        token = self.get_auth_token()
        
        # Add some test transactions
        with self.app.app_context():
            transaction = Transaksi(
                sku='TEST001',
                batch_number='B001',
                jenis_transaksi='pengurangan',
                jumlah=5,
                amount=50000,
                waktu_transaksi=datetime.now(timezone.utc)
            )
            db.session.add(transaction)
            db.session.commit()

        # Test getting monthly sales
        current_year = datetime.now(timezone.utc).year
        current_month = datetime.now(timezone.utc).month
        
        response = self.client.get(
            f'/transactions/monthly-sales?year={current_year}&month={current_month}',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['total_sales'], 50000)

if __name__ == '__main__':
    unittest.main()