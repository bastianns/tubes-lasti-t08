# routes.py
from flask import Blueprint, jsonify, request, current_app
from models import User, Inventory, Transaksi
from app import db
from utils import token_required, create_token, calculate_monthly_sales
from sqlalchemy import extract, text
from datetime import datetime
import logging

# Configure logger
logger = logging.getLogger(__name__)

# Create Blueprint for routing
main = Blueprint('main', __name__)

@main.route('/health')
def health_check():
    """Check the health status of the application and database connection."""
    try:
        # Test database connection
        db.session.execute(text('SELECT 1'))
        db.session.commit()
        
        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'timestamp': datetime.utcnow().isoformat(),
            'environment': current_app.config['FLASK_ENV']
        }), 200
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        db.session.rollback()
        
        return jsonify({
            'status': 'unhealthy',
            'database': 'disconnected',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500

@main.route('/login', methods=['POST'])
def login():
    """Handle user authentication and return JWT token."""
    data = request.json
    user = User.query.filter_by(username=data.get('username')).first()
    
    if user and user.check_password(data.get('password')):
        token = create_token(user.id)
        return jsonify({'token': token}), 200
    return jsonify({'message': 'Invalid credentials'}), 401

@main.route('/inventory/low-stock', methods=['GET'])
@token_required
def get_low_stock():
    """Get inventory items with stock at or below minimum level."""
    low_stock_items = Inventory.query.filter(
        Inventory.stok_tersedia <= Inventory.stok_minimum
    ).all()
    
    return jsonify([{
        'sku': item.sku,
        'nama_item': item.nama_item,
        'stok_tersedia': item.stok_tersedia,
        'stok_minimum': item.stok_minimum,
        'kategori': item.kategori,
        'batch_number': item.batch_number
    } for item in low_stock_items]), 200

@main.route('/transactions/monthly-sales', methods=['GET'])
@token_required
def get_monthly_sales():
    """Get total sales for a specific month and year."""
    year = request.args.get('year', datetime.now().year, type=int)
    month = request.args.get('month', datetime.now().month, type=int)
    
    total_sales = calculate_monthly_sales(year, month)
    return jsonify({
        'year': year,
        'month': month,
        'total_sales': total_sales
    }), 200

@main.route('/transactions', methods=['POST', 'GET'])
@token_required
def handle_transactions():
    """Handle transaction creation and retrieval."""
    if request.method == 'GET':
        transactions = Transaksi.query.order_by(Transaksi.waktu_transaksi.desc()).all()
        return jsonify([{
            'id_transaksi': t.id_transaksi,
            'sku': t.sku,
            'batch_number': t.batch_number,
            'jenis_transaksi': t.jenis_transaksi,
            'jumlah': t.jumlah,
            'amount': t.amount,
            'waktu_transaksi': t.waktu_transaksi.isoformat()
        } for t in transactions]), 200
    
    data = request.json
    try:
        with db.session.begin():
            # Lock the inventory record for update
            inventory = Inventory.query.filter_by(
                sku=data['sku'],
                batch_number=data['batch_number']
            ).with_for_update().first()
            
            if not inventory:
                raise ValueError('Inventory item not found')
            
            # Validate and update inventory stock
            if data['jenis_transaksi'] == 'pengurangan':
                if inventory.stok_tersedia < data['jumlah']:
                    raise ValueError(f'Insufficient stock. Available: {inventory.stok_tersedia}, Requested: {data["jumlah"]}')
                inventory.stok_tersedia -= data['jumlah']
            elif data['jenis_transaksi'] == 'penambahan':
                inventory.stok_tersedia += data['jumlah']
            else:
                raise ValueError('Invalid transaction type')
            
            # Create transaction record
            transaction = Transaksi(**data)
            db.session.add(transaction)
        
        return jsonify({
            'message': 'Transaction successful',
            'new_stock_level': inventory.stok_tersedia
        }), 201
        
    except ValueError as e:
        logger.error(f"Transaction error: {str(e)}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Unexpected error in transaction: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500

@main.route('/inventory/<sku>', methods=['PUT'])
@token_required
def update_inventory(sku):
    """Update inventory item details."""
    data = request.json
    try:
        inventory = Inventory.query.filter_by(sku=sku).first()
        if not inventory:
            return jsonify({'message': 'Item not found'}), 404
        
        # Update only allowed fields
        allowed_fields = {'nama_item', 'kategori', 'stok_minimum', 'harga'}
        for key, value in data.items():
            if key in allowed_fields:
                setattr(inventory, key, value)
        
        db.session.commit()
        return jsonify({
            'message': 'Inventory updated successfully',
            'inventory': {
                'sku': inventory.sku,
                'nama_item': inventory.nama_item,
                'kategori': inventory.kategori,
                'stok_tersedia': inventory.stok_tersedia,
                'stok_minimum': inventory.stok_minimum,
                'harga': inventory.harga
            }
        }), 200
    except Exception as e:
        logger.error(f"Error updating inventory: {str(e)}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 400