# ./app/routes.py

from flask import Blueprint, jsonify, request
from app import db
from app.models import User, Inventory, Transaksi
from app.utils import token_required, create_token, calculate_monthly_sales
from sqlalchemy import extract
from datetime import datetime

# Create Blueprint
main = Blueprint('main', __name__)

# 1. Login endpoint
@main.route('/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(username=data.get('username')).first()
    
    if user and user.check_password(data.get('password')):
        token = create_token(user.id)
        return jsonify({'token': token}), 200
    return jsonify({'message': 'Invalid credentials'}), 401

# 2. Get low stock products
@main.route('/inventory/low-stock', methods=['GET'])
@token_required
def get_low_stock():
    low_stock_items = Inventory.query.filter(
        Inventory.stok_tersedia <= Inventory.stok_minimum
    ).all()
    
    return jsonify([{
        'sku': item.sku,
        'nama_item': item.nama_item,
        'stok_tersedia': item.stok_tersedia,
        'stok_minimum': item.stok_minimum
    } for item in low_stock_items]), 200

# 3. Get monthly sales
@main.route('/transactions/monthly-sales', methods=['GET'])
@token_required
def get_monthly_sales():
    year = request.args.get('year', datetime.now().year, type=int)
    month = request.args.get('month', datetime.now().month, type=int)
    
    total_sales = calculate_monthly_sales(year, month)
    return jsonify({
        'year': year,
        'month': month,
        'total_sales': total_sales
    }), 200

# 4. Transaction endpoints
@main.route('/transactions', methods=['POST', 'GET'])
@token_required
def handle_transactions():
    if request.method == 'GET':
        transactions = Transaksi.query.all()
        return jsonify([{
            'id_transaksi': t.id_transaksi,
            'sku': t.sku,
            'jumlah': t.jumlah,
            'amount': t.amount,
            'waktu_transaksi': t.waktu_transaksi
        } for t in transactions]), 200
    
    data = request.json
    try:
        with db.session.begin():
            # Create new transaction
            transaction = Transaksi(**data)
            db.session.add(transaction)
            
            # Update inventory
            inventory = Inventory.query.filter_by(
                sku=data['sku'], 
                batch_number=data['batch_number']
            ).with_for_update().first()
            
            if data['jenis_transaksi'] == 'pengurangan':
                if inventory.stok_tersedia < data['jumlah']:
                    raise ValueError('Insufficient stock')
                inventory.stok_tersedia -= data['jumlah']
            else:
                inventory.stok_tersedia += data['jumlah']
        
        return jsonify({'message': 'Transaction successful'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

# 5. Update inventory
@main.route('/inventory/<sku>', methods=['PUT'])
@token_required
def update_inventory(sku):
    data = request.json
    try:
        inventory = Inventory.query.filter_by(sku=sku).first()
        if not inventory:
            return jsonify({'message': 'Item not found'}), 404
        
        for key, value in data.items():
            setattr(inventory, key, value)
        
        db.session.commit()
        return jsonify({'message': 'Inventory updated successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400
    
# 6. Check database connection health
@main.route('/health')
def health_check():
    try:
        # Test database connection
        db.session.execute('SELECT 1')
        return jsonify({
            'status': 'healthy',
            'database': 'connected'
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'database': 'disconnected',
            'error': str(e)
        }), 500