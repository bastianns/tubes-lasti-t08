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
    total_stock = db.session.query(
        Inventory.sku,
        db.func.sum(Inventory.stok_tersedia).label('total_stok'),
        db.func.min(Inventory.nama_item).label('nama_item'),  
        db.func.min(Inventory.stok_minimum).label('stok_minimum')  
    ).group_by(Inventory.sku).subquery()
    
    low_stock_items = db.session.query(
        total_stock.c.sku,
        total_stock.c.nama_item,
        total_stock.c.total_stok,
        total_stock.c.stok_minimum
    ).filter(
        total_stock.c.total_stok <= total_stock.c.stok_minimum
    ).all()
    
    return jsonify([{
        'sku': item.sku,
        'nama_item': item.nama_item,
        'stok_tersedia': item.total_stok,
        'stok_minimum': item.stok_minimum
    } for item in low_stock_items]), 200

# 5. Update inventory
@main.route('/inventory/<sku>/<batch_number>', methods=['PUT'])
@token_required
def update_inventory(sku, batch_number):
    data = request.json
    try:
        inventory = Inventory.query.filter_by(
            sku=sku,
            batch_number=batch_number
        ).first()
        
        if not inventory:
            return jsonify({
                'message': 'Item not found',
                'details': f'No inventory found with SKU {sku} and batch number {batch_number}'
            }), 404
        
        # List of allowed fields to update
        allowed_fields = {'nama_item', 'kategori', 'stok_tersedia', 'stok_minimum', 'harga'}
        
        # Only update allowed fields
        for key, value in data.items():
            if key in allowed_fields:
                setattr(inventory, key, value)
            # Optionally warn about invalid fields
            else:
                logger.warning(f"Attempted to update invalid/protected field: {key}")
        
        db.session.commit()
        return jsonify({
            'message': 'Inventory updated successfully',
            'sku': sku,
            'batch_number': batch_number
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating inventory: {str(e)}")
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

# Create new inventory
@main.route('/inventory', methods=['POST'])
@token_required
def create_inventory():
    data = request.json
    required_fields = {'sku', 'batch_number', 'nama_item', 'harga'}
    
    # Validate required fields
    if not all(field in data for field in required_fields):
        return jsonify({
            'message': 'Missing required fields',
            'required_fields': list(required_fields)
        }), 400
        
    try:
        # Check if inventory with same SKU and batch number already exists
        existing_inventory = Inventory.query.filter_by(
            sku=data['sku'],
            batch_number=data['batch_number']
        ).first()
        
        if existing_inventory:
            return jsonify({
                'message': 'Inventory already exists',
                'details': f"SKU {data['sku']} with batch number {data['batch_number']} is already in the system"
            }), 409
            
        # Create new inventory
        new_inventory = Inventory(**data)
        db.session.add(new_inventory)
        db.session.commit()
        
        return jsonify({
            'message': 'Inventory created successfully',
            'inventory': {
                'sku': new_inventory.sku,
                'batch_number': new_inventory.batch_number,
                'nama_item': new_inventory.nama_item,
                'kategori': new_inventory.kategori,
                'stok_tersedia': new_inventory.stok_tersedia,
                'stok_minimum': new_inventory.stok_minimum,
                'harga': new_inventory.harga,
                'waktu_pembaruan': new_inventory.waktu_pembaruan.isoformat()
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating inventory: {str(e)}")
        return jsonify({'error': str(e)}), 400

# Delete inventory
@main.route('/inventory/<sku>/<batch_number>', methods=['DELETE'])
@token_required
def delete_inventory(sku, batch_number):
    try:
        # Check for existing transactions
        existing_transactions = Transaksi.query.filter_by(
            sku=sku,
            batch_number=batch_number
        ).first()
        
        if existing_transactions:
            return jsonify({
                'message': 'Cannot delete inventory with existing transactions',
                'details': 'Delete operation rejected due to referential integrity'
            }), 409
            
        # Find and delete inventory
        inventory = Inventory.query.filter_by(
            sku=sku,
            batch_number=batch_number
        ).first()
        
        if not inventory:
            return jsonify({
                'message': 'Item not found',
                'details': f'No inventory found with SKU {sku} and batch number {batch_number}'
            }), 404
            
        db.session.delete(inventory)
        db.session.commit()
        
        return jsonify({
            'message': 'Inventory deleted successfully',
            'deleted_item': {
                'sku': sku,
                'batch_number': batch_number,
                'nama_item': inventory.nama_item
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting inventory: {str(e)}")
        return jsonify({'error': str(e)}), 400

# Get all transactions
@main.route('/transactions', methods=['GET'])
@token_required
def get_transactions():
    try:
        transactions = Transaksi.query.all()
        return jsonify([{
            'id_transaksi': t.id_transaksi,
            'sku': t.sku,
            'batch_number': t.batch_number,
            'jenis_transaksi': t.jenis_transaksi,
            'jumlah': t.jumlah,
            'amount': t.amount,
            'waktu_transaksi': t.waktu_transaksi.isoformat() if t.waktu_transaksi else None
        } for t in transactions]), 200
    except Exception as e:
        logger.error(f"Error fetching transactions: {str(e)}")
        return jsonify({'error': str(e)}), 400

# Add new transactions
@main.route('/transactions', methods=['POST'])
@token_required
def create_transaction():
    data = request.json
    required_fields = {'sku', 'batch_number', 'jumlah', 'amount'}
    
    if not all(field in data for field in required_fields):
        return jsonify({
            'message': 'Missing required fields',
            'required_fields': list(required_fields)
        }), 400
    
    # Force transaction type to be 'pengurangan' since it's a customer purchase
    data['jenis_transaksi'] = 'pengurangan'
    transaction = None
        
    try:
        with db.session.begin():
            # Validate inventory exists and lock for update
            inventory = Inventory.query.filter_by(
                sku=data['sku'], 
                batch_number=data['batch_number']
            ).with_for_update().first()
            
            if not inventory:
                return jsonify({
                    'message': 'Product not found',
                    'details': f"No product found with SKU {data['sku']} and batch number {data['batch_number']}"
                }), 404
            
            # Validate stock availability
            if inventory.stok_tersedia < data['jumlah']:
                return jsonify({
                    'message': 'Insufficient stock',
                    'available_stock': inventory.stok_tersedia,
                    'requested_quantity': data['jumlah']
                }), 400
            
            # Validate amount matches product price
            expected_amount = inventory.harga * data['jumlah']
            if abs(expected_amount - data['amount']) > 0.01:  # Using small delta for float comparison
                return jsonify({
                    'message': 'Invalid amount',
                    'expected_amount': expected_amount,
                    'provided_amount': data['amount']
                }), 400
            
            # Update inventory
            inventory.stok_tersedia -= data['jumlah']
            
            # Create transaction
            transaction = Transaksi(**data)
            db.session.add(transaction)
            
        # After successful commit, refresh the transaction to get the ID
        db.session.refresh(transaction)
        
        return jsonify({
            'message': 'Purchase successful',
            'transaction_id': transaction.id_transaksi,
            'details': {
                'product': inventory.nama_item,
                'quantity': data['jumlah'],
                'amount': data['amount'],
                'remaining_stock': inventory.stok_tersedia
            }
        }), 201
            
    except Exception as e:
        logger.error(f"Error processing purchase: {str(e)}")
        return jsonify({'error': 'Failed to process purchase'}), 400

# Update Transaction
@main.route('/transactions/<int:transaction_id>', methods=['PUT'])
@token_required
def update_transaction(transaction_id):
    data = request.json
    required_fields = {'jumlah', 'amount'}
    
    if not all(field in data for field in required_fields):
        return jsonify({
            'message': 'Missing required fields',
            'required_fields': list(required_fields)
        }), 400

    try:
        with db.session.begin():
            transaction = Transaksi.query.filter_by(id_transaksi=transaction_id).first()
            if not transaction:
                return jsonify({'message': 'Transaction not found'}), 404
            
            # Store old quantity for inventory adjustment
            old_quantity = transaction.jumlah
            
            # Get inventory and lock for update
            inventory = Inventory.query.filter_by(
                sku=transaction.sku,
                batch_number=transaction.batch_number
            ).with_for_update().first()
            
            if not inventory:
                return jsonify({'message': 'Product not found'}), 404
            
            # Revert old transaction effect (add back the old quantity)
            inventory.stok_tersedia += old_quantity
            
            # Validate new amount matches product price
            expected_amount = inventory.harga * data['jumlah']
            if abs(expected_amount - data['amount']) > 0.01:
                return jsonify({
                    'message': 'Invalid amount',
                    'expected_amount': expected_amount,
                    'provided_amount': data['amount']
                }), 400
            
            # Check if new quantity is available in stock
            if inventory.stok_tersedia < data['jumlah']:
                return jsonify({
                    'message': 'Insufficient stock',
                    'available_stock': inventory.stok_tersedia,
                    'requested_quantity': data['jumlah']
                }), 400
            
            # Update transaction
            transaction.jumlah = data['jumlah']
            transaction.amount = data['amount']
            
            # Apply new effect on inventory (subtract new quantity)
            inventory.stok_tersedia -= transaction.jumlah
            
            return jsonify({
                'message': 'Purchase updated successfully',
                'transaction_id': transaction_id,
                'details': {
                    'product': inventory.nama_item,
                    'quantity': transaction.jumlah,
                    'amount': transaction.amount,
                    'remaining_stock': inventory.stok_tersedia
                }
            }), 200
            
    except Exception as e:
        logger.error(f"Error updating purchase: {str(e)}")
        return jsonify({'error': 'Failed to update purchase'}), 400

@main.route('/transactions/<int:transaction_id>', methods=['DELETE'])
@token_required
def delete_transaction(transaction_id):
    try:
        with db.session.begin():
            transaction = Transaksi.query.filter_by(id_transaksi=transaction_id).first()
            if not transaction:
                return jsonify({'message': 'Transaction not found'}), 404
            
            # Get inventory and lock for update
            inventory = Inventory.query.filter_by(
                sku=transaction.sku,
                batch_number=transaction.batch_number
            ).with_for_update().first()
            
            if not inventory:
                return jsonify({'message': 'Product not found'}), 404
            
            # Revert transaction effect (add back the quantity since it was a purchase)
            inventory.stok_tersedia += transaction.jumlah
            
            # Delete transaction
            db.session.delete(transaction)
            
            return jsonify({
                'message': 'Purchase cancelled successfully',
                'details': {
                    'product': inventory.nama_item,
                    'returned_quantity': transaction.jumlah,
                    'current_stock': inventory.stok_tersedia
                }
            }), 200
            
    except Exception as e:
        logger.error(f"Error cancelling purchase: {str(e)}")
        return jsonify({'error': 'Failed to cancel purchase'}), 400