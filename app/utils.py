# ./app/utils.py

from functools import wraps
from flask import jsonify, request
import jwt
from datetime import datetime, timedelta
from config import Config
from app import db

def create_token(user_id):
    """Create JWT token for authentication"""
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(hours=1)
    }
    return jwt.encode(payload, Config.JWT_SECRET_KEY, algorithm='HS256')

def token_required(f):
    """Decorator to protect routes"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        try:
            token = token.split()[1]  # Remove 'Bearer ' prefix
            data = jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=['HS256'])
        except:
            return jsonify({'message': 'Token is invalid!'}), 401
        return f(*args, **kwargs)
    return decorated

def calculate_monthly_sales(year=None, month=None):
    """Calculate total sales for a given month"""
    from app.models import Transaksi
    from sqlalchemy import extract
    
    query = Transaksi.query
    if year and month:
        query = query.filter(
            extract('year', Transaksi.waktu_transaksi) == year,
            extract('month', Transaksi.waktu_transaksi) == month
        )
    return query.with_entities(db.func.sum(Transaksi.amount)).scalar() or 0