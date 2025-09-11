from flask import Flask, render_template, request, redirect, url_for, flash, session, abort
from utils.data_helper import DataHelper
from datetime import datetime
from functools import wraps
import os
from config import config

app = Flask(__name__)

# Load configuration
config_name = os.environ.get('FLASK_ENV', 'development')
app.config.from_object(config[config_name])

data_helper = DataHelper()

# ---------------------------
# Decorators
# ---------------------------
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Silakan login terlebih dahulu', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Silakan login terlebih dahulu', 'danger')
            return redirect(url_for('login'))
        if session.get('role') != 'admin':
            flash('Akses ditolak. Hanya admin yang dapat mengakses fitur ini', 'danger')
            return redirect(url_for('karyawan_dashboard'))
        return f(*args, **kwargs)
    return decorated_function

# ---------------------------
# Template Filters
# ---------------------------
@app.template_filter('number_format')
def number_format(value):
    if value is None:
        return "0"
    try:
        return "{:,.0f}".format(float(value)).replace(",", ".")
    except:
        return str(value)

@app.template_filter('select')
def select_filter(sequence, attribute, value):
    if attribute == '>':
        return [item for item in sequence if item > value]
    elif attribute == '==':
        return [item for item in sequence if item == value]
    elif attribute == '>=':
        return [item for item in sequence if item >= value]
    elif attribute == '<':
        return [item for item in sequence if item < value]
    elif attribute == '<=':
        return [item for item in sequence if item <= value]
    return sequence

@app.template_filter('count')
def count_filter(sequence):
    return len(sequence)

@app.template_filter('selectattr')
def selectattr_filter(sequence, attribute, operator, value):
    """Filter untuk memilih item dari sequence berdasarkan attribute"""
    try:
        result = []
        for item in sequence:
            if hasattr(item, attribute):
                item_value = getattr(item, attribute)
            else:
                item_value = item.get(attribute)
            
            # Handle different operators
            if operator == 'equalto':
                if item_value == value:
                    result.append(item)
            elif operator == 'gt' or operator == '>':
                if item_value > value:
                    result.append(item)
            elif operator == 'lt' or operator == '<':
                if item_value < value:
                    result.append(item)
            elif operator == 'ge' or operator == '>=':
                if item_value >= value:
                    result.append(item)
            elif operator == 'le' or operator == '<=':
                if item_value <= value:
                    result.append(item)
            elif operator == 'ne' or operator == '!=':
                if item_value != value:
                    result.append(item)
        
        return result
    except Exception as e:
        print(f"Error in selectattr filter: {e}")
        return sequence

@app.context_processor
def inject_data_helper():
    return dict(data_helper=data_helper)

# ---------------------------
# Authentication Routes
# ---------------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        success, user_data = data_helper.authenticate_user(username, password)
        
        if success:
            session['user_id'] = user_data['id']
            session['username'] = user_data['username']
            session['role'] = user_data['role']
            
            flash('Login berhasil', 'success')
            
            # Redirect berdasarkan role
            if user_data['role'] == 'admin':
                return redirect(url_for('index'))
            else:
                return redirect(url_for('karyawan_dashboard'))
        else:
            flash('Username atau password salah', 'danger')
    
    return render_template('auth/login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logout berhasil', 'success')
    return redirect(url_for('login'))

# ---------------------------
# Main Dashboard
# ---------------------------
@app.route('/')
@login_required
def index():
    if session.get('role') == 'admin':
        try:
            outlets = data_helper.get_all_outlets()
            products = data_helper.get_all_products()
            
            # Convert to list of dicts for template compatibility
            outlets_list = [dict(outlet) for outlet in outlets] if outlets else []
            products_list = [dict(product) for product in products] if products else []
            
            # Calculate slot usage for each outlet
            for outlet in outlets_list:
                outlet_id = outlet['id']
                slot_used = data_helper.get_outlet_slot_info(outlet_id)
                outlet['slot_terpakai'] = slot_used
                outlet['slot_tersedia'] = outlet['slot_maksimal'] - slot_used
            
            # Get totals
            _, totals = data_helper.get_all_sales_report()
            
            return render_template('index.html', 
                                 outlets=outlets_list, 
                                 products=products_list,
                                 total_distribusi=totals['total_distribusi'],
                                 total_penjualan=totals['total_penjualan'])
        except Exception as e:
            flash(f'Error loading dashboard: {str(e)}', 'danger')
            return render_template('index.html', outlets=[], products=[], total_distribusi=0, total_penjualan=0)
    else:
        return redirect(url_for('karyawan_dashboard'))

