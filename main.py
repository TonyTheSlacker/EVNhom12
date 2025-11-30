import tkinter as tk
from tkinter import messagebox, scrolledtext
import pandas as pd
from typing import Optional
import numpy as np
import heapq
import time
from math import radians, sin, cos, sqrt, atan2
from typing import List, Tuple, Dict, Any
import re 
import folium # Import thư viện bản đồ
import webbrowser # Import để mở bản đồ HTML trong trình duyệt
import os # Dùng để tạo file tạm
from models import ElectricCar, cars

# --- CÁC HÀM TỪ file.py (ĐƯỢC ĐỊNH NGHĨA LẠI HOẶC IMPORT) ---
TIMEOUT_SECONDS = 120 
AVG_SPEED_KMH = 100 
R_EARTH = 6371.0
ROAD_FACTOR = 1.25

def haversine(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    # Sao chép từ file.py
    lat1, lng1, lat2, lng2 = map(radians, [lat1, lng1, lat2, lng2])
    dlat = lat2 - lat1
    dlng = lng2 - lng1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlng/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    return R_EARTH * c

def find_nearest_node(lat: float, lng: float, df_charge: pd.DataFrame) -> str:
    # Sao chép từ file.py
    df = df_charge.copy()
    df = df[df['lat'].notnull() & df['lng'].notnull()]
    df['dist'] = ((df['lat'].astype(float) - lat)**2 + (df['lng'].astype(float) - lng)**2).apply(np.sqrt)
    if df.empty: return 'unknown'
    nearest = df.loc[df['dist'].idxmin()]
    return nearest['name'] if 'name' in nearest else 'unknown'

# Import run_astar_search (Giả định từ file.py)
from file import astar_charging_stations, run_astar_search

# Import các hàm BOT/PDF (Giả định từ pdf_utils.py)
try:
    from pdf_utils import export_route_to_pdf, check_bot_stations, load_bot_stations
except ImportError:
    # Fallback nếu không import được
    def export_route_to_pdf(model, pin, start_coords, end_coords, summary, details):
        messagebox.showerror("Lỗi", "Thiếu file pdf_utils.py hoặc hàm export_route_to_pdf.")
    def check_bot_stations(route_points, df_bot): return []
    def load_bot_stations(filename): return pd.DataFrame()


# ======================= #
# HÀM TẠO BẢN ĐỒ VỚI FOLIUM
# ======================= #

def create_route_map(route_points: List[Tuple[float, float]], df_charge: pd.DataFrame, bot_stations: List[Dict]) -> str:
    """
    Tạo bản đồ tương tác (HTML) sử dụng Folium hiển thị lộ trình, trạm sạc và trạm BOT.
    
    :param route_points: Danh sách các cặp (lat, lng) tạo nên lộ trình.
    :param df_charge: DataFrame chứa dữ liệu trạm sạc.
    :param bot_stations: Danh sách các trạm BOT được đi qua.
    :return: Đường dẫn tới file HTML bản đồ.
    """
    if not route_points:
        return ""

    # Tạo bản đồ, tập trung vào điểm bắt đầu
    start_lat, start_lng = route_points[0]
    m = folium.Map(location=[start_lat, start_lng], zoom_start=6)

    # 1. Vẽ Lộ trình
    folium.PolyLine(locations=route_points, color="blue", weight=5, opacity=0.7).add_to(m)

    # 2. Đánh dấu các điểm trên lộ trình
    for i, (lat, lng) in enumerate(route_points):
        popup_text = f"Lat: {lat:.4f}, Lng: {lng:.4f}"
        
        icon = 'info'
        color = 'gray'
        
        if i == 0:
            color = 'green'
            icon = 'play'
            popup_text = "Điểm BẮT ĐẦU"
        elif i == len(route_points) - 1:
            color = 'red'
            icon = 'flag'
            popup_text = "Điểm KẾT THÚC"
        else:
            # Đây là một trạm sạc
            info_row = df_charge[(df_charge['lat'].astype(float) == lat) & (df_charge['lng'].astype(float) == lng)]
            if not info_row.empty:
                station_name = info_row.iloc[0]['name']
                popup_text = f"Trạm Sạc: {station_name}"
                color = 'orange'
                icon = 'bolt'

        folium.Marker(
            [lat, lng],
            popup=popup_text,
            icon=folium.Icon(color=color, icon=icon, prefix='fa')
        ).add_to(m)
        
    # 3. Đánh dấu các trạm BOT đi qua (nếu có)
    for bot in bot_stations:
        bot_lat = float(bot['lat'])
        bot_lng = float(bot['lng'])
        bot_name = bot['name']
        
        folium.CircleMarker(
            location=[bot_lat, bot_lng],
            radius=10,
            color='#FF00FF', # Màu hồng
            fill=True,
            fill_color='#FF00FF',
            fill_opacity=0.6,
            popup=f"Trạm BOT: {bot_name} - Phí: {bot['fee']}"
        ).add_to(m)


    # Lưu bản đồ vào file HTML tạm
    map_file_path = os.path.join(os.getcwd(), "route_map_temp.html")
    m.save(map_file_path)
    return map_file_path

# --- HÀM TRỢ GIÚP ---
def load_charging_stations(filename='charging_stations.csv'):
    """Tải dữ liệu trạm sạc"""
    try:
        df = pd.read_csv(filename, skipinitialspace=True)
        df = df[df['lat'].notnull() & df['lng'].notnull()]
        # Đảm bảo cột lat/lng là float
        df['lat'] = df['lat'].astype(float)
        df['lng'] = df['lng'].astype(float)
        return df.reset_index(drop=True)
    except FileNotFoundError:
        messagebox.showerror("Lỗi", f"Không tìm thấy file dữ liệu: {filename}")
        return pd.DataFrame()

# --- ỨNG DỤNG GUI CHÍNH ---
class ElectricCarRoutingApp:
    def __init__(self, master):
        self.master = master
        master.title("Hệ thống Lập kế hoạch lộ trình Xe điện")
        master.geometry("1100x700") # Mở rộng giao diện
        
        self.df_charge = load_charging_stations()
        self.df_bot = load_bot_stations() # Tải dữ liệu BOT
        
        if self.df_charge.empty:
            master.quit()
            return
            
        self.car_names = [car.name for car in cars]
        self.selected_car = tk.StringVar(master)
        self.selected_car.set(self.car_names[0]) 
        self.map_file_path = None # Khai báo biến lưu đường dẫn file bản đồ

        # Thuật toán lựa chọn: A* hoặc UCS
        self.algorithms = ["A*", "UCS"]
        self.selected_algorithm = tk.StringVar(master)
        self.selected_algorithm.set(self.algorithms[0])

        # --- TẠO CÁC KHUNG CHÍNH ---
        self.config_frame = tk.LabelFrame(master, text="CẤU HÌNH LỘ TRÌNH", padx=10, pady=10)
        self.config_frame.pack(side=tk.LEFT, fill="y", padx=10, pady=10)

        self.result_frame = tk.LabelFrame(master, text="KẾT QUẢ TÌM KIẾM", padx=10, pady=10)
        self.result_frame.pack(side=tk.RIGHT, fill="both", expand=True, padx=10, pady=10)

        # --- 1. KHUNG CẤU HÌNH (INPUT) ---
        self._setup_car_config()
        self._setup_route_input()
        self._setup_buttons()

        # --- 2. KHUNG KẾT QUẢ (OUTPUT) ---
        self._setup_result_display()
        
        self.last_search_result = None # Lưu kết quả cuối cùng để xuất PDF

    def _setup_car_config(self):
        # Chọn xe
        tk.Label(self.config_frame, text="1. Chọn Mẫu Xe:", font=("Arial", 10, "bold")).pack(anchor='w', pady=(5, 0))
        tk.OptionMenu(self.config_frame, self.selected_car, *self.car_names, command=self.update_car_info).pack(fill='x', pady=2)

        # Chọn thuật toán
        tk.Label(self.config_frame, text="Thuật toán tìm kiếm:", font=("Arial", 10, "bold")).pack(anchor='w', pady=(10, 0))
        tk.OptionMenu(self.config_frame, self.selected_algorithm, *self.algorithms).pack(fill='x', pady=2)

        # Hiển thị thông tin xe
        self.lbl_car_info = tk.Label(self.config_frame, text="Thông số xe:", justify=tk.LEFT, fg="blue", wraplength=300)
        self.lbl_car_info.pack(anchor='w', pady=5)
        self.update_car_info(self.car_names[0])

    def _setup_route_input(self):
        # Input Tọa độ
        tk.Label(self.config_frame, text="2. Tọa độ (Vĩ độ, Kinh độ - VD: 10.76,106.69)", font=("Arial", 10, "bold")).pack(anchor='w', pady=(10, 0))
        
        tk.Label(self.config_frame, text="Bắt đầu:").pack(anchor='w')
        self.entry_start = tk.Entry(self.config_frame, width=35)
        self.entry_start.insert(0, "20.825,105.351") # Giá trị mặc định: Hòa Bình
        self.entry_start.pack(fill='x', pady=2)

        tk.Label(self.config_frame, text="Kết thúc:").pack(anchor='w')
        self.entry_end = tk.Entry(self.config_frame, width=35)
        self.entry_end.insert(0, "10.771,106.701") # Giá trị mặc định: TP.HCM
        self.entry_end.pack(fill='x', pady=2)

        # Pin khởi hành
        tk.Label(self.config_frame, text="3. Pin khởi hành (0-100%):", font=("Arial", 10, "bold")).pack(anchor='w', pady=(10, 0))
        self.entry_pin = tk.Entry(self.config_frame, width=10)
        self.entry_pin.insert(0, "80")
        self.entry_pin.pack(anchor='w', pady=2)

        # Tránh trạm thu phí
        self.qua_tram_thu_phi_var = tk.BooleanVar(self.master, value=False)
        tk.Checkbutton(self.config_frame, text="Tránh trạm thu phí BOT", variable=self.qua_tram_thu_phi_var).pack(anchor='w', pady=5)

    def _setup_buttons(self):
        self.btn_search = tk.Button(self.config_frame, text="TÌM LỘ TRÌNH TỐI ƯU", command=self.run_search, bg="#4CAF50", fg="white", font=("Arial", 11, "bold"))
        self.btn_search.pack(fill='x', pady=15)
        # Theo dõi thay đổi thuật toán để cập nhật nút
        self.selected_algorithm.trace_add('write', self._update_search_button_text)

        # Thêm nút xuất PDF
        self.btn_export_pdf = tk.Button(self.config_frame, text="Xuất file PDF", command=self.export_pdf, bg="#2196F3", fg="white", font=("Arial", 11, "bold"))
        self.btn_export_pdf.pack(fill='x', pady=5)

        # THÊM NÚT XEM BẢN ĐỒ
        self.btn_show_map = tk.Button(self.config_frame, text="XEM BẢN ĐỒ LỘ TRÌNH (HTML)", command=self.show_map, bg="#FF9800", fg="white", font=("Arial", 11, "bold"), state=tk.DISABLED)
        self.btn_show_map.pack(fill='x', pady=5)

    def _update_search_button_text(self, *args):
        algo = self.selected_algorithm.get()
        if algo == "A*":
            self.btn_search.config(text="TÌM LỘ TRÌNH TỐI ƯU (A*)")
        elif algo == "UCS":
            self.btn_search.config(text="TÌM LỘ TRÌNH TỐI ƯU (UCS)")
        else:
            self.btn_search.config(text="TÌM LỘ TRÌNH TỐI ƯU")

    def _setup_result_display(self):
        # Khung Tổng kết
        self.summary_frame = tk.LabelFrame(self.result_frame, text="TÓM TẮT", padx=10, pady=10)
        self.summary_frame.pack(fill='x', pady=(0, 10))
        
        self.lbl_dist = tk.Label(self.summary_frame, text="Tổng quãng đường di chuyển: N/A", anchor='w', fg="#333", font=("Arial", 10))
        self.lbl_dist.pack(fill='x')
        self.lbl_time = tk.Label(self.summary_frame, text="Tổng thời gian lái xe: N/A", anchor='w', fg="#333", font=("Arial", 10))
        self.lbl_time.pack(fill='x')
        self.lbl_charge = tk.Label(self.summary_frame, text="Tổng thời gian sạc: N/A", anchor='w', fg="#333", font=("Arial", 10))
        self.lbl_charge.pack(fill='x')
        self.lbl_fee = tk.Label(self.summary_frame, text="Tổng chi phí sạc: N/A", anchor='w', fg="#333", font=("Arial", 10))
        self.lbl_fee.pack(fill='x')
        self.lbl_bot_fee = tk.Label(self.summary_frame, text="Tổng phí qua các trạm BOT: N/A", anchor='w', fg="#333", font=("Arial", 10))
        self.lbl_bot_fee.pack(fill='x')

        # Khung Chi tiết
        tk.Label(self.result_frame, text="CHI TIẾT LỘ TRÌNH (Trạm sạc & Hoạt động)", font=("Arial", 10, "bold")).pack(anchor='w', pady=(5, 0))
        self.txt_path = scrolledtext.ScrolledText(self.result_frame, width=50, height=20, font=("Consolas", 9), state='disabled')
        self.txt_path.pack(fill='both', expand=True)
        

    def _get_selected_car(self) -> Optional[ElectricCar]:
        """Tìm đối tượng xe được chọn"""
        name = self.selected_car.get()
        for car in cars:
            if car.name == name:
                return car
        return None

    def update_car_info(self, car_name):
        """Cập nhật thông số xe khi chọn từ Dropdown"""
        car = self._get_selected_car()
        if car:
            info = f"Pin: {car.battery_capacity} kWh\n"
            info += f"Quãng đường: {car.max_km_per_charge} km\n"
            info += f"Tiêu thụ: {car.tinh_tieu_thu():.4f} kWh/km" 
            self.lbl_car_info.config(text=info)
            
    def _clear_summary(self):
        self.lbl_dist.config(text="Tổng quãng đường di chuyển: N/A")
        self.lbl_time.config(text="Tổng thời gian lái xe: N/A")
        self.lbl_charge.config(text="Tổng thời gian sạc: N/A")
        self.lbl_fee.config(text="Tổng chi phí sạc: N/A")
        self.lbl_bot_fee.config(text="Tổng phí qua các trạm BOT: N/A")
        self.btn_show_map.config(state=tk.DISABLED) # Tắt nút bản đồ khi lỗi
        self.map_file_path = None


    def run_search(self):
        """Thực hiện tìm kiếm và hiển thị kết quả"""
        self._clear_summary() # Xóa kết quả cũ
        self.btn_show_map.config(state=tk.DISABLED)
        self.map_file_path = None

        try:
            # 1. Lấy và kiểm tra input
            start_coords = [float(x.strip()) for x in self.entry_start.get().split(',')]
            end_coords = [float(x.strip()) for x in self.entry_end.get().split(',')]
            pin_percent = int(self.entry_pin.get())
            qua_tram_thu_phi = self.qua_tram_thu_phi_var.get()

            if not (0 <= pin_percent <= 100):
                raise ValueError("Phần trăm pin không hợp lệ (0-100).")

            car = self._get_selected_car()
            if not car:
                raise ValueError("Vui lòng chọn xe.")

        except Exception as e:
            messagebox.showerror("Lỗi Input", f"Dữ liệu nhập không hợp lệ: {e}")
            return

        # 2. Chạy thuật toán theo lựa chọn
        self.btn_search.config(text="ĐANG TÌM KIẾM...", state=tk.DISABLED, bg="orange")
        self.master.update()

        algorithm = self.selected_algorithm.get()
        if algorithm == "A*":
            result = run_astar_search(car, start_coords[0], start_coords[1], end_coords[0], end_coords[1], pin_percent, qua_tram_thu_phi, self.df_charge)
        elif algorithm == "UCS":
            try:
                from file import run_ucs_search
            except ImportError:
                messagebox.showerror("Lỗi", "Thiếu hàm run_ucs_search trong file.py!")
                self._update_search_button_text()
                self.btn_search.config(state=tk.NORMAL, bg="#4CAF50")
                return
            result = run_ucs_search(car, start_coords[0], start_coords[1], end_coords[0], end_coords[1], pin_percent, qua_tram_thu_phi, self.df_charge)
        else:
            messagebox.showerror("Lỗi", "Thuật toán không hợp lệ!")
            self._update_search_button_text()
            self.btn_search.config(state=tk.NORMAL, bg="#4CAF50")
            return

        self._update_search_button_text()
        self.btn_search.config(state=tk.NORMAL, bg="#4CAF50")

        # 3. Hiển thị kết quả
        self.txt_path.config(state='normal')
        self.txt_path.delete('1.0', tk.END)

        if "error" in result:
            messagebox.showerror("Lỗi Tìm kiếm", result['error'])
            self.txt_path.insert(tk.END, f"LỖI: {result['error']}\nVui lòng kiểm tra lại tọa độ hoặc pin.")
            self._clear_summary()
            self.last_search_result = None
            return

        # Lấy tên trạm bắt đầu/kết thúc từ lộ trình
        start_station = result['path'][1].get('node', 'unknown') if len(result['path']) > 1 else 'unknown'
        end_station = result['path'][-2].get('node', 'unknown').replace(' (TRẠM CUỐI)', '') if len(result['path']) > 1 else 'unknown'


        # --- Tính toán phí BOT (ĐÃ HOÀN THIỆN) và Lấy Tọa độ Lộ trình ---
        route_points = []
        # 1. Điểm bắt đầu thực tế
        route_points.append(tuple(start_coords)) 
        # 2. Các trạm sạc/điểm trung gian
        for step in result['path'][1:-1]:
            # Lấy tọa độ trạm sạc
            node_name = step['node'].replace(' (TRẠM CUỐI)', '')
            info_row = self.df_charge[self.df_charge['name'] == node_name]
            if not info_row.empty:
                lat = float(info_row.iloc[0]['lat'])
                lng = float(info_row.iloc[0]['lng'])
                route_points.append((lat, lng))
        # 3. Điểm kết thúc thực tế
        route_points.append(tuple(end_coords))

        bot_stations = check_bot_stations(route_points, self.df_bot)

        # Tính tổng phí BOT
        total_bot_fee = 0
        bot_info_text = ""
        for bot in bot_stations:
            # Xử lý phí: loại bỏ ký tự không phải số và chuyển sang int
            fee_raw = re.sub(r'[^\d]', '', bot['fee'])
            fee_int = int(fee_raw) if fee_raw else 0
            
            # Chỉ tính phí nếu không tránh BOT HOẶC nếu BOT được coi là không thể tránh
            if not qua_tram_thu_phi:
                total_bot_fee += fee_int
                bot_info_text += f"- {bot['name']} ({bot['address']}): {bot['fee']}\n"
            else:
                bot_info_text += f"- {bot['name']} ({bot['address']}): ĐÃ TRÁNH\n"


        # --- Hiển thị Tóm tắt ---
        self.lbl_dist.config(text=f"Tổng quãng đường di chuyển: {result['total_dist']:.2f} km")
        time_lai_hour = result['total_time_lai'] // 60
        time_lai_min = result['total_time_lai'] % 60
        time_sac_hour = result['total_time_sac'] // 60
        time_sac_min = result['total_time_sac'] % 60
        
        self.lbl_time.config(text=f"Tổng thời gian lái xe: {int(time_lai_hour)} giờ {int(time_lai_min)} phút")
        self.lbl_charge.config(text=f"Tổng thời gian sạc: {int(time_sac_hour)} giờ {int(time_sac_min)} phút")
        self.lbl_fee.config(text=f"Tổng chi phí sạc: {result['total_fee']:.0f} VND")
        self.lbl_bot_fee.config(text=f"Tổng phí qua các trạm BOT: {total_bot_fee:.0f} VND (Tránh BOT: {'Có' if qua_tram_thu_phi else 'Không'})")

        # --- Hiển thị Chi tiết ---
        full_path_text = f"TÓM TẮT:\n"
        full_path_text += f"Xe: {car.name} | Pin ban đầu: {pin_percent}%\n"
        full_path_text += f"Xuất phát: {self.entry_start.get()} (Gần trạm {start_station})\n"
        full_path_text += f"Kết thúc: {self.entry_end.get()} (Gần trạm {end_station})\n"
        full_path_text += "---------------------------------------\n"

        for step in result['path']:
            dist_km = step.get('dist_lai', 0)
            time_min = step.get('time_lai', 0)

            if step['node'] == "Điểm BẮT ĐẦU":
                full_path_text += f"1. {step['node']} -> {start_station}:\n"
            elif step['node'] == "Điểm KẾT THÚC":
                full_path_text += f"\n{len(result['path'])-1}. {end_station} -> {step['node']}:\n"
            else:
                full_path_text += f"\n{step['node']}:\n"
            
            full_path_text += f"   - Quãng đường: {dist_km:.2f} km\n"
            full_path_text += f"   - Thời gian lái: {int(time_min)} phút\n"
            
            if 'charge_status' in step:
                full_path_text += f"   - Tình trạng Pin/Sạc: {step['charge_status']}\n"
            
            full_path_text += "---------------------------------------\n"
        
        # Thêm danh sách BOT đã đi qua (nếu có)
        if bot_stations:
            full_path_text += "\nTHÔNG TIN TRẠM THU PHÍ ĐI QUA:\n"
            full_path_text += bot_info_text
            full_path_text += f"Tổng phí BOT: {total_bot_fee:.0f} VND (Chỉ tính nếu KHÔNG tránh BOT)\n"

        self.txt_path.insert(tk.END, full_path_text)
        self.txt_path.see(tk.END)
        self.txt_path.config(state='disabled')

        # --- TẠO BẢN ĐỒ VÀ KÍCH HOẠT NÚT XEM BẢN ĐỒ ---
        try:
            map_path = create_route_map(route_points, self.df_charge, bot_stations)
            if map_path:
                self.map_file_path = map_path
                self.btn_show_map.config(state=tk.NORMAL)
        except Exception as e:
            messagebox.showwarning("Cảnh báo Bản đồ", f"Không thể tạo bản đồ (thiếu thư viện folium?): {e}")


        # Lưu lại dữ liệu kết quả để xuất PDF
        summary_text = f"Tổng quãng đường di chuyển: {result['total_dist']:.2f} km\n"
        summary_text += f"Tổng thời gian lái xe: {int(time_lai_hour)} giờ {int(time_lai_min)} phút\n"
        summary_text += f"Tổng thời gian sạc: {int(time_sac_hour)} giờ {int(time_sac_min)} phút\n"
        summary_text += f"Tổng chi phí sạc: {result['total_fee']:.0f} VND\n"
        summary_text += f"Tổng phí BOT: {total_bot_fee:.0f} VND (Tránh BOT: {'Có' if qua_tram_thu_phi else 'Không'})"

        self.last_search_result = {
            'model': car.name,
            'pin': pin_percent,
            'start_coords': self.entry_start.get(),
            'end_coords': self.entry_end.get(),
            'summary': summary_text,
            'details': full_path_text
        }

    def export_pdf(self):
        """Xuất kết quả tìm kiếm cuối cùng ra file PDF"""
        if self.last_search_result is None:
            messagebox.showwarning("Cảnh báo", "Vui lòng chạy tìm kiếm lộ trình trước khi xuất PDF.")
            return

        try:
            res = self.last_search_result
            # Sử dụng hàm export_route_to_pdf từ pdf_utils
            export_route_to_pdf(
                model=res['model'],
                pin=res['pin'],
                start_coords=res['start_coords'],
                end_coords=res['end_coords'],
                summary=res['summary'],
                details=res['details']
            )
            messagebox.showinfo("Thành công", f"Đã xuất lộ trình ra file PDF!")
        
        except Exception as e:
            messagebox.showerror("Lỗi Xuất PDF", f"Đã xảy ra lỗi khi xuất file: {e}")

    def show_map(self):
        """Mở bản đồ HTML trong trình duyệt mặc định"""
        if self.map_file_path and os.path.exists(self.map_file_path):
            webbrowser.open_new_tab(f'file://{os.path.realpath(self.map_file_path)}')
        else:
            messagebox.showwarning("Cảnh báo", "Không tìm thấy file bản đồ. Vui lòng chạy tìm kiếm lộ trình trước.")


if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = ElectricCarRoutingApp(root)
        root.mainloop()
    except Exception as e:
        messagebox.showerror("Lỗi Khởi tạo", f"Ứng dụng gặp lỗi khi khởi tạo: {e}.")