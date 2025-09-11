# Sistem Distribusi Produk

Web application untuk mengelola distribusi produk ke outlet dengan sistem komisi per produk menggunakan Flask dan PostgreSQL.

## Fitur Utama

- **Manajemen Outlet**: CRUD outlet dengan slot maksimal
- **Manajemen Produk**: CRUD produk dengan komisi per produk (bukan per outlet)
- **Distribusi**: Pencatatan distribusi produk ke outlet
- **Penjualan**: Pencatatan penjualan dengan perhitungan otomatis tagihan dan komisi
- **Pembayaran**: Pencatatan pembayaran dari outlet
- **Laporan**: Laporan lengkap penjualan dan komisi
- **User Management**: Admin dan karyawan dengan role-based access

## Perubahan dari Versi Sebelumnya

### 1. Database: Excel → PostgreSQL
- Menggunakan PostgreSQL untuk production-ready deployment
- Performa lebih baik dan concurrent access
- Data integrity dan ACID compliance

### 2. Komisi: Per Outlet → Per Produk
- Setiap produk memiliki persentase komisi sendiri
- Lebih fleksibel dalam penetapan margin keuntungan
- Tabel `outlets` tidak lagi memiliki kolom `persentase_komisi`
- Tabel `products` sekarang memiliki kolom `persentase_komisi`

## Instalasi

### Prerequisites
- Python 3.11+
- PostgreSQL 12+

### Setup Development

1. Clone repository dan masuk ke direktori:
```bash
cd minimalist
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Setup PostgreSQL:
```sql
-- Login ke PostgreSQL sebagai superuser
CREATE DATABASE distribusi_produk;
CREATE USER your_username WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE distribusi_produk TO your_username;
```

4. Setup environment variables:
```bash
cp .env.example .env
# Edit .env dengan kredensial database Anda
```

5. Initialize database:
```bash
python init_db.py
```

6. Run development server:
```bash
python app.py
```

### Setup Production

1. Set environment variables:
```bash
export FLASK_ENV=production
export DATABASE_URL=postgresql://user:password@host:port/database
export SECRET_KEY=your-secret-key-here
```

2. Initialize database:
```bash
python init_db.py
```

3. Run with Gunicorn:
```bash
gunicorn app:app
```

## Default Login

- **Admin**: username=`admin`, password=`admin123`
- **Karyawan**: username=`karyawan`, password=`karyawan123`

## Struktur Database

### Tables

1. **outlets** - Data outlet
   - id, nama, lokasi, kontak, slot_maksimal

2. **products** - Data produk dengan komisi
   - id, nama, harga, stok_pusat, **persentase_komisi**

3. **distributions** - Distribusi produk ke outlet
   - id, outlet_id, produk_id, jumlah, tanggal

4. **sales** - Penjualan dengan perhitungan otomatis
   - id, outlet_id, produk_id, jumlah_terjual, tanggal, tagihan, komisi, yang_harus_dibayar

5. **payments** - Pembayaran dari outlet
   - id, outlet_id, jumlah_bayar, tanggal_bayar, status

6. **users** - User management
   - id, username, password, role

## Deployment

### Heroku
```bash
# Login ke Heroku
heroku login

# Create app
heroku create your-app-name

# Add PostgreSQL addon
heroku addons:create heroku-postgresql:hobby-dev

# Set environment variables
heroku config:set FLASK_ENV=production
heroku config:set SECRET_KEY=your-secret-key

# Deploy
git add .
git commit -m "Deploy to production"
git push heroku main

# Initialize database
heroku run python init_db.py
```

### Docker
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:5000"]
```

## API Endpoints

- `/` - Dashboard admin
- `/karyawan/dashboard` - Dashboard karyawan
- `/outlet` - Manajemen outlet
- `/product` - Manajemen produk (dengan komisi)
- `/distribution` - Manajemen distribusi
- `/sales` - Manajemen penjualan
- `/payment` - Manajemen pembayaran
- `/report` - Laporan
- `/user` - User management

## Kontribusi

1. Fork repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Create Pull Request

## License

MIT License