@app.route('/karyawan/dashboard')
@login_required
def karyawan_dashboard():
    try:
        # Get totals
        _, totals = data_helper.get_all_sales_report()
        
        outlets = data_helper.get_all_outlets()
        products = data_helper.get_all_products()
        
        total_outlet = len(outlets) if outlets else 0
        total_produk = len(products) if products else 0
        
        # Get recent distributions and sales
        distributions = data_helper.get_all_distributions()
        sales = data_helper.get_all_sales()
        
        distribusi_terbaru = [dict(d) for d in distributions[:5]] if distributions else []
        penjualan_terbaru = [dict(s) for s in sales[:5]] if sales else []
        
        return render_template('karyawan/dashboard.html',
                             total_distribusi=totals['total_distribusi'],
                             total_penjualan=totals['total_penjualan'],
                             total_outlet=total_outlet,
                             total_produk=total_produk,
                             distribusi_terbaru=distribusi_terbaru,
                             penjualan_terbaru=penjualan_terbaru)
    except Exception as e:
        flash(f'Error loading dashboard: {str(e)}', 'danger')
        return render_template('karyawan/dashboard.html',
                             total_distribusi=0,
                             total_penjualan=0,
                             total_outlet=0,
                             total_produk=0,
                             distribusi_terbaru=[],
                             penjualan_terbaru=[])

# ---------------------------
# Outlet Routes
# ---------------------------
@app.route('/outlet')
@admin_required
def outlet_list():
    try:
        outlets = data_helper.get_all_outlets()
        outlets_list = [dict(outlet) for outlet in outlets] if outlets else []
        return render_template('outlet/list.html', outlets=outlets_list)
    except Exception as e:
        flash(f'Error loading outlets: {str(e)}', 'danger')
        return render_template('outlet/list.html', outlets=[])

@app.route('/outlet/add', methods=['GET', 'POST'])
@admin_required
def outlet_add():
    if request.method == 'POST':
        try:
            nama = request.form.get('nama')
            lokasi = request.form.get('lokasi')
            kontak = request.form.get('kontak')
            slot_maksimal = int(request.form.get('slot_maksimal', 0))
            
            outlet_id = data_helper.create_outlet(nama, lokasi, kontak, slot_maksimal)
            
            if outlet_id:
                flash('Outlet berhasil ditambahkan', 'success')
                return redirect(url_for('outlet_list'))
            else:
                flash('Gagal menambahkan outlet', 'danger')
        except Exception as e:
            flash(f'Error: {e}', 'danger')
    
    return render_template('outlet/add.html')

@app.route('/outlet/edit/<int:id>', methods=['GET', 'POST'])
@admin_required
def outlet_edit(id):
    try:
        outlet = data_helper.get_outlet_by_id(id)
        if not outlet:
            flash('Outlet tidak ditemukan', 'danger')
            return redirect(url_for('outlet_list'))
        
        outlet_dict = dict(outlet)
        
        if request.method == 'POST':
            nama = request.form.get('nama')
            lokasi = request.form.get('lokasi')
            kontak = request.form.get('kontak')
            slot_maksimal = int(request.form.get('slot_maksimal', 0))
            
            success = data_helper.update_outlet(id, nama, lokasi, kontak, slot_maksimal)
            
            if success:
                flash('Outlet berhasil diupdate', 'success')
                return redirect(url_for('outlet_list'))
            else:
                flash('Gagal mengupdate outlet', 'danger')
        
        return render_template('outlet/edit.html', outlet=outlet_dict)
    except Exception as e:
        flash(f'Error: {e}', 'danger')
        return redirect(url_for('outlet_list'))

@app.route('/outlet/delete/<int:id>')
@admin_required
def outlet_delete(id):
    try:
        success = data_helper.delete_outlet(id)
        if success:
            flash('Outlet berhasil dihapus', 'success')
        else:
            flash('Gagal menghapus outlet', 'danger')
    except Exception as e:
        flash(f'Error: {e}', 'danger')
    return redirect(url_for('outlet_list'))

# ---------------------------
# Product Routes (Updated with commission per product)
# ---------------------------
@app.route('/product')
@admin_required
def product_list():
    try:
        products = data_helper.get_all_products()
        products_list = [dict(product) for product in products] if products else []
        return render_template('product/list.html', products=products_list)
    except Exception as e:
        flash(f'Error loading products: {str(e)}', 'danger')
        return render_template('product/list.html', products=[])

