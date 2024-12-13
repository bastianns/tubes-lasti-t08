# routes.py
from flask import Blueprint, jsonify, request
from models import User, Inventory, Transaksi
from app import db
from utils import token_required, create_token, calculate_monthly_sales
from state import blacklisted_tokens
from sqlalchemy import extract, text
from datetime import datetime
import logging

# Configure logger
logger = logging.getLogger(__name__)

# Create Blueprint
main = Blueprint('main', __name__)

# 1. Login endpoint
@main.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    # Detailed logging
    logger.info(f"Login attempt - Username: {username}")
    
    # Find the user
    user = User.query.filter_by(username=username).first()
    
    if not user:
        logger.warning(f"User not found: {username}")
        return jsonify({'message': 'Invalid credentials', 'debug': 'User not found'}), 401
    
    # Debug: print the stored password hash
    logger.info(f"Stored password hash: {user.password_hash}")
    
    # Check password
    password_check = user.check_password(password)
    logger.info(f"Password check result: {password_check}")
    
    if password_check:
        token = create_token(user.id)
        return jsonify({'token': token}), 200
    
    return jsonify({'message': 'Invalid credentials', 'debug': 'Password check failed'}), 401

# 2. Logout endpoint
@main.route('/logout', methods=['POST'])
@token_required
def logout():
    token = request.headers.get('Authorization').split()[1]
    blacklisted_tokens.add(token)
    return jsonify({'message': 'Successfully logged out'}), 200

# 3. Get stock levels
@main.route('/inventory', methods=['GET'])
@token_required
def get_inventory():
    # Get optional query parameters for filtering
    category = request.args.get('category')
    search = request.args.get('search')
    
    query = Inventory.query
    
    # Apply filters if provided
    if category:
        query = query.filter(Inventory.kategori == category)
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            db.or_(
                Inventory.nama_item.ilike(search_term),
                Inventory.sku.ilike(search_term)
            )
        )
    
    inventory_items = query.all()
    
    return jsonify([{
        'sku': item.sku,
        'batch_number': item.batch_number,
        'nama_item': item.nama_item,
        'kategori': item.kategori,
        'stok_tersedia': item.stok_tersedia,
        'stok_minimum': item.stok_minimum,
        'harga': item.harga,
        'waktu_pembaruan': item.waktu_pembaruan.isoformat() if item.waktu_pembaruan else None
    } for item in inventory_items]), 200

# 4. Get low stock products
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

# 6. Transaction endpoints
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
    
# 7. Get monthly sales
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
    
# 8. Check database connection health
@main.route('/health')
def health_check():
    try:
        # Test database connection
        db.session.execute(text('SELECT 1'))
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

@main.route('/debug/users', methods=['GET'])
def debug_users():
    users = User.query.all()
    user_list = [{'id': u.id, 'username': u.username, 'password_hash': u.password_hash} for u in users]
    return jsonify(user_list), 200