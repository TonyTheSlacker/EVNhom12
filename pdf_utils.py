
from fpdf import FPDF
from datetime import datetime
import os

def export_route_to_pdf(model, pin, start_coords, end_coords, summary, details):
    now = datetime.now()
    date_str = now.strftime('%d-%m-%Y')
    time_str = now.strftime('%H-%M-%S')  # Dùng dấu gạch ngang thay cho dấu hai chấm
    # Lấy tên trạm bắt đầu/kết thúc từ summary
    start_station = ''
    end_station = ''
    for line in summary.split('\n'):
        if 'Bắt đầu:' in line:
            start_station = line.split(':',1)[-1].strip()
        if 'Kết thúc:' in line:
            end_station = line.split(':',1)[-1].strip()
    # Nếu trạm bắt đầu/kết thúc trống thì thay bằng 'unknown'
    if not start_station:
        start_station = 'unknown'
    if not end_station:
        end_station = 'unknown'
    # Format tên file, loại bỏ ký tự đặc biệt không hợp lệ cho Windows
    def clean_filename(s):
        for ch in ':/\\*?"<>|[]':
            s = s.replace(ch, '-')
        return s
    filename = f"{date_str}-{time_str}-{clean_filename(model)}-{pin}-{clean_filename(start_station)}-{clean_filename(end_station)}.pdf"
    filename = filename.replace(' ', '').replace(',', '-')
    folder = os.path.join(os.path.dirname(__file__), 'routes')
    os.makedirs(folder, exist_ok=True)
    filepath = os.path.join(folder, filename)

    pdf = FPDF()
    pdf.add_page()
    font_path = os.path.join(os.path.dirname(__file__), "Arial.ttf")
    pdf.add_font('ArialUnicode', '', font_path, uni=True)
    pdf.set_font("ArialUnicode", size=16)
    pdf.cell(0, 12, txt="KẾT QUẢ LỘ TRÌNH XE ĐIỆN", ln=True, align='C')
    pdf.ln(6)
    pdf.set_font("ArialUnicode", size=12)
    pdf.cell(0, 10, txt=f"Ngày xuất: {date_str} - {time_str}", ln=True)
    pdf.cell(0, 10, txt=f"Mẫu xe: {model} | % Pin: {pin}", ln=True)
    pdf.cell(0, 10, txt=f"Trạm bắt đầu: {start_station}", ln=True)
    pdf.cell(0, 10, txt=f"Trạm kết thúc: {end_station}", ln=True)
    pdf.ln(4)
    pdf.set_font("ArialUnicode", size=12)
    pdf.cell(0, 10, txt="--- TÓM TẮT LỘ TRÌNH ---", ln=True)
    pdf.set_font("ArialUnicode", size=11)
    for line in summary.split('\n'):
        pdf.multi_cell(0, 8, txt=line)
    pdf.ln(4)
    pdf.set_font("ArialUnicode", size=12)
    pdf.cell(0, 10, txt="--- CHI TIẾT LỘ TRÌNH ---", ln=True)
    pdf.set_font("ArialUnicode", size=10)
    for line in details.split('\n'):
        pdf.multi_cell(0, 7, txt=line)
    pdf.output(filepath)
    return filepath
