from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import datetime
import os
from io import BytesIO

class InvoicePDFGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()
    
    def setup_custom_styles(self):
        """Setup custom styles for the invoice"""
        # Company header style
        self.company_style = ParagraphStyle(
            'CompanyStyle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#2c5aa0'),
            alignment=TA_CENTER,
            spaceAfter=6,
            fontName='Helvetica-Bold'
        )
        
        # Contact info style
        self.contact_style = ParagraphStyle(
            'ContactStyle',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#666666'),
            alignment=TA_CENTER,
            spaceAfter=20
        )
        
        # Invoice title style
        self.invoice_title_style = ParagraphStyle(
            'InvoiceTitle',
            parent=self.styles['Heading2'],
            fontSize=18,
            textColor=colors.HexColor('#2c5aa0'),
            alignment=TA_CENTER,
            spaceAfter=20,
            fontName='Helvetica-Bold'
        )
        
        # Section header style
        self.section_header_style = ParagraphStyle(
            'SectionHeader',
            parent=self.styles['Heading3'],
            fontSize=12,
            textColor=colors.HexColor('#2c5aa0'),
            spaceAfter=10,
            fontName='Helvetica-Bold'
        )
        
        # Normal text style
        self.normal_style = ParagraphStyle(
            'NormalText',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.black,
            spaceAfter=6
        )
    
    def format_currency(self, amount):
        """Format currency in Indonesian Rupiah"""
        try:
            return f"Rp {float(amount):,.0f}".replace(",", ".")
        except:
            return "Rp 0"
    
    def generate_invoice(self, outlet_data, sales_data, invoice_number=None, invoice_date=None):
        """Generate PDF invoice for an outlet"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=20*mm,
            leftMargin=20*mm,
            topMargin=20*mm,
            bottomMargin=20*mm
        )
        
        # Story elements
        story = []
        
        # Company header
        company_name = Paragraph("Yobels Salatiga", self.company_style)
        story.append(company_name)
        
        # Contact information
        contact_info = """
        Instagram: @abonyobels | WhatsApp: +62 821-3855-8731<br/>
        Tokopedia: Abon Yobels | Shopee: Abon Yobels
        """
        contact_para = Paragraph(contact_info, self.contact_style)
        story.append(contact_para)
        
        # Divider line
        story.append(Spacer(1, 10))
        
        # Invoice title
        invoice_title = Paragraph("INVOICE TAGIHAN BELUM DIBAYAR", self.invoice_title_style)
        story.append(invoice_title)
        
        # Invoice details
        if not invoice_number:
            invoice_number = f"INV-{datetime.now().strftime('%Y%m%d')}-{outlet_data['id']:04d}"
        
        if not invoice_date:
            invoice_date = datetime.now().strftime('%d %B %Y')
        
        invoice_details_data = [
            ['No. Invoice:', invoice_number],
            ['Tanggal:', invoice_date],
            ['Outlet:', outlet_data['nama']],
            ['Lokasi:', outlet_data.get('lokasi', '-')],
            ['Kontak:', outlet_data.get('kontak', '-')]
        ]
        
        invoice_details_table = Table(invoice_details_data, colWidths=[40*mm, 120*mm])
        invoice_details_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#2c5aa0')),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ]))
        
        story.append(invoice_details_table)
        story.append(Spacer(1, 20))
        
        # Check if there are unpaid sales
        if not sales_data:
            no_data_msg = Paragraph(
                "TIDAK ADA TAGIHAN YANG BELUM DIBAYAR", 
                self.section_header_style
            )
            story.append(no_data_msg)
            
            paid_msg = Paragraph(
                "Semua tagihan untuk outlet ini sudah lunas. Terima kasih!", 
                self.normal_style
            )
            story.append(paid_msg)
        else:
            # Sales items table
            sales_header = Paragraph("RINCIAN PENJUALAN BELUM DIBAYAR", self.section_header_style)
            story.append(sales_header)
            
            # Prepare sales data for table
            table_data = [
                ['No.', 'Tanggal', 'Produk', 'Qty', 'Harga Satuan', 'Total', 'Komisi', 'Tagihan']
            ]
            
            total_qty = 0
            total_amount = 0
            total_commission = 0
            total_bill = 0
            
            for idx, sale in enumerate(sales_data, 1):
                qty = int(sale.get('jumlah_terjual', 0))
                price = float(sale.get('harga', 0))
                total = float(sale.get('tagihan', 0))
                commission = float(sale.get('komisi', 0))
                bill = float(sale.get('yang_harus_dibayar', 0))
                
                total_qty += qty
                total_amount += total
                total_commission += commission
                total_bill += bill
                
                table_data.append([
                    str(idx),
                    datetime.strptime(str(sale['tanggal']), '%Y-%m-%d %H:%M:%S').strftime('%d/%m/%Y') if sale.get('tanggal') else '-',
                    sale.get('produk_nama', '-'),
                    str(qty),
                    self.format_currency(price),
                    self.format_currency(total),
                    self.format_currency(commission),
                    self.format_currency(bill)
                ])
            
            # Add totals row
            table_data.append([
                '', '', 'TOTAL', str(total_qty), '',
                self.format_currency(total_amount),
                self.format_currency(total_commission),
                self.format_currency(total_bill)
            ])
            
            # Create table
            sales_table = Table(table_data, colWidths=[15*mm, 25*mm, 45*mm, 20*mm, 25*mm, 25*mm, 25*mm, 25*mm])
            
            # Table styling
            sales_table.setStyle(TableStyle([
                # Header row
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5aa0')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                
                # Data rows
                ('FONTNAME', (0, 1), (-1, -2), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -2), 8),
                ('ALIGN', (0, 1), (0, -2), 'CENTER'),  # No. column
                ('ALIGN', (1, 1), (1, -2), 'CENTER'),  # Date column
                ('ALIGN', (3, 1), (-1, -2), 'RIGHT'),  # Numeric columns
                
                # Total row
                ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#f0f0f0')),
                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, -1), (-1, -1), 9),
                ('ALIGN', (0, -1), (2, -1), 'CENTER'),
                ('ALIGN', (3, -1), (-1, -1), 'RIGHT'),
                
                # Grid
                ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                
                # Padding
                ('LEFTPADDING', (0, 0), (-1, -1), 3),
                ('RIGHTPADDING', (0, 0), (-1, -1), 3),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ]))
            
            story.append(sales_table)
            story.append(Spacer(1, 20))
            
            # Summary section
            summary_header = Paragraph("RINGKASAN TAGIHAN", self.section_header_style)
            story.append(summary_header)
            
            summary_data = [
                ['Total Penjualan:', self.format_currency(total_amount)],
                ['Total Komisi:', self.format_currency(total_commission)],
                ['', ''],
                ['TOTAL YANG HARUS DIBAYAR:', self.format_currency(total_bill)]
            ]
            
            summary_table = Table(summary_data, colWidths=[80*mm, 50*mm])
            summary_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, -2), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -2), 11),
                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, -1), (-1, -1), 14),
                ('TEXTCOLOR', (0, -1), (-1, -1), colors.HexColor('#2c5aa0')),
                ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
                ('TOPPADDING', (0, 0), (-1, -1), 5),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                ('LINEBELOW', (0, -1), (-1, -1), 2, colors.HexColor('#2c5aa0')),
            ]))
            
            story.append(summary_table)
        
        story.append(Spacer(1, 30))
        
        # Footer
        footer_text = """
        <para align="center">
        <font size="8" color="#666666">
        Terima kasih atas kerjasama Anda!<br/>
        Invoice ini dibuat secara otomatis pada {}<br/>
        Untuk pertanyaan, silakan hubungi kontak di atas.
        </font>
        </para>
        """.format(datetime.now().strftime('%d %B %Y %H:%M:%S'))
        
        footer_para = Paragraph(footer_text, self.normal_style)
        story.append(footer_para)
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer
    
    def generate_outlet_invoice(self, data_helper, outlet_id, start_date=None, end_date=None):
        """Generate invoice for a specific outlet - HANYA SALES YANG BELUM DIBAYAR"""
        try:
            # Get outlet data
            outlet = data_helper.get_outlet_by_id(outlet_id)
            if not outlet:
                raise ValueError("Outlet tidak ditemukan")
            
            outlet_dict = dict(outlet)
            
            # Get UNPAID sales data for the outlet - INI YANG PENTING!
            unpaid_sales_data = data_helper.get_unpaid_sales(start_date, end_date, outlet_id)
            
            # Convert to list of dicts
            sales_list = [dict(sale) for sale in unpaid_sales_data] if unpaid_sales_data else []
            
            # Generate PDF
            pdf_buffer = self.generate_invoice(outlet_dict, sales_list)
            
            # Create filename
            status = "LUNAS" if not sales_list else "BELUM_LUNAS"
            filename = f"Invoice_{outlet_dict['nama'].replace(' ', '_')}_{status}_{datetime.now().strftime('%Y%m%d')}.pdf"
            
            return pdf_buffer, filename
            
        except Exception as e:
            raise Exception(f"Error generating invoice: {str(e)}")