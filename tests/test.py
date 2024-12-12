# ./tests/test.py

import unittest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, app, db
from app.models import User, Inventory, Transaksi

class ApotekTestCase(unittest.TestCase):
    def setUp(self):
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
            db.session.commit()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def login(self):
        return self.client.post('/login', json={
            'username': 'test_user',
            'password': 'test123'
        })

    def test_login(self):
        response = self.login()
        self.assertEqual(response.status_code, 200)
        self.assertIn('token', response.json)

    def test_low_stock(self):
        # First login to get token
        login_response = self.login()
        token = login_response.json['token']

        # Test low stock endpoint
        response = self.client.get('/inventory/low-stock', 
            headers={'Authorization': f'Bearer {token}'})
        self.assertEqual(response.status_code, 200)

    def test_monthly_sales(self):
        # Add test logic for monthly sales
        pass

    def test_inventory_update(self):
        # Add test logic for inventory updates
        pass

if __name__ == '__main__':
    unittest.main()