# routes.py
from flask import Blueprint, jsonify, request
from models import User, Inventory, Transaksi, TransaksiDetail
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
    
    try:
        # Find the user
        user = User.query.filter_by(username=username).first()
        
        if not user:
            logger.warning(f"User not found: {username}")
            return jsonify({'message': 'Invalid credentials'}), 401
        
        # Check password
        if user.check_password(password):
            token = create_token(user.id)
            return jsonify({'token': token}), 200
        
        return jsonify({'message': 'Invalid credentials'}), 401
        
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return jsonify({'message': 'Login failed', 'error': str(e)}), 500

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
        Inventory.stok_tersedia < Inventory.stok_minimum
    ).all()
    
    return jsonify([{
        'sku': item.sku,
        'batch_number': item.batch_number,
        'nama_item': item.nama_item,
        'stok_tersedia': item.stok_tersedia,
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
                'message': 'Item not found'
            }), 404
        
        sku_consistent_fields = {'nama_item', 'kategori', 'stok_minimum', 'harga'}
        batch_specific_fields = {'stok_tersedia'}
        
        if any(field in data for field in sku_consistent_fields):
            update_data = {k: v for k, v in data.items() if k in sku_consistent_fields}
            if update_data:
                Inventory.query.filter(
                    Inventory.sku == sku
                ).update(update_data)
        
        batch_updates = {k: v for k, v in data.items() if k in batch_specific_fields}
        if batch_updates:
            for key, value in batch_updates.items():
                setattr(inventory, key, value)
        
        db.session.commit()
        db.session.refresh(inventory)
        
        return jsonify({
            'message': 'Inventory updated successfully',
            'inventory': {
                'sku': inventory.sku,
                'batch_number': inventory.batch_number,
                'nama_item': inventory.nama_item,
                'kategori': inventory.kategori,
                'stok_tersedia': inventory.stok_tersedia,
                'stok_minimum': inventory.stok_minimum,
                'harga': inventory.harga,
                'waktu_pembaruan': inventory.waktu_pembaruan.isoformat()
            }
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
    required_fields = {'sku', 'batch_number','kategori', 'nama_item', 'harga'}
    
    if not all(field in data for field in required_fields):
        return jsonify({
            'message': 'Missing required fields',
            'required_fields': list(required_fields)
        }), 400
        
    try:
        existing_sku = Inventory.query.filter_by(sku=data['sku']).first()
        
        if existing_sku:
            data['nama_item'] = existing_sku.nama_item
            data['kategori'] = existing_sku.kategori
            data['stok_minimum'] = existing_sku.stok_minimum
            data['harga'] = existing_sku.harga
        
        existing_inventory = Inventory.query.filter_by(
            sku=data['sku'],
            batch_number=data['batch_number']
        ).first()
        
        if existing_inventory:
            return jsonify({
                'message': 'Inventory already exists'
            }), 409
        
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
        # Check for existing transactions in TransaksiDetail instead of Transaksi
        existing_transactions = TransaksiDetail.query.filter_by(
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
            'total_amount': t.total_amount,
            'waktu_transaksi': t.waktu_transaksi.isoformat() if t.waktu_transaksi else None,
            'items': [{
                'sku': detail.sku,
                'batch_number': detail.batch_number,
                'jumlah': detail.jumlah,
                'harga_satuan': detail.harga_satuan,
                'subtotal': detail.subtotal
            } for detail in t.details]
        } for t in transactions]), 200
    except Exception as e:
        logger.error(f"Error fetching transactions: {str(e)}")
        return jsonify({'error': str(e)}), 400

# Add new transactions
@main.route('/transactions', methods=['POST'])
@token_required
def create_transaction():
    data = request.json
    if not isinstance(data.get('items'), list) or not data['items']:
        return jsonify({
            'message': 'At least one item is required',
            'required_fields': ['items[].sku', 'items[].batch_number', 'items[].jumlah']
        }), 400
    
    try:
        # Initialize variables outside the transaction block
        total_amount = 0
        transaction_details = []
        
        # Start transaction
        with db.session.begin():
            # Process each item
            for item in data['items']:
                # Validate required fields
                if not all(field in item for field in ['sku', 'batch_number', 'jumlah']):
                    raise ValueError("Missing required fields in item")
                
                # Get inventory and lock for update
                inventory = Inventory.query.filter_by(
                    sku=item['sku'], 
                    batch_number=item['batch_number']
                ).with_for_update().first()
                
                if not inventory:
                    raise ValueError(f"Product not found: SKU {item['sku']}, Batch {item['batch_number']}")
                
                # Validate stock availability
                if inventory.stok_tersedia < item['jumlah']:
                    raise ValueError(f"Insufficient stock for {inventory.nama_item}")
                
                # Calculate subtotal
                subtotal = inventory.harga * item['jumlah']
                total_amount += subtotal
                
                # Update inventory
                inventory.stok_tersedia -= item['jumlah']
                
                # Create transaction detail
                transaction_details.append({
                    'sku': item['sku'],
                    'batch_number': item['batch_number'],
                    'jumlah': item['jumlah'],
                    'harga_satuan': inventory.harga,
                    'subtotal': subtotal
                })
            
            # Create main transaction
            transaction = Transaksi(total_amount=total_amount)
            db.session.add(transaction)
            db.session.flush()  # Get transaction ID
            
            # Create transaction details
            for detail in transaction_details:
                detail['id_transaksi'] = transaction.id_transaksi
                db.session.add(TransaksiDetail(**detail))
            
            # No need to call commit() - the context manager will handle it
            
        # After successful commit, return response
        return jsonify({
            'message': 'Transaction successful',
            'transaction_id': transaction.id_transaksi,
            'total_amount': total_amount,
            'details': transaction_details
        }), 201
            
    except ValueError as e:
        # No need to call rollback() - the context manager will handle it
        return jsonify({'message': str(e)}), 400
    except Exception as e:
        logger.error(f"Error processing transaction: {str(e)}")
        return jsonify({'error': 'Failed to process transaction'}), 400

# Update Transaction
@main.route('/transactions/<int:transaction_id>', methods=['PUT'])
@token_required
def update_transaction(transaction_id):
    data = request.json
    if not isinstance(data.get('items'), list) or not data['items']:
        return jsonify({
            'message': 'At least one item is required',
            'required_fields': ['items[].sku', 'items[].batch_number', 'items[].jumlah']
        }), 400

    try:
        # Initialize variables outside transaction block
        total_amount = 0
        new_details = []

        with db.session.begin():
            # Get transaction and validate
            transaction = Transaksi.query.filter_by(id_transaksi=transaction_id).first()
            if not transaction:
                return jsonify({'message': 'Transaction not found'}), 404
            
            # Revert all inventory changes
            for detail in transaction.details:
                inventory = Inventory.query.filter_by(
                    sku=detail.sku,
                    batch_number=detail.batch_number
                ).with_for_update().first()
                
                if inventory:
                    inventory.stok_tersedia += detail.jumlah
            
            # Delete old transaction details
            TransaksiDetail.query.filter_by(id_transaksi=transaction_id).delete()
            
            # Process new items
            for item in data['items']:
                # Validate required fields
                if not all(field in item for field in ['sku', 'batch_number', 'jumlah']):
                    raise ValueError("Missing required fields in item")
                
                # Get inventory and lock for update
                inventory = Inventory.query.filter_by(
                    sku=item['sku'],
                    batch_number=item['batch_number']
                ).with_for_update().first()
                
                if not inventory:
                    raise ValueError(f"Product not found: SKU {item['sku']}, Batch {item['batch_number']}")
                
                # Validate stock availability
                if inventory.stok_tersedia < item['jumlah']:
                    raise ValueError(f"Insufficient stock for {inventory.nama_item}")
                
                # Calculate subtotal
                subtotal = inventory.harga * item['jumlah']
                total_amount += subtotal
                
                # Update inventory
                inventory.stok_tersedia -= item['jumlah']
                
                # Create new transaction detail
                new_detail = TransaksiDetail(
                    id_transaksi=transaction_id,
                    sku=item['sku'],
                    batch_number=item['batch_number'],
                    jumlah=item['jumlah'],
                    harga_satuan=inventory.harga,
                    subtotal=subtotal
                )
                db.session.add(new_detail)
                new_details.append(new_detail)
            
            # Update transaction total
            transaction.total_amount = total_amount
            
        # Return response after successful commit
        return jsonify({
            'message': 'Transaction updated successfully',
            'transaction_id': transaction_id,
            'total_amount': total_amount,
            'details': [{
                'sku': detail.sku,
                'batch_number': detail.batch_number,
                'jumlah': detail.jumlah,
                'harga_satuan': detail.harga_satuan,
                'subtotal': detail.subtotal
            } for detail in new_details]
        }), 200
            
    except ValueError as e:
        return jsonify({'message': str(e)}), 400
    except Exception as e:
        logger.error(f"Error updating transaction: {str(e)}")
        return jsonify({'error': 'Failed to update transaction'}), 400

# Delete Transaction
@main.route('/transactions/<int:transaction_id>', methods=['DELETE'])
@token_required
def delete_transaction(transaction_id):
    try:
        details = []

        with db.session.begin():
            # Get transaction and validate
            transaction = Transaksi.query.filter_by(id_transaksi=transaction_id).first()
            if not transaction:
                return jsonify({'message': 'Transaction not found'}), 404
            
            # Revert inventory changes
            for detail in transaction.details:
                inventory = Inventory.query.filter_by(
                    sku=detail.sku,
                    batch_number=detail.batch_number
                ).with_for_update().first()
                
                if inventory:
                    inventory.stok_tersedia += detail.jumlah
                    details.append({
                        'product': inventory.nama_item,
                        'returned_quantity': detail.jumlah,
                        'current_stock': inventory.stok_tersedia
                    })
            
            # Delete transaction (cascade will handle details)
            db.session.delete(transaction)
            
        # Return response after successful commit
        return jsonify({
            'message': 'Transaction cancelled successfully',
            'transaction_id': transaction_id,
            'details': details
        }), 200
            
    except Exception as e:
        logger.error(f"Error cancelling transaction: {str(e)}")
        return jsonify({'error': 'Failed to cancel transaction'}), 400