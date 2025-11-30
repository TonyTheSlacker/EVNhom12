from fpdf import FPDF
from datetime import datetime
import os
import pandas as pd
from typing import List, Tuple, Dict, Any
from math import radians, sin, cos, sqrt, atan2
import re

# CẤU HÌNH CHO BOT
R_EARTH = 6371.0 # Bán kính Trái Đất (km)
BOT_PROXIMITY_THRESHOLD = 5.0 # km - Nếu lộ trình đi qua trong vòng 5km của BOT, tính là đã đi qua

# --- HÀM TÍNH TOÁN KHOẢNG CÁCH ---
def haversine(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Tính khoảng cách Haversine (Đường chim bay) giữa hai điểm (km)"""
    lat1, lng1, lat2, lng2 = map(radians, [lat1, lng1, lat2, lng2])
    dlat = lat2 - lat1
    dlng = lng2 - lng1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlng/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    return R_EARTH * c

# --- HÀM XỬ LÝ BOT ---
def load_bot_stations(filename='BOT.csv') -> pd.DataFrame:
    """Tải và chuẩn hóa dữ liệu BOT station từ BOT.csv"""
    try:
        # Đọc dữ liệu từ file BOT.csv
        df = pd.read_csv(filename, skipinitialspace=True)
        # Đổi tên cột cho dễ xử lý (Giả định cột thứ 3 là tọa độ, cột thứ 4 là phí)
        df.columns = ['name', 'address', 'coords', 'fee']
        # Tách cột 'coords' thành 'lat' và 'lng'
        df[['lat', 'lng']] = df['coords'].str.split(',', expand=True).astype(float)
        # Loại bỏ các hàng không có tọa độ
        df = df[df['lat'].notnull() & df['lng'].notnull()]
        return df.reset_index(drop=True)
    except FileNotFoundError:
        print(f"Lỗi: Không tìm thấy file dữ liệu BOT: {filename}")
        return pd.DataFrame()

def check_bot_stations(route_points: List[Tuple[float, float]], df_bot: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    Kiểm tra các trạm BOT có thể đi qua trên lộ trình.
    route_points: Danh sách các tọa độ [(lat_start, lng_start), (lat_tram1, lng_tram1), ..., (lat_end, lng_end)]
    """
    if df_bot.empty:
        return []
        
    passed_bot_stations = {} # Dùng dict để tránh trùng lặp
    
    # Duyệt qua từng đoạn đường (A -> B)
    for i in range(len(route_points) - 1):
        lat_a, lng_a = route_points[i]
        lat_b, lng_b = route_points[i+1]
        
        for index, bot in df_bot.iterrows():
            bot_name = bot['name']
            bot_lat = bot['lat']
            bot_lng = bot['lng']
            
            # Kiểm tra xem BOT có nằm gần điểm đầu hoặc điểm cuối của đoạn đường hay không
            dist_a_to_bot = haversine(lat_a, lng_a, bot_lat, bot_lng)
            dist_b_to_bot = haversine(lat_b, lng_b, bot_lat, bot_lng)

            if dist_a_to_bot < BOT_PROXIMITY_THRESHOLD or dist_b_to_bot < BOT_PROXIMITY_THRESHOLD:
                if bot_name not in passed_bot_stations:
                    passed_bot_stations[bot_name] = {
                        'name': bot_name,
                        'address': bot['address'],
                        'fee': bot['fee'],
                        'lat': bot_lat,
                        'lng': bot_lng
                    }
                    
    return list(passed_bot_stations.values())

# --- HÀM XUẤT PDF ---
def clean_filename(s):
    """Làm sạch tên file để tránh lỗi hệ điều hành"""
    for ch in ':/\\*?"<>|[]':
        s = s.replace(ch, '-')
    return s

def export_route_to_pdf(model, pin, start_coords, end_coords, summary, details):
    """Xuất thông tin lộ trình ra file PDF"""
    now = datetime.now()
    date_str = now.strftime('%d-%m-%Y')
    time_str = now.strftime('%H-%M-%S') 
    
    start_station = start_coords
    end_station = end_coords
    
    # Cố gắng lấy tên trạm từ summary để đặt tên file
    for line in summary.split('\n'):
        if 'Xuất phát:' in line:
            start_station = line.split(':',1)[-1].strip()
            start_station = re.sub(r'\(Gần trạm .*\)', '', start_station).strip()
        if 'Kết thúc:' in line:
            end_station = line.split(':',1)[-1].strip()
            end_station = re.sub(r'\(Gần trạm .*\)', '', end_station).strip()

    if not start_station: start_station = 'unknown'
    if not end_station: end_station = 'unknown'

    # Format tên file
    filename = f"{date_str}-{time_str}-{clean_filename(model)}-{pin}-{clean_filename(start_station)}-{clean_filename(end_station)}.pdf"
    filename = filename.replace(' ', '').replace(',', '-')
    folder = os.path.join(os.path.dirname(__file__), 'routes')
    os.makedirs(folder, exist_ok=True)
    filepath = os.path.join(folder, filename)

    pdf = FPDF()
    pdf.add_page()
    # Sử dụng font hỗ trợ Unicode (Tiếng Việt)
    try:
        font_path = os.path.join(os.path.dirname(__file__), "Arial.ttf")
        # Thêm font thường
        pdf.add_font('ArialUnicode', '', font_path, uni=True)
        # Thêm font đậm (bold) nếu cần
        pdf.add_font('ArialUnicode', 'B', font_path, uni=True)
        font_name = 'ArialUnicode'
    except Exception as e:
        print(f"Lỗi khi thêm font: {e}")
        font_name = 'Arial' # Fallback

    pdf.set_font(font_name, '', 16)
    pdf.cell(0, 12, txt="KẾT QUẢ LỘ TRÌNH XE ĐIỆN", ln=True, align='C')
    pdf.ln(6)

    pdf.set_font(font_name, '', 12)
    # Ghi tóm tắt
    for line in summary.split('\n'):
        if line.strip():
            pdf.multi_cell(0, 8, txt=line, align='L')
    pdf.ln(5)

    # Ghi chi tiết
    pdf.set_font(font_name, 'B', 11)
    pdf.multi_cell(0, 8, txt="CHI TIẾT LỘ TRÌNH:", align='L')
    pdf.set_font(font_name, '', 10)

    # Xử lý chi tiết để ngắt dòng
    for line in details.split('\n'):
        if line.strip():
            pdf.multi_cell(0, 5, txt=line.strip(), align='L')

    pdf.output(filepath)
    print(f"Lộ trình đã được xuất ra: {filepath}")