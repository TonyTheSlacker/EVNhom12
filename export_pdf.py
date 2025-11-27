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
    with open(csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        for i, row in enumerate(reader):
            line = ' | '.join(row)
            pdf.cell(0, 10, txt=line, ln=True)
    pdf.output(pdf_path)

# Ví dụ sử dụng
if __name__ == "__main__":
    export_charging_stations_to_pdf("charging_stations.csv", "charging_stations.pdf")