@app.route('/product/add', methods=['GET', 'POST'])
@admin_required
def product_add():
    if request.method == 'POST':
        try:
            nama = request.form.get('nama')
            harga = float(request.form.get('harga', 0))
            stok_pusat = int(request.form.get('stok_pusat', 0))
            persentase_komisi = float(request.form.get('persentase_komisi', 0))
            
            product_id = data_helper.create_product(nama, harga, stok_pusat, persentase_komisi)
            
            if product_id:
                flash('Produk berhasil ditambahkan', 'success')
                return redirect(url_for('product_list'))
            else:
                flash('Gagal menambahkan produk', 'danger')
        except Exception as e:
            flash(f'Error: {e}', 'danger')
    
    return render_template('product/add.html')

@app.route('/product/edit/<int:id>', methods=['GET', 'POST'])
@admin_required
def product_edit(id):
    try:
        product = data_helper.get_product_by_id(id)
        if not product:
            flash('Produk tidak ditemukan', 'danger')
            return redirect(url_for('product_list'))
        
        product_dict = dict(product)
        
        if request.method == 'POST':
            nama = request.form.get('nama')
            harga = float(request.form.get('harga', 0))
            stok_pusat = int(request.form.get('stok_pusat', 0))
            persentase_komisi = float(request.form.get('persentase_komisi', 0))
            
            success = data_helper.update_product(id, nama, harga, stok_pusat, persentase_komisi)
            
            if success:
                flash('Produk berhasil diupdate', 'success')
                return redirect(url_for('product_list'))
            else:
                flash('Gagal mengupdate produk', 'danger')
        
        return render_template('product/edit.html', product=product_dict)
    except Exception as e:
        flash(f'Error: {e}', 'danger')
        return redirect(url_for('product_list'))

@app.route('/product/delete/<int:id>')
@admin_required
def product_delete(id):
    try:
        success = data_helper.delete_product(id)
        if success:
            flash('Produk berhasil dihapus', 'success')
        else:
            flash('Gagal menghapus produk', 'danger')
    except Exception as e:
        flash(f'Error: {e}', 'danger')
    return redirect(url_for('product_list'))

# ---------------------------
# Distribution Routes
# ---------------------------
@app.route('/distribution')
@login_required
def distribution_list():
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        outlet_id = request.args.get('outlet_id', type=int)
        
        distributions = data_helper.get_all_distributions(start_date, end_date, outlet_id)
        outlets = data_helper.get_all_outlets()
        
        distributions_list = [dict(d) for d in distributions] if distributions else []
        outlets_list = [dict(o) for o in outlets] if outlets else []
        
        return render_template('distribution/list.html', 
                             distributions=distributions_list,
                             outlets=outlets_list,
                             start_date=start_date or '',
                             end_date=end_date or '',
                             selected_outlet=outlet_id)
    except Exception as e:
        flash(f'Error loading distributions: {str(e)}', 'danger')
        return render_template('distribution/list.html', distributions=[], outlets=[])

@app.route('/distribution/add', methods=['GET', 'POST'])
@login_required
def distribution_add():
    try:
        outlets = data_helper.get_all_outlets()
        products = data_helper.get_all_products()
        
        outlets_list = [dict(o) for o in outlets] if outlets else []
        products_list = [dict(p) for p in products] if products else []
        
        if request.method == 'POST':
            outlet_id = int(request.form.get('outlet_id'))
            product_id = int(request.form.get('product_id'))
            jumlah = int(request.form.get('jumlah', 0))
            
            success, message = data_helper.create_distribution(outlet_id, product_id, jumlah)
            
            if success:
                flash(message, 'success')
                return redirect(url_for('distribution_list'))
            else:
                flash(message, 'danger')
        
        return render_template('distribution/add.html', outlets=outlets_list, products=products_list)
    except Exception as e:
        flash(f'Error: {e}', 'danger')
        return render_template('distribution/add.html', outlets=[], products=[])

