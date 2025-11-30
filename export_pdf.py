from fpdf import FPDF
import csv

# Hàm xuất danh sách trạm sạc ra file PDF
# Đọc dữ liệu từ charging_stations.csv và ghi ra file PDF

def export_charging_stations_to_pdf(csv_path, pdf_path):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Danh sách trạm sạc", ln=True, align='C')
    pdf.ln(10)

    # Đọc dữ liệu từ CSV và ghi vào PDF
    try:
        with open(csv_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            for i, row in enumerate(reader):
                # Format dòng dữ liệu
                line = ' | '.join(row)
                pdf.cell(0, 10, txt=line, ln=True)
        
        pdf.output(pdf_path)
        print(f"Danh sách trạm sạc đã được xuất ra: {pdf_path}")
    except FileNotFoundError:
        print(f"Lỗi: Không tìm thấy file dữ liệu: {csv_path}")
    except Exception as e:
        print(f"Lỗi khi xuất PDF: {e}")

# Ví dụ sử dụng
if __name__ == "__main__":
    # Lưu ý: Cần có file 'charging_stations.csv' trong cùng thư mục để chạy
    export_charging_stations_to_pdf("charging_stations.csv", "charging_stations.pdf")