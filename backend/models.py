# models.py
from app import db
from datetime import datetime, timezone, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
 
def get_wib_time():
    return datetime.now(timezone(timedelta(hours=7)))  # UTC+7 for WIB

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Inventory(db.Model):
    __tablename__ = 'inventory'

    sku = db.Column(db.String(100), primary_key=True)
    batch_number = db.Column(db.String(50), primary_key=True)
    nama_item = db.Column(db.String(100), nullable=False)
    kategori = db.Column(db.String(50))
    stok_tersedia = db.Column(db.Integer, default=0)
    stok_minimum = db.Column(db.Integer, default=10)
    harga = db.Column(db.Float, nullable=False)
    waktu_pembaruan = db.Column(
        db.DateTime(timezone=True),
        default=get_wib_time,
        onupdate=get_wib_time
    )

class Transaksi(db.Model):
    __tablename__ = 'transaksi'

    id_transaksi = db.Column(db.Integer, primary_key=True)
    total_amount = db.Column(db.Float, nullable=False)
    waktu_transaksi = db.Column(
        db.DateTime(timezone=True), 
        default=get_wib_time
    )
    
    # Add cascade="all, delete-orphan" to properly handle deletion
    details = db.relationship(
        'TransaksiDetail', 
        backref='transaksi', 
        lazy=True,
        cascade="all, delete-orphan"
    )
    
class TransaksiDetail(db.Model):
    __tablename__ = 'transaksi_detail'
    
    id = db.Column(db.Integer, primary_key=True)
    id_transaksi = db.Column(db.Integer, db.ForeignKey('transaksi.id_transaksi'), nullable=False)
    sku = db.Column(db.String(100), nullable=False)
    batch_number = db.Column(db.String(50), nullable=False)
    jumlah = db.Column(db.Integer, nullable=False)
    harga_satuan = db.Column(db.Float, nullable=False)
    subtotal = db.Column(db.Float, nullable=False)
    
    __table_args__ = (
        db.ForeignKeyConstraint(
            ['sku', 'batch_number'],
            ['inventory.sku', 'inventory.batch_number']
        ),
    )