# ---------------------------
# Sales Routes
# ---------------------------
@app.route('/sales')
@login_required
def sales_list():
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        outlet_id = request.args.get('outlet_id', type=int)
        
        sales = data_helper.get_all_sales(start_date, end_date, outlet_id)
        outlets = data_helper.get_all_outlets()
        
        sales_list = [dict(s) for s in sales] if sales else []
        outlets_list = [dict(o) for o in outlets] if outlets else []
        
        return render_template('sales/list.html', 
                             sales=sales_list,
                             outlets=outlets_list,
                             start_date=start_date or '',
                             end_date=end_date or '',
                             selected_outlet=outlet_id)
    except Exception as e:
        flash(f'Error loading sales: {str(e)}', 'danger')
        return render_template('sales/list.html', sales=[], outlets=[])

@app.route('/sales/add', methods=['GET', 'POST'])
@login_required
def sales_add():
    try:
        outlets = data_helper.get_all_outlets()
        products = data_helper.get_all_products()
        
        outlets_list = [dict(o) for o in outlets] if outlets else []
        products_list = [dict(p) for p in products] if products else []
        
        if request.method == 'POST':
            outlet_id = int(request.form.get('outlet_id'))
            product_id = int(request.form.get('product_id'))
            jumlah_terjual = int(request.form.get('jumlah_terjual', 0))
            
            success, message = data_helper.record_sale_with_bill(
                outlet_id, product_id, jumlah_terjual, 
                datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            )
            
            if success:
                flash(message, 'success')
                return redirect(url_for('sales_list'))
            else:
                flash(message, 'danger')
        
        return render_template('sales/add.html', outlets=outlets_list, products=products_list)
    except Exception as e:
        flash(f'Error: {e}', 'danger')
        return render_template('sales/add.html', outlets=[], products=[])

# ---------------------------
# Payment Routes
# ---------------------------
@app.route('/payment')
@admin_required
def payment_list():
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        outlet_id = request.args.get('outlet_id', type=int)
        
        payments = data_helper.get_all_payments(start_date, end_date, outlet_id)
        outlets = data_helper.get_all_outlets()
        
        payments_list = [dict(p) for p in payments] if payments else []
        outlets_list = [dict(o) for o in outlets] if outlets else []
        
        # Calculate outlet balances
        outlet_balances = {}
        outlets_dict = {}
        for outlet in outlets_list:
            outlet_id_key = outlet['id']
            outlet_balances[outlet_id_key] = data_helper.get_outlet_balance(outlet_id_key)
            outlets_dict[outlet_id_key] = outlet['nama']
        
        # Add balance info to payments
        for payment in payments_list:
            payment['total_tagihan'] = outlet_balances.get(payment['outlet_id'], 0)
        
        print("HASIL GET ALL OUTLETS:", outlets_list) 
        return render_template('payment/list.html', 
                             payments=payments_list,
                             outlet_balances=outlet_balances,
                             outlets_dict=outlets_dict,
                             outlets=outlets_list,
                             start_date=start_date or '',
                             end_date=end_date or '',
                             selected_outlet=outlet_id)
    except Exception as e:
        flash(f'Error loading payments: {str(e)}', 'danger')
        return render_template('payment/list.html', 
                             payments=[], 
                             outlet_balances={}, 
                             outlets_dict={},
                             outlets=[])

@app.route('/payment/add', methods=['GET', 'POST'])
@admin_required
def payment_add():
    try:
        outlets = data_helper.get_all_outlets()
        outlets_list = [dict(o) for o in outlets] if outlets else []
        
        selected_outlet = request.args.get('outlet_id', type=int)
        
        if request.method == 'POST':
            outlet_id = int(request.form.get('outlet_id'))
            amount = float(request.form.get('jumlah_bayar', 0))
            payment_date = request.form.get('tanggal_bayar')
            
            if amount <= 0:
                flash('Jumlah pembayaran harus lebih dari 0', 'danger')
                return render_template('payment/add.html', outlets=outlets_list, selected_outlet=selected_outlet)
            
            balance = data_helper.get_outlet_balance(outlet_id)
            
            if balance <= 0:
                flash('Outlet tidak memiliki tagihan', 'danger')
                return render_template('payment/add.html', outlets=outlets_list, selected_outlet=selected_outlet)
            
            if amount > balance:
                flash(f'Jumlah pembayaran melebihi tagihan. Tagihan outlet: Rp {balance:,.0f}', 'danger')
                return render_template('payment/add.html', outlets=outlets_list, selected_outlet=selected_outlet)
            
            success, message = data_helper.record_payment(outlet_id, amount, payment_date)
            
            if success:
                flash(message, 'success')
                return redirect(url_for('payment_list'))
            else:
                flash(message, 'danger')
        
        return render_template('payment/add.html', outlets=outlets_list, selected_outlet=selected_outlet)
    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')
        return render_template('payment/add.html', outlets=[], selected_outlet=None)

