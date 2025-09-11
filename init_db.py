from utils.data_helper import DataHelper
import sys

def init_database():
    try:
        helper = DataHelper()
        helper.init_database()
        print("PostgreSQL database telah diinisialisasi!")
        print("Default admin login: username=admin, password=admin123")
        print("Default karyawan login: username=karyawan, password=karyawan123")
        print("\nPastikan PostgreSQL sudah berjalan dan database 'distribusi_produk' sudah dibuat.")
        print("Untuk membuat database: CREATE DATABASE distribusi_produk;")
    except Exception as e:
        print(f"Error initializing database: {e}")
        print("Pastikan:")
        print("1. PostgreSQL sudah terinstall dan berjalan")
        print("2. Database 'distribusi_produk' sudah dibuat")
        print("3. Kredensial database di .env sudah benar")
        sys.exit(1)

if __name__ == "__main__":
    init_database()