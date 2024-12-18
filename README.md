# Prototype Layanan Sistem dan Teknologi Informasi - Kelompok 8
## Anggota
- Arvyno Pranata Limahardja - 18222007
- David Dewanto - 18222027
- Ricky Wijaya - 18222043
- Bastian Natanael Sibarani - 18222053
- Dedy Hofmanindo Saragih - 18222085

# Sistem ERP untuk Manajemen Apotek
Proyek ini merupakan implementasi prototipe sistem Enterprise Resource Planning (ERP) sederhana untuk manajemen apotek, yang dikembangkan sebagai salah satu requirement tugas dari mata kuliah II3120 Layanan Sistem dan Teknologi Informasi di program studi Sistem dan Teknologi Informasi Institut Teknologi Bandung (ITB). Sistem ini membantu apotek dalam mengelola inventaris, melacak transaksi, dan memantau kinerja penjualan.

# Cara Mengakses Prototype
## Website (Disarankan)
Dapat mengakses prototype secara langsung melalui http://apotek-erp.my.id/

## Local (Tidak Disarankan)
Pastikan sudah mengunduh Docker-Desktop dan juga Git CLI, serta mematikan layanan Postgres (apabila sudah pernah mengunduh dan menjalankan Postgres melalui services.msc)
1. Masuk ke dalam folder project yang diinginkan
2. Lakukan git clone dengan membuka terminal dan memasukkan "git clone "https://github.com/bastianns/tubes-lasti-t08.git""
3. Setelah itu jalankan "docker-compose up"
4. Prototype dapat dijalankan dengan membuka http://localhost pada browser
* Apabila tidak bisa disarankan langsung mengakses prototype melalui deployment yang sudah ada (http://apotek-erp.my.id/)

# Deskripsi Detail Prototype
## Fitur Utama

- **Autentikasi Pengguna**
  - Fungsi login/logout yang aman
  - Autentikasi berbasis token
  - Rute terproteksi untuk pengguna yang terautentikasi

- **Manajemen Inventaris**
  - Tambah, edit, dan hapus item inventaris
  - Pantau level stok dengan peringatan stok minimum
  - Pelacakan nomor batch
  - Fungsi pencarian dan filter

- **Manajemen Transaksi**
  - Buat transaksi baru
  - Lihat riwayat transaksi
  - Edit atau batalkan transaksi yang ada
  - Filter transaksi berdasarkan rentang tanggal dan ID transaksi

- **Dashboard**
  - Ringkasan penjualan bulanan dengan grafik
  - Peringatan stok menipis
  - Pemantauan stok secara real-time

## Teknologi yang Digunakan

### Backend
- Flask (Framework web Python)
- PostgreSQL (Database)
- SQLAlchemy (ORM)
- JWT untuk autentikasi

### Frontend
- React dengan TypeScript
- Tailwind CSS untuk styling
- React Query untuk manajemen state
- Recharts untuk visualisasi data

## Struktur Proyek

Proyek menggunakan arsitektur client-server:

```
├── backend/
│   ├── app.py           # Aplikasi Flask utama
│   ├── config.py        # Pengaturan konfigurasi
│   ├── models.py        # Model database
│   ├── routes.py        # Endpoint API
│   ├── schema.sql       # Skema database
│   └── utils.py         # Fungsi pembantu
│
└── frontend/
    ├── src/
    │   ├── components/  # Komponen UI yang dapat digunakan kembali
    │   ├── pages/       # Komponen halaman
    │   ├── services/    # Fungsi layanan API
    │   └── utils/       # Utilitas pembantu
    └── public/          # Aset statis
```

## Pengembangan Kode

### Catatan Penting Implementasi
Kode implementasi saat ini telah dikonfigurasi khusus untuk mendukung deployment di Virtual Private Server (VPS), sehingga **tidak dapat dikembangkan secara lokal**. Hal ini merupakan bagian dari desain arsitektur yang telah disesuaikan dengan kebutuhan deployment production.
- Semua kode menggunakan TypeScript untuk type safety
- Penggunaan React Query untuk state management
- Implementasi JWT untuk autentikasi
- Database menggunakan PostgreSQL dengan proper indexing
- Error handling yang konsisten di semua layer
- UI components yang reusable dan responsive

### Struktur Pengembangan

#### Backend
- **Models**: Mendefinisikan struktur data dan relasi database
  ```python
  # models.py
  class Inventory(db.Model):
      sku = db.Column(db.String(100), primary_key=True)
      batch_number = db.Column(db.String(50), primary_key=True)
      nama_item = db.Column(db.String(100), nullable=False)
      # ... field lainnya
  ```

- **Routes**: Implementasi endpoint API
  ```python
  # routes.py
  @main.route('/inventory', methods=['GET'])
  @token_required
  def get_inventory():
      # Implementasi logic
  ```

- **Services**: Logic bisnis utama
  ```python
  # utils.py
  def calculate_monthly_sales(year, month):
      # Implementasi perhitungan
  ```

#### Frontend
Frontend dikembangkan menggunakan React dengan Vite sebagai build tool. Vite dipilih karena memberikan developer experience yang lebih baik dengan fitur Hot Module Replacement (HMR) yang cepat.

- **Components**: Komponen UI yang reusable
  ```typescript
  // components/Button.tsx
  export const Button = ({ children, ...props }) => {
    // Implementasi komponen
  }
  ```

- **Pages**: Implementasi halaman utama
  ```typescript
  // pages/inventory/InventoryPage.tsx
  const InventoryPage = () => {
    // Implementasi halaman
  }
  ```

- **Services**: Integrasi dengan API
  ```typescript
  // services/inventoryService.ts
  export const inventoryService = {
    getAllInventory: async () => {
      // Implementasi service
    }
  }
  ```

### Implementasi Kode Penting

Berikut adalah penjelasan komponen-komponen utama dalam implementasi sistem:

#### Database Models (models.py)
Mendefinisikan struktur tabel dan relasi database.

```python
class Inventory(db.Model):
    sku = db.Column(db.String(100), primary_key=True)
    batch_number = db.Column(db.String(50), primary_key=True)
    nama_item = db.Column(db.String(100), nullable=False)
```

#### API Endpoints (routes.py)
Menangani request HTTP dan implementasi business logic.

```python
@main.route('/inventory', methods=['GET'])
@token_required
def get_inventory():
    query = Inventory.query
    if search:
        query = query.filter(Inventory.nama_item.ilike(f"%{search}%"))
```

#### Reusable Components (components/Button.tsx)
Komponen UI yang dapat digunakan ulang dengan styling konsisten.

```typescript
export const Button = ({ variant = 'primary', children }) => {
  return (
    <button className={`px-4 py-2 ${variant === 'primary' ? 'bg-blue-600' : 'bg-gray-200'}`}>
      {children}
    </button>
  );
};
```

#### Data Fetching (pages/InventoryPage.tsx)
Manajemen state dan fetching data dari API.

```typescript
const { data: inventory } = useQuery({
    queryKey: ['inventory'],
    queryFn: inventoryService.getAllInventory
});
```

#### API Services (services/inventoryService.ts)
Centralized API calls dengan type safety.

```typescript
export const inventoryService = {
    getAllInventory: async () => {
        const response = await api.get('/inventory');
        return response.data;
    }
};
```

#### Authentication (utils/axios.ts)
Manajemen token dan error handling.

```typescript
api.interceptors.request.use((config) => {
    const token = localStorage.getItem('token');
    if (token) config.headers.Authorization = `Bearer ${token}`;
    return config;
});
```

#### Transaction Processing (routes.py)
Atomic database transactions dengan error handling.

```python
with db.session.begin():
    inventory = Inventory.query.with_for_update().filter_by(sku=sku).first()
    inventory.stok_tersedia -= quantity
```

#### Error Handling
Penanganan error yang konsisten dan user-friendly.

```python
try:
    # Process transaction
except ValueError as e:
    return jsonify({'message': str(e)}), 400
```

#### Database Schema (schema.sql)
Definisi struktur database dan indexing.

```sql
CREATE TABLE inventory (
    sku VARCHAR(100),
    batch_number VARCHAR(50),
    PRIMARY KEY (sku, batch_number)
);
```

### Praktik Pengembangan yang Direkomendasikan

1. **Type Safety**
   - Gunakan TypeScript untuk type checking
   - Definisikan interface untuk semua data structures
   ```typescript
   interface InventoryItem {
     sku: string;
     batch_number: string;
     nama_item: string;
     // ... properti lainnya
   }
   ```

2. **State Management**
   - Gunakan React Query untuk manajemen state server
   - Implementasikan error handling yang konsisten
   ```typescript
   const { data, isLoading, error } = useQuery({
     queryKey: ['inventory'],
     queryFn: inventoryService.getAllInventory
   });
   ```

3. **Database**
   - Gunakan migrations untuk perubahan schema
   - Implementasikan proper indexing untuk optimasi
   ```sql
   CREATE INDEX idx_inventory_sku ON inventory(sku);
   ```

4. **Security**
   - Implementasikan JWT untuk autentikasi
   - Validasi semua input user
   - Gunakan prepared statements untuk query database

## Cara Menggunakan Aplikasi

1. **Login**
   - Kredensial default:
     - Username: admin
     - Password: admin123

2. **Mengelola Inventaris**
   - Buka halaman Inventory
   - Gunakan tombol "Add New Item" untuk membuat item baru
   - Setiap item memerlukan:
     - SKU (identifikasi unik)
     - Nomor batch
     - Nama item
     - Kategori
     - Level stok
     - Harga

3. **Membuat Transaksi**
   - Buka halaman Transactions
   - Cari item berdasarkan SKU dan nomor batch
   - Tambahkan item ke keranjang
   - Sesuaikan jumlah sesuai kebutuhan
   - Submit transaksi

4. **Melihat Laporan**
   - Dashboard menampilkan grafik penjualan bulanan
   - Pantau item dengan stok menipis
   - Lihat riwayat transaksi dengan filter

## Masalah Umum dan Solusi

- **Masalah Koneksi Database**
  - Periksa layanan PostgreSQL berjalan
  - Verifikasi kredensial database
  - Pastikan konfigurasi jaringan di Docker sudah benar

- **Error Autentikasi**
  - Hapus penyimpanan browser
  - Periksa masa berlaku token
  - Verifikasi kredensial