# ---------------------------
# Report Routes
# ---------------------------
@app.route('/report')
@admin_required
def report():
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        outlet_id = request.args.get('outlet_id', type=int)
        
        outlets = data_helper.get_all_outlets()
        outlets_list = [dict(o) for o in outlets] if outlets else []
        
        detailed_report, summary = data_helper.get_detailed_outlet_report(outlet_id, start_date, end_date)
        _, overall_totals = data_helper.get_all_sales_report(start_date, end_date)
        
        # Calculate outlet slot info
        outlet_slot_info = {}
        for outlet in outlets_list:
            distributed, sold, slot_used = data_helper.get_outlet_slot_usage(outlet['id'])
            outlet_slot_info[outlet['id']] = {
                'distributed': distributed,
                'sold': sold,
                'used': slot_used,
                'available': outlet['slot_maksimal'] - slot_used,
                'usage_percentage': (slot_used / outlet['slot_maksimal'] * 100) if outlet['slot_maksimal'] > 0 else 0
            }
        
        detailed_report_list = [dict(r) for r in detailed_report] if detailed_report else []
        
        return render_template('report/index.html',
                             detailed_report=detailed_report_list,
                             summary=summary,
                             outlets=outlets_list,
                             outlet_slot_info=outlet_slot_info,
                             overall_totals=overall_totals,
                             selected_outlet=outlet_id,
                             start_date=start_date or '',
                             end_date=end_date or '')
    except Exception as e:
        flash(f'Error generating report: {str(e)}', 'danger')
        return render_template('report/index.html',
                             detailed_report=[],
                             summary={},
                             outlets=[],
                             outlet_slot_info={},
                             overall_totals={
                                 'total_distribusi': 0,
                                 'total_penjualan': 0,
                                 'total_komisi': 0,
                                 'total_omzet_bersih': 0
                             },
                             selected_outlet=None,
                             start_date='',
                             end_date='')

# ---------------------------
# User Management Routes
# ---------------------------
@app.route('/user')
@admin_required
def user_list():
    try:
        users = data_helper.get_all_users()
        users_list = [dict(u) for u in users] if users else []
        return render_template('user/list.html', users=users_list)
    except Exception as e:
        flash(f'Error loading users: {str(e)}', 'danger')
        return render_template('user/list.html', users=[])

@app.route('/user/add', methods=['GET', 'POST'])
@admin_required
def user_add():
    if request.method == 'POST':
        try:
            username = request.form.get('username')
            password = request.form.get('password')
            role = request.form.get('role')
            
            user_id = data_helper.create_user(username, password, role)
            
            if user_id:
                flash('User berhasil ditambahkan', 'success')
                return redirect(url_for('user_list'))
            else:
                flash('Gagal menambahkan user', 'danger')
        except Exception as e:
            flash(f'Error: {e}', 'danger')
    
    return render_template('user/add.html')

@app.route('/user/edit/<int:id>', methods=['GET', 'POST'])
@admin_required
def user_edit(id):
    try:
        user = data_helper.get_user_by_id(id)
        if not user:
            flash('User tidak ditemukan', 'danger')
            return redirect(url_for('user_list'))
        
        if request.method == 'POST':
            username = request.form.get('username')
            role = request.form.get('role')
            new_password = request.form.get('password')
            
            success = data_helper.update_user(id, username, role, new_password if new_password else None)
            
            if success:
                flash('User berhasil diupdate', 'success')
                return redirect(url_for('user_list'))
            else:
                flash('Gagal mengupdate user', 'danger')
        
        return render_template('user/edit.html', user=user)
    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')
        return redirect(url_for('user_list'))

@app.route('/user/delete/<int:id>')
@admin_required
def user_delete(id):
    try:
        user = data_helper.get_user_by_id(id)
        if user and user['username'] == 'admin':
            flash('Tidak dapat menghapus user admin utama', 'danger')
            return redirect(url_for('user_list'))
        
        success = data_helper.delete_user(id)
        if success:
            flash('User berhasil dihapus', 'success')
        else:
            flash('Gagal menghapus user', 'danger')
    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')
    return redirect(url_for('user_list'))

# ---------------------------
# Run Application
# ---------------------------
if __name__ == '__main__':
   
    
    app.run(debug=app.config.get('DEBUG', False), host="0.0.0.0", port=5000)