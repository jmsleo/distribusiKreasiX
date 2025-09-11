import psycopg2
import psycopg2.extras
from datetime import datetime
import os
from config import Config

class DataHelper:
    def __init__(self):
        self.config = Config()
        self._connection = None
    
    def get_connection(self):
        """Get database connection"""
        if self._connection is None or self._connection.closed:
            try:
                if self.config.DATABASE_URL:
                    self._connection = psycopg2.connect(self.config.DATABASE_URL)
                else:
                    self._connection = psycopg2.connect(
                        host=self.config.DB_HOST,
                        port=self.config.DB_PORT,
                        database=self.config.DB_NAME,
                        user=self.config.DB_USER,
                        password=self.config.DB_PASSWORD
                    )
            except Exception as e:
                print(f"Database connection error: {e}")
                raise e
        return self._connection
    
    def init_database(self):
        """Initialize database tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Create outlets table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS outlets (
                    id SERIAL PRIMARY KEY,
                    nama VARCHAR(255) NOT NULL,
                    lokasi VARCHAR(255),
                    kontak VARCHAR(100),
                    slot_maksimal INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create products table (with commission per product)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS products (
                    id SERIAL PRIMARY KEY,
                    nama VARCHAR(255) NOT NULL,
                    harga DECIMAL(12,2) NOT NULL DEFAULT 0,
                    stok_pusat INTEGER DEFAULT 0,
                    persentase_komisi DECIMAL(5,2) DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create distributions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS distributions (
                    id SERIAL PRIMARY KEY,
                    outlet_id INTEGER REFERENCES outlets(id) ON DELETE CASCADE,
                    produk_id INTEGER REFERENCES products(id) ON DELETE CASCADE,
                    jumlah INTEGER NOT NULL DEFAULT 0,
                    tanggal TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create sales table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sales (
                    id SERIAL PRIMARY KEY,
                    outlet_id INTEGER REFERENCES outlets(id) ON DELETE CASCADE,
                    produk_id INTEGER REFERENCES products(id) ON DELETE CASCADE,
                    jumlah_terjual INTEGER NOT NULL DEFAULT 0,
                    tanggal TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    tagihan DECIMAL(12,2) DEFAULT 0,
                    komisi DECIMAL(12,2) DEFAULT 0,
                    yang_harus_dibayar DECIMAL(12,2) DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    username VARCHAR(100) UNIQUE NOT NULL,
                    password VARCHAR(255) NOT NULL,
                    role VARCHAR(50) NOT NULL DEFAULT 'karyawan',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create payments table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS payments (
                    id SERIAL PRIMARY KEY,
                    outlet_id INTEGER REFERENCES outlets(id) ON DELETE CASCADE,
                    jumlah_bayar DECIMAL(12,2) NOT NULL DEFAULT 0,
                    tanggal_bayar DATE NOT NULL,
                    tanggal_pelunasan DATE,
                    status VARCHAR(50) DEFAULT 'sebagian',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create indexes for better performance
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_distributions_outlet ON distributions(outlet_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_distributions_product ON distributions(produk_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_sales_outlet ON sales(outlet_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_sales_product ON sales(produk_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_payments_outlet ON payments(outlet_id)")
            
            # Insert default users if not exist
            cursor.execute("SELECT COUNT(*) FROM users WHERE username = 'admin'")
            if cursor.fetchone()[0] == 0:
                cursor.execute("""
                    INSERT INTO users (username, password, role) VALUES 
                    ('admin', 'admin123', 'admin'),
                    ('karyawan', 'karyawan123', 'karyawan')
                """)
            
            conn.commit()
            print("Database initialized successfully!")
            
        except Exception as e:
            conn.rollback()
            print(f"Error initializing database: {e}")
            raise e
        finally:
            cursor.close()
    
    def execute_query(self, query, params=None, fetch=False):
        """Execute a database query"""
        conn = self.get_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        try:
            cursor.execute(query, params)
            
            result = None
            if fetch:
                if fetch == 'one':
                    result = cursor.fetchone()
                else:
                    result = cursor.fetchall()
            
            conn.commit()  # ✅ selalu commit untuk INSERT/UPDATE/DELETE
            return result if fetch else cursor.rowcount
            
        except Exception as e:
            conn.rollback()
            print(f"Database query error: {e}")
            raise e
        finally:
            cursor.close()

    
    # User authentication methods
    def authenticate_user(self, username, password):
        """Authenticate user and return user data if successful"""
        try:
            query = "SELECT * FROM users WHERE username = %s AND password = %s"
            user = self.execute_query(query, (username, password), fetch='one')
            
            if user:
                return True, dict(user)
            else:
                return False, None
        except Exception as e:
            print(f"Authentication error: {e}")
            return False, None
    
    def get_user_by_id(self, user_id):
        """Get user data by ID"""
        try:
            query = "SELECT * FROM users WHERE id = %s"
            user = self.execute_query(query, (user_id,), fetch='one')
            return dict(user) if user else None
        except:
            return None
    
    # Outlet methods
    def get_all_outlets(self):
        """Get all outlets"""
        query = "SELECT * FROM outlets ORDER BY id"
        return self.execute_query(query, fetch='all')
    
    def get_outlet_by_id(self, outlet_id):
        """Get outlet by ID"""
        query = "SELECT * FROM outlets WHERE id = %s"
        return self.execute_query(query, (outlet_id,), fetch='one')
    
    def create_outlet(self, nama, lokasi, kontak, slot_maksimal):
        """Create new outlet"""
        query = """
            INSERT INTO outlets (nama, lokasi, kontak, slot_maksimal) 
            VALUES (%s, %s, %s, %s) RETURNING id
        """
        result = self.execute_query(query, (nama, lokasi, kontak, slot_maksimal), fetch='one')
        return result['id'] if result else None
    
    def update_outlet(self, outlet_id, nama, lokasi, kontak, slot_maksimal):
        """Update outlet"""
        query = """
            UPDATE outlets 
            SET nama = %s, lokasi = %s, kontak = %s, slot_maksimal = %s, updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
        """
        return self.execute_query(query, (nama, lokasi, kontak, slot_maksimal, outlet_id))
    
    def delete_outlet(self, outlet_id):
        """Delete outlet"""
        query = "DELETE FROM outlets WHERE id = %s"
        return self.execute_query(query, (outlet_id,))
    
    # Product methods (now with commission per product)
    def get_all_products(self):
        """Get all products"""
        query = "SELECT * FROM products ORDER BY id"
        return self.execute_query(query, fetch='all')
    
    def get_product_by_id(self, product_id):
        """Get product by ID"""
        query = "SELECT * FROM products WHERE id = %s"
        return self.execute_query(query, (product_id,), fetch='one')
    
    def create_product(self, nama, harga, stok_pusat, persentase_komisi):
        """Create new product"""
        query = """
            INSERT INTO products (nama, harga, stok_pusat, persentase_komisi) 
            VALUES (%s, %s, %s, %s) RETURNING id
        """
        result = self.execute_query(query, (nama, harga, stok_pusat, persentase_komisi), fetch='one')
        return result['id'] if result else None
    
    def update_product(self, product_id, nama, harga, stok_pusat, persentase_komisi):
        """Update product"""
        query = """
            UPDATE products 
            SET nama = %s, harga = %s, stok_pusat = %s, persentase_komisi = %s, updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
        """
        return self.execute_query(query, (nama, harga, stok_pusat, persentase_komisi, product_id))
    
    def delete_product(self, product_id):
        """Delete product"""
        query = "DELETE FROM products WHERE id = %s"
        return self.execute_query(query, (product_id,))
    
    def update_product_stock(self, product_id, quantity_change):
        """Update product stock"""
        query = "UPDATE products SET stok_pusat = stok_pusat + %s WHERE id = %s"
        return self.execute_query(query, (quantity_change, product_id))
    
    # Distribution methods
    def get_all_distributions(self, start_date=None, end_date=None, outlet_id=None):
        """Get all distributions with filters"""
        query = """
            SELECT d.*, o.nama as outlet_nama, p.nama as produk_nama
            FROM distributions d
            LEFT JOIN outlets o ON d.outlet_id = o.id
            LEFT JOIN products p ON d.produk_id = p.id
            WHERE 1=1
        """
        params = []
        
        if start_date and end_date:
            query += " AND DATE(d.tanggal) BETWEEN %s AND %s"
            params.extend([start_date, end_date])
        
        if outlet_id:
            query += " AND d.outlet_id = %s"
            params.append(outlet_id)
        
        query += " ORDER BY d.tanggal DESC"
        
        return self.execute_query(query, params, fetch='all')
    
    def create_distribution(self, outlet_id, produk_id, jumlah):
        """Create new distribution"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Check if product has enough stock
            cursor.execute("SELECT stok_pusat FROM products WHERE id = %s", (produk_id,))
            product = cursor.fetchone()
            
            if not product or product[0] < jumlah:
                return False, "Stok pusat tidak mencukupi"
            
            # Create distribution record
            cursor.execute("""
                INSERT INTO distributions (outlet_id, produk_id, jumlah) 
                VALUES (%s, %s, %s) RETURNING id
            """, (outlet_id, produk_id, jumlah))
            
            # Update product stock
            cursor.execute("""
                UPDATE products SET stok_pusat = stok_pusat - %s WHERE id = %s
            """, (jumlah, produk_id))
            
            conn.commit()
            return True, "Distribusi berhasil dicatat"
            
        except Exception as e:
            conn.rollback()
            return False, f"Error: {str(e)}"
        finally:
            cursor.close()
    
    # Sales methods
    def get_all_sales(self, start_date=None, end_date=None, outlet_id=None):
        """Get all sales with filters"""
        query = """
            SELECT s.*, o.nama as outlet_nama, p.nama as produk_nama
            FROM sales s
            LEFT JOIN outlets o ON s.outlet_id = o.id
            LEFT JOIN products p ON s.produk_id = p.id
            WHERE 1=1
        """
        params = []
        
        if start_date and end_date:
            query += " AND DATE(s.tanggal) BETWEEN %s AND %s"
            params.extend([start_date, end_date])
        
        if outlet_id:
            query += " AND s.outlet_id = %s"
            params.append(outlet_id)
        
        query += " ORDER BY s.tanggal DESC"
        
        return self.execute_query(query, params, fetch='all')
    
    def calculate_product_bill(self, product_id, quantity_sold):
        """Calculate bill based on product commission (not outlet)"""
        try:
            product = self.get_product_by_id(product_id)
            if not product:
                return 0, 0, 0
            
            product_price = float(product['harga'])
            commission_rate = float(product['persentase_komisi']) / 100
            
            tagihan = quantity_sold * product_price
            komisi = tagihan * commission_rate
            yang_harus_dibayar = tagihan - komisi
            
            return tagihan, komisi, yang_harus_dibayar
            
        except Exception as e:
            print(f"Error calculating bill: {e}")
            return 0, 0, 0
    
    def record_sale_with_bill(self, outlet_id, product_id, quantity_sold, sale_date):
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Calculate bill based on product commission
            tagihan, komisi, yang_harus_dibayar = self.calculate_product_bill(product_id, quantity_sold)
            
            if tagihan <= 0:
                return False, "Tidak dapat menghitung tagihan"
            
            # Check available stock at outlet
            available_stock = self.get_outlet_product_stock(outlet_id, product_id)
            if available_stock < quantity_sold:
                return False, f"Stok tidak mencukupi. Tersedia: {available_stock}"
            
            # Insert sale record
            query = """
                INSERT INTO sales (outlet_id, produk_id, jumlah_terjual, tanggal, tagihan, komisi, yang_harus_dibayar)
                VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id
            """
            cursor.execute(query, (outlet_id, product_id, quantity_sold, sale_date, tagihan, komisi, yang_harus_dibayar))
            result = cursor.fetchone()
            
            conn.commit()
            
            if result:
                return True, f"Penjualan berhasil dicatat. Tagihan: Rp {tagihan:,.0f}"
            else:
                return False, "Gagal mencatat penjualan"
                
        except Exception as e:
            conn.rollback()
            return False, f"Error: {str(e)}"
        finally:
            cursor.close()
    
    def get_outlet_product_stock(self, outlet_id, product_id):
        try:
            # Get total distributed
            query_dist = """
                SELECT COALESCE(SUM(jumlah), 0) as distributed 
                FROM distributions 
                WHERE outlet_id = %s AND produk_id = %s
            """
            dist_result = self.execute_query(query_dist, (outlet_id, product_id), fetch='one')
            distributed = float(dist_result['distributed']) if dist_result else 0
            
            # Get total sold
            query_sales = """
                SELECT COALESCE(SUM(jumlah_terjual), 0) as sold 
                FROM sales 
                WHERE outlet_id = %s AND produk_id = %s
            """
            sales_result = self.execute_query(query_sales, (outlet_id, product_id), fetch='one')
            sold = float(sales_result['sold']) if sales_result else 0
            
            return distributed - sold
            
        except Exception as e:
            print(f"Error getting outlet product stock: {e}")
            return 0
    
    def get_outlet_balance(self, outlet_id):
        """Get outlet balance (total amount to be paid)"""
        try:
            # Get total yang_harus_dibayar from sales
            query_sales = """
                SELECT COALESCE(SUM(yang_harus_dibayar), 0) as total_tagihan
                FROM sales 
                WHERE outlet_id = %s
            """
            sales_result = self.execute_query(query_sales, (outlet_id,), fetch='one')
            total_tagihan = float(sales_result['total_tagihan']) if sales_result and 'total_tagihan' in sales_result else 0
            
            # Get total payments
            query_payments = """
                SELECT COALESCE(SUM(jumlah_bayar), 0) as total_dibayar
                FROM payments 
                WHERE outlet_id = %s
            """
            payments_result = self.execute_query(query_payments, (outlet_id,), fetch='one')
            total_dibayar = float(payments_result['total_dibayar']) if payments_result and 'total_dibayar' in payments_result else 0
            
            return max(0, total_tagihan - total_dibayar)
            
        except Exception as e:
            print(f"Error calculating outlet balance: {e}")
            return 0

    def get_all_outlets(self):
        """Get all outlets"""
        try:
            query = "SELECT * FROM outlets ORDER BY id"
            result = self.execute_query(query, fetch='all')
            return result if result else []
        except Exception as e:
            print(f"Error getting outlets: {e}")
            return []
    
    def get_outlet_slot_info(self, outlet_id):
        """Get outlet slot usage information"""
        try:
            # Get total distributed
            query_dist = """
                SELECT COALESCE(SUM(jumlah), 0) as distributed 
                FROM distributions 
                WHERE outlet_id = %s
            """
            dist_result = self.execute_query(query_dist, (outlet_id,), fetch='one')
            distributed = float(dist_result['distributed']) if dist_result else 0
            
            # Get total sold
            query_sales = """
                SELECT COALESCE(SUM(jumlah_terjual), 0) as sold 
                FROM sales 
                WHERE outlet_id = %s
            """
            sales_result = self.execute_query(query_sales, (outlet_id,), fetch='one')
            sold = float(sales_result['sold']) if sales_result else 0
            
            return distributed - sold
            
        except Exception as e:
            print(f"Error getting outlet slot info: {e}")
            return 0
    
    # Payment methods
    def get_all_payments(self, start_date=None, end_date=None, outlet_id=None):
        """Get all payments with filters"""
        query = """
            SELECT p.*, o.nama as outlet_nama
            FROM payments p
            LEFT JOIN outlets o ON p.outlet_id = o.id
            WHERE 1=1
        """
        params = []
        
        if start_date and end_date:
            query += " AND p.tanggal_bayar >= %s AND p.tanggal_bayar <= %s"
            params.extend([start_date, end_date])
        
        if outlet_id:
            query += " AND p.outlet_id = %s"
            params.append(outlet_id)
        
        query += " ORDER BY p.tanggal_bayar DESC"
        
        return self.execute_query(query, params, fetch='all')
    
    def record_payment(self, outlet_id, amount, payment_date):
        try:
            total_tagihan = self.get_outlet_balance(outlet_id)
            print("DEBUG total_tagihan:", total_tagihan)  # debug

            if total_tagihan <= 0:
                return False, "Outlet tidak memiliki tagihan"
            
            if amount <= 0:
                return False, "Jumlah pembayaran harus lebih dari 0"
            
            if amount > total_tagihan:
                return False, f"Jumlah pembayaran ({amount:,.0f}) melebihi total tagihan ({total_tagihan:,.0f})"
            
            # Determine status
            if amount >= total_tagihan:
                status = "lunas"
                tanggal_pelunasan = payment_date
            else:
                status = "sebagian"
                tanggal_pelunasan = None
            
            query = """
                INSERT INTO payments (outlet_id, jumlah_bayar, tanggal_bayar, tanggal_pelunasan, status)
                VALUES (%s, %s, %s, %s, %s) RETURNING id
            """
            print("DEBUG query params:", outlet_id, amount, payment_date, tanggal_pelunasan, status)  # debug
            
            result = self.execute_query(query, (outlet_id, amount, payment_date, tanggal_pelunasan, status), fetch='one')
            print("DEBUG result:", result)  # debug
            
            if result:
                return True, "Pembayaran berhasil dicatat"
            else:
                return False, "Gagal mencatat pembayaran"
                    
        except Exception as e:
            import traceback; print(traceback.format_exc())
            return False, f"Error: {str(e)}"

    
    # Report methods
    def get_detailed_outlet_report(self, outlet_id=None, start_date=None, end_date=None):
        """Get detailed outlet report"""
        try:
            query = """
                SELECT 
                    s.tanggal,
                    s.outlet_id,
                    o.nama as outlet_nama,
                    s.produk_id,
                    p.nama as produk_nama,
                    s.jumlah_terjual,
                    p.harga,
                    s.tagihan,
                    s.komisi,
                    s.yang_harus_dibayar,
                    COALESCE(d.total_distribusi, 0) as distribusi,
                    COALESCE(d.total_distribusi, 0) - COALESCE(sold.total_sold, 0) as sisa
                FROM sales s
                LEFT JOIN outlets o ON s.outlet_id = o.id
                LEFT JOIN products p ON s.produk_id = p.id
                LEFT JOIN (
                    SELECT produk_id, outlet_id, SUM(jumlah) as total_distribusi
                    FROM distributions
                    GROUP BY produk_id, outlet_id
                ) d ON s.produk_id = d.produk_id AND s.outlet_id = d.outlet_id
                LEFT JOIN (
                    SELECT produk_id, outlet_id, SUM(jumlah_terjual) as total_sold
                    FROM sales
                    GROUP BY produk_id, outlet_id
                ) sold ON s.produk_id = sold.produk_id AND s.outlet_id = sold.outlet_id
                WHERE 1=1
            """
            params = []
            
            if start_date and end_date:
                query += " AND s.tanggal >= %s AND s.tanggal <= %s"
                params.extend([start_date, end_date])
            
            if outlet_id:
                query += " AND s.outlet_id = %s"
                params.append(outlet_id)
            
            query += " ORDER BY s.tanggal DESC"
            
            detailed_report = self.execute_query(query, params, fetch='all')
            
            # Calculate summary
            if detailed_report:
                summary = {
                    'total_terjual': sum(float(row['jumlah_terjual']) for row in detailed_report),
                    'total_tagihan': sum(float(row['tagihan']) for row in detailed_report),
                    'total_komisi': sum(float(row['komisi']) for row in detailed_report),
                    'total_dibayar': sum(float(row['yang_harus_dibayar']) for row in detailed_report),
                    'total_distribusi': sum(float(row['distribusi']) for row in detailed_report)
                }
            else:
                summary = {
                    'total_terjual': 0,
                    'total_tagihan': 0,
                    'total_komisi': 0,
                    'total_dibayar': 0,
                    'total_distribusi': 0
                }
            
            return detailed_report, summary
            
        except Exception as e:
            print(f"Error in get_detailed_outlet_report: {e}")
            return [], {}
    
    def get_all_sales_report(self, start_date=None, end_date=None):
        """Get overall sales report"""
        try:
            # Get distributions total
            dist_query = "SELECT COALESCE(SUM(jumlah), 0) as total_distribusi FROM distributions"
            dist_params = []
            
            if start_date and end_date:
                dist_query += " WHERE tanggal >= %s AND tanggal <= %s"
                dist_params.extend([start_date, end_date])
            
            dist_result = self.execute_query(dist_query, dist_params, fetch='one')
            total_distribusi = float(dist_result['total_distribusi']) if dist_result else 0
            
            # Get sales totals
            sales_query = """
                SELECT 
                    COALESCE(SUM(jumlah_terjual), 0) as total_penjualan,
                    COALESCE(SUM(komisi), 0) as total_komisi,
                    COALESCE(SUM(yang_harus_dibayar), 0) as total_omzet_bersih
                FROM sales
            """
            sales_params = []
            
            if start_date and end_date:
                sales_query += " WHERE tanggal >= %s AND tanggal <= %s"
                sales_params.extend([start_date, end_date])
            
            sales_result = self.execute_query(sales_query, sales_params, fetch='one')
            
            overall_totals = {
                'total_distribusi': total_distribusi,
                'total_penjualan': float(sales_result['total_penjualan']) if sales_result else 0,
                'total_komisi': float(sales_result['total_komisi']) if sales_result else 0,
                'total_omzet_bersih': float(sales_result['total_omzet_bersih']) if sales_result else 0
            }
            
            return [], overall_totals
            
        except Exception as e:
            print(f"Error in get_all_sales_report: {e}")
            return [], {
                'total_distribusi': 0,
                'total_penjualan': 0,
                'total_komisi': 0,
                'total_omzet_bersih': 0
            }
    
    def get_outlet_slot_usage(self, outlet_id):
        """Get outlet slot usage details"""
        try:
            # Get total distributed
            query_dist = """
                SELECT COALESCE(SUM(jumlah), 0) as distributed 
                FROM distributions 
                WHERE outlet_id = %s
            """
            dist_result = self.execute_query(query_dist, (outlet_id,), fetch='one')
            distributed = float(dist_result['distributed']) if dist_result else 0
            
            # Get total sold
            query_sales = """
                SELECT COALESCE(SUM(jumlah_terjual), 0) as sold 
                FROM sales 
                WHERE outlet_id = %s
            """
            sales_result = self.execute_query(query_sales, (outlet_id,), fetch='one')
            sold = float(sales_result['sold']) if sales_result else 0
            
            slot_used = distributed - sold
            
            return distributed, sold, slot_used
            
        except Exception as e:
            print(f"Error getting outlet slot usage: {e}")
            return 0, 0, 0
    
    # User management methods
    def get_all_users(self):
        """Get all users"""
        query = "SELECT * FROM users ORDER BY id"
        return self.execute_query(query, fetch='all')
    
    def create_user(self, username, password, role):
        """Create new user"""
        query = """
            INSERT INTO users (username, password, role) 
            VALUES (%s, %s, %s) RETURNING id
        """
        result = self.execute_query(query, (username, password, role), fetch='one')
        return result['id'] if result else None
    
    def update_user(self, user_id, username, role, password=None):
        """Update user"""
        if password:
            query = """
                UPDATE users 
                SET username = %s, role = %s, password = %s, updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
            """
            return self.execute_query(query, (username, role, password, user_id))
        else:
            query = """
                UPDATE users 
                SET username = %s, role = %s, updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
            """
            return self.execute_query(query, (username, role, user_id))
    
    def delete_user(self, user_id):
        """Delete user"""
        query = "DELETE FROM users WHERE id = %s"
        return self.execute_query(query, (user_id,))
    
    def close_connection(self):
        """Close database connection"""
        if self._connection and not self._connection.closed:
            self._connection.close()