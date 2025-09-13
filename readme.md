# 🏪 Sistem Manajemen Distribusi & Penjualan

<div align="center">

![Flask](https://img.shields.io/badge/Flask-2.0+-000000?style=for-the-badge&logo=flask&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5.0+-7952B3?style=for-the-badge&logo=bootstrap&logoColor=white)

**Sistem manajemen lengkap untuk distribusi produk ke outlet dengan tracking penjualan, pembayaran, dan laporan komprehensif**

[Demo](#demo) • [Instalasi](#instalasi) • [Fitur](#fitur) • [Dokumentasi](#dokumentasi)

</div>

---

## 🌟 Fitur Utama

### 👨‍💼 **Multi-Role Management**
- **Admin**: Akses penuh ke semua fitur sistem
- **Karyawan**: Dashboard khusus dengan akses terbatas

### 🏢 **Manajemen Outlet**
- ✅ CRUD outlet dengan informasi lokasi dan kontak
- 📊 Tracking slot maksimal dan penggunaan slot
- 📈 Monitoring kapasitas distribusi real-time

### 📦 **Manajemen Produk**
- ✅ Master data produk dengan harga dan stok
- 💰 Sistem komisi per produk (persentase)
- 📊 Tracking stok pusat otomatis

### 🚚 **Sistem Distribusi**
- ✅ Distribusi produk ke outlet dengan validasi slot
- 📊 Tracking stok outlet real-time
- 🔄 Update otomatis stok pusat dan outlet

### 💰 **Manajemen Penjualan**
- ✅ Recording penjualan dengan kalkulasi komisi otomatis
- 📊 Tracking tagihan outlet
- 💳 Sistem billing terintegrasi

### 💳 **Sistem Pembayaran**
- ✅ Recording pembayaran dari outlet
- 📊 Tracking saldo tagihan
- 📄 Generate invoice PDF otomatis

### 📊 **Reporting & Analytics**
- 📈 Dashboard real-time dengan metrics
- 📊 Laporan detail per outlet dan periode
- 📄 Export PDF invoice professional
- 📊 Analisis slot usage dan performance

---

## 🚀 Quick Start

### Prasyarat
```bash
Python 3.8+
Flask 2.0+
PostgreSQL 12+
```

### Instalasi

1. **Clone repository**
```bash
git clone <repository-url>
cd sistem-distribusi
```

2. **Setup virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# atau
venv\Scripts\activate     # Windows
```

3. **Install dependencies**
```bash
pip install flask psycopg2-binary reportlab
```

4. **Setup PostgreSQL Database**
```bash
# Buat database PostgreSQL
createdb sistem_distribusi

# Atau melalui psql
psql -U postgres
CREATE DATABASE sistem_distribusi;
\q
```

5. **Setup environment variables**
```bash
# Buat file .env atau set environment variables
export DATABASE_URL="postgresql://username:password@localhost:5432/sistem_distribusi"
# atau
export DB_HOST="localhost"
export DB_PORT="5432"
export DB_NAME="sistem_distribusi"
export DB_USER="your_username"
export DB_PASSWORD="your_password"
```

6. **Initialize database**
```bash
python -c "from utils.data_helper import DataHelper; DataHelper().init_database()"
```

7. **Run aplikasi**
```bash
python app.py
```

8. **Akses aplikasi**
```
http://localhost:5000
```

### Login Default
- **Username**: `admin`
- **Password**: `admin123`
- **Role**: Administrator

---

## 📁 Struktur Project

```
📦 sistem-distribusi/
├── 🐍 app.py                 # Main Flask application
├── 📁 utils/
│   ├── 🔧 data_helper.py     # Database operations & business logic (PostgreSQL)
│   └── 📄 pdf_generator.py   # PDF invoice generation
├── 📁 templates/             # Jinja2 templates
│   ├── 📁 auth/             # Authentication templates
│   ├── 📁 outlet/           # Outlet management
│   ├── 📁 product/          # Product management
│   ├── 📁 distribution/     # Distribution tracking
│   ├── 📁 sales/            # Sales recording
│   ├── 📁 payment/          # Payment management
│   ├── 📁 invoice/          # Invoice templates
│   ├── 📁 report/           # Reporting dashboard
│   ├── 📁 user/             # User management
│   └── 📁 karyawan/         # Employee dashboard
└── 📁 static/
    └── 🎨 style.css         # Custom styling
```

---

## 🎯 Fitur Detail

### 🏢 **Outlet Management**
- **Master Data**: Nama, lokasi, kontak, slot maksimal
- **Slot Tracking**: Monitor penggunaan vs kapasitas
- **Status Monitoring**: Real-time availability checking

### 📦 **Product Management**
- **Master Data**: Nama, harga, stok pusat
- **Commission System**: Persentase komisi per produk
- **Stock Control**: Auto-update dari distribusi dan penjualan

### 🚚 **Distribution System**
- **Smart Validation**: Cek slot availability sebelum distribusi
- **Auto Calculation**: Update stok pusat dan outlet otomatis
- **Tracking**: History lengkap semua distribusi

### 💰 **Sales & Billing**
- **Sales Recording**: Input penjualan dengan validasi stok
- **Auto Billing**: Kalkulasi tagihan dan komisi otomatis
- **Commission Tracking**: Monitor komisi per outlet/produk

### 💳 **Payment Management**
- **Payment Recording**: Input pembayaran dengan validasi
- **Balance Tracking**: Monitor saldo tagihan real-time
- **Invoice Generation**: PDF invoice professional

### 📊 **Advanced Reporting**
- **Dashboard Metrics**: KPI dan statistik real-time
- **Detailed Reports**: Filter by outlet, date range, product
- **PDF Export**: Professional invoice dan laporan
- **Analytics**: Slot usage, performance analysis

---

## 🔧 Konfigurasi

### Environment Variables
```bash
# Database Configuration
DATABASE_URL=postgresql://username:password@localhost:5432/sistem_distribusi

# Alternative individual settings
DB_HOST=localhost
DB_PORT=5432
DB_NAME=sistem_distribusi
DB_USER=your_username
DB_PASSWORD=your_password

# Flask Configuration
FLASK_ENV=development    # atau production
```

### Database Schema
Sistem menggunakan PostgreSQL dengan fitur-fitur berikut:
- **SERIAL PRIMARY KEY**: Auto-increment ID
- **Foreign Key Constraints**: Referential integrity
- **Indexes**: Optimized query performance
- **Transactions**: ACID compliance
- **Advanced Data Types**: DECIMAL, BOOLEAN, TIMESTAMP

### Database Tables
- `outlets` - Master data outlet
- `products` - Master data produk dengan komisi
- `distributions` - Tracking distribusi produk
- `sales` - Recording penjualan dengan sistem cicilan
- `payments` - Recording pembayaran outlet
- `users` - User management dengan role-based access

---

## 📊 Dashboard Preview

### Admin Dashboard
- 📊 Total distribusi dan penjualan
- 🏢 Status semua outlet (slot usage)
- 📦 Inventory produk real-time
- 📈 Metrics dan KPI

### Employee Dashboard
- 📊 Summary distribusi dan penjualan
- 📋 Recent transactions
- 🏢 Outlet dan produk overview
- 📊 Basic analytics

---

## 🔐 Security Features

- ✅ **Session-based Authentication**
- ✅ **Role-based Access Control**
- ✅ **Input Validation & Sanitization**
- ✅ **CSRF Protection Ready**
- ✅ **SQL Injection Prevention** (Parameterized queries)
- ✅ **Database Transactions** (ACID compliance)

---

## 🛠️ Tech Stack

| Technology | Purpose | Version |
|------------|---------|---------|
| **Flask** | Web Framework | 2.0+ |
| **Python** | Backend Language | 3.8+ |
| **PostgreSQL** | Database | 12+ |
| **psycopg2** | PostgreSQL Adapter | Latest |
| **Jinja2** | Template Engine | Built-in |
| **Bootstrap** | UI Framework | 5.0+ |
| **ReportLab** | PDF Generation | Latest |

---

## 📈 Performance Features

- ⚡ **Optimized Queries**: Efficient PostgreSQL operations
- 🔄 **Connection Pooling**: Efficient database connections
- 📱 **Responsive Design**: Mobile-friendly interface
- 🚀 **Fast Loading**: Optimized static assets
- 📊 **Database Indexes**: Optimized query performance
- 🔄 **Transaction Management**: Consistent data operations

---

## 🗄️ Database Features

### Advanced PostgreSQL Features
- **ACID Transactions**: Ensuring data consistency
- **Foreign Key Constraints**: Maintaining referential integrity
- **Indexes**: Optimized performance for large datasets
- **Advanced Data Types**: DECIMAL for financial calculations
- **Row Level Security**: Ready for multi-tenant setup
- **Backup & Recovery**: Built-in PostgreSQL features

### Business Logic Features
- **Installment Payment System**: Sistem cicilan pembayaran
- **Commission Calculation**: Kalkulasi komisi per produk
- **Stock Management**: Real-time inventory tracking
- **Slot Management**: Kapasitas outlet monitoring
- **Financial Reporting**: Comprehensive financial analytics

---

## 🚀 Deployment

### Production Setup
```bash
# Install production dependencies
pip install gunicorn

# Set production environment
export FLASK_ENV=production
export DATABASE_URL="postgresql://user:pass@prod-server:5432/sistem_distribusi"

# Run with Gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

### Docker Setup (Optional)
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python", "app.py"]
```

---

## 🤝 Contributing

1. Fork the project
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📝 License

Distributed under the MIT License. See `LICENSE` for more information.

---

## 📞 Support

Jika Anda memiliki pertanyaan atau membutuhkan bantuan:

- 📧 **Email**: support@example.com
- 💬 **Issues**: [GitHub Issues](https://github.com/jmsleo/distribusiKreasiX/issues)
- 📖 **Documentation**: [Wiki](https://github.com/jmsleo/distribusiKreasiX/wiki)

---

## 🎉 Acknowledgments

- Flask community untuk framework yang luar biasa
- PostgreSQL team untuk database yang powerful
- Bootstrap untuk UI components
- ReportLab untuk PDF generation
- psycopg2 untuk PostgreSQL connectivity

---

<div align="center">

**⭐ Jangan lupa berikan star jika project ini membantu! ⭐**

Made with ❤️ by KreasiX

</div>