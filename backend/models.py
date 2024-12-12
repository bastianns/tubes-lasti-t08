from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Inventory(db.Model):
    __tablename__ = 'inventory'

    sku = db.Column(db.String(100), primary_key=True)
    batch_number = db.Column(db.String(50), primary_key=True)
    nama_item = db.Column(db.String(100), nullable=False)
    kategori = db.Column(db.String(50))
    stok_tersedia = db.Column(db.Integer, default=0)
    stok_minimum = db.Column(db.Integer, default=10)
    waktu_pembaruan = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())


class Transaksi(db.Model):
    __tablename__ = 'transaksi'

    id_transaksi = db.Column(db.Integer, primary_key=True)
    sku = db.Column(db.String(100), nullable=False)
    batch_number = db.Column(db.String(50), nullable=False)
    jenis_transaksi = db.Column(db.String(50), nullable=False)
    jumlah = db.Column(db.Integer, nullable=False)
    amount = db.Column(db.Numeric, nullable=False)
    waktu_transaksi = db.Column(db.DateTime, default=db.func.now())
    
    __table_args__ = (
        db.ForeignKeyConstraint(
            ['sku', 'batch_number'],
            ['inventory.sku', 'inventory.batch_number']
        ),
    )

