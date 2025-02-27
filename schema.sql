-- ./schema.sql

-- Basic database schema and initial data

-- Create extensions if needed
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Grant basic permissions
ALTER USER apotek_user WITH CREATEDB;
GRANT ALL PRIVILEGES ON SCHEMA public TO apotek_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL PRIVILEGES ON TABLES TO apotek_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL PRIVILEGES ON SEQUENCES TO apotek_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL PRIVILEGES ON FUNCTIONS TO apotek_user;
ALTER SCHEMA public OWNER TO apotek_user;

-- Create tables
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(80) UNIQUE NOT NULL,
    password_hash VARCHAR(200) NOT NULL
);

CREATE TABLE IF NOT EXISTS inventory (
    sku VARCHAR(100),
    batch_number VARCHAR(50),
    nama_item VARCHAR(100) NOT NULL,
    kategori VARCHAR(50),
    stok_tersedia INTEGER DEFAULT 0,
    stok_minimum INTEGER DEFAULT 10,
    harga FLOAT NOT NULL,
    waktu_pembaruan TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (sku, batch_number)
);

CREATE TABLE IF NOT EXISTS transaksi (
    id_transaksi SERIAL PRIMARY KEY,
    sku VARCHAR(100) NOT NULL,
    batch_number VARCHAR(50) NOT NULL,
    jenis_transaksi VARCHAR(50) NOT NULL,
    jumlah INTEGER NOT NULL,
    amount FLOAT NOT NULL,
    waktu_transaksi TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sku, batch_number) REFERENCES inventory(sku, batch_number)
);

-- Grant table permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO apotek_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO apotek_user;

-- Insert initial admin user (password: admin123)
INSERT INTO users (username, password_hash) VALUES 
('admin', 'pbkdf2:sha256:600000$dR7OPGAc$d82c87a9ce4983794a0599d5967d428513f197754666d8ea91aa99b02c5467f8');

-- Insert sample inventory
INSERT INTO inventory (sku, batch_number, nama_item, kategori, stok_tersedia, stok_minimum, harga) VALUES 
('PARA001', 'B001', 'Paracetamol 500mg', 'Obat Bebas', 100, 20, 10000),
('VITC001', 'B002', 'Vitamin C 500mg', 'Suplemen', 50, 10, 25000);