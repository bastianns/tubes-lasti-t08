# utils.py
import jwt
from functools import wraps
from flask import request, jsonify, current_app
from datetime import datetime, timedelta
from models import User, Transaksi
from sqlalchemy import extract

def create_token(user_id):
    """
    Creates a JWT token for user authentication.
    
    The token includes the user ID and an expiration time. It is signed with 
    the application's JWT secret key to ensure security.
    """
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(hours=1)  # Token expires in 1 hour
    }
    token = jwt.encode(
        payload,
        current_app.config['JWT_SECRET_KEY'],
        algorithm='HS256'
    )
    return token

def token_required(f):
    """
    A decorator that checks if a valid JWT token is present in the request headers.
    
    This ensures that only authenticated users can access protected routes.
    It extracts the user ID from the token and makes it available to the route handler.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        
        if not token:
            return jsonify({'message': 'Token is missing'}), 401
        
        try:
            # Remove 'Bearer ' prefix if present
            if token.startswith('Bearer '):
                token = token.split(' ')[1]
            
            # Decode and verify the token
            data = jwt.decode(
                token,
                current_app.config['JWT_SECRET_KEY'],
                algorithms=['HS256']
            )
            
            # Get user from database
            current_user = User.query.get(data['user_id'])
            if not current_user:
                raise ValueError('User not found')
                
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token'}), 401
        except Exception as e:
            return jsonify({'message': str(e)}), 401
        
        return f(*args, **kwargs)
    return decorated

def calculate_monthly_sales(year, month):
    """
    Calculates the total sales for a specific month and year.
    
    This function aggregates all transactions marked as 'pengurangan' (sales)
    and sums their amounts to get the total sales value.
    """
    sales = Transaksi.query.filter(
        extract('year', Transaksi.waktu_transaksi) == year,
        extract('month', Transaksi.waktu_transaksi) == month,
        Transaksi.jenis_transaksi == 'pengurangan'
    ).with_entities(
        Transaksi.amount
    ).all()
    
    total_sales = sum(sale[0] for sale in sales)
    return total_sales