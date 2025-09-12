# Fitur Ekspor Invoice PDF

## Deskripsi
Fitur ini memungkinkan ekspor invoice tagihan outlet ke dalam format PDF dengan desain yang menarik dan profesional.

## Fitur yang Ditambahkan

### 1. Generator PDF Invoice (`utils/pdf_generator.py`)
- Membuat invoice PDF dengan format kertas HVS normal (A4)
- Desain yang senada dengan tema web
- Kop surat "Yobels Salatiga" dengan informasi kontak lengkap:
  - Instagram: @abonyobels
  - WhatsApp: +62 821-3855-8731
  - Tokopedia: Abon Yobels
  - Shopee: Abon Yobels

### 2. Route Baru di Flask App
- `/invoice/preview/<outlet_id>` - Preview invoice sebelum download
- `/invoice/export/<outlet_id>` - Download PDF invoice

### 3. Template Preview Invoice
- `templates/invoice/preview.html` - Halaman preview invoice
- Desain responsif dengan styling yang menarik
- Fungsi print untuk cetak langsung

### 4. Integrasi dengan Payment List
- Tombol "Preview" dan "PDF" pada setiap outlet yang memiliki tagihan
- Filter berdasarkan tanggal untuk periode tertentu

## Cara Penggunaan

1. **Melalui Halaman Pembayaran:**
   - Buka menu "Pembayaran"
   - Pada tabel "Ringkasan Tagihan Outlet", klik tombol:
     - "Preview" untuk melihat preview invoice
     - "PDF" untuk langsung download PDF

2. **Filter Periode:**
   - Gunakan filter tanggal untuk membuat invoice periode tertentu
   - Kosongkan filter untuk semua periode

3. **Preview Invoice:**
   - Klik "Preview" untuk melihat tampilan invoice
   - Dari halaman preview, bisa langsung download PDF
   - Bisa juga print langsung dengan Ctrl+P

## Format Invoice

### Header
- Logo/Nama: "Yobels Salatiga"
- Informasi kontak lengkap
- Nomor invoice otomatis: INV-YYYYMMDD-NNNN

### Detail Invoice
- Informasi outlet (nama, lokasi, kontak)
- Tabel rincian penjualan per produk
- Kolom: No, Tanggal, Produk, Qty, Harga Satuan, Total, Komisi, Tagihan

### Ringkasan
- Total penjualan
- Total komisi
- **Total yang harus dibayar** (highlighted)

### Footer
- Ucapan terima kasih
- Timestamp pembuatan
- Informasi kontak untuk pertanyaan

## Dependencies Baru
- `reportlab` - Library untuk generate PDF

## File yang Dimodifikasi
1. `app.py` - Menambah route dan import PDF generator
2. `templates/payment/list.html` - Menambah tombol export
3. `utils/pdf_generator.py` - File baru untuk generate PDF
4. `templates/invoice/preview.html` - Template preview baru

## Styling dan Desain
- Warna tema: #2c5aa0 (biru profesional)
- Font: Helvetica untuk keterbacaan optimal
- Layout responsif dan print-friendly
- Tabel dengan styling yang jelas dan mudah dibaca

## Error Handling
- Validasi outlet exists
- Validasi data penjualan tersedia
- Error message yang informatif
- Fallback untuk data yang tidak lengkap

Fitur ini memberikan kemudahan bagi admin untuk membuat dan mengirim invoice profesional kepada outlet-outlet yang memiliki tagihan.