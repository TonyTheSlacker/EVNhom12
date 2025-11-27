import tkinter as tk
from tkinter import messagebox, scrolledtext
import pandas as pd
from typing import Optional
from models import ElectricCar, cars
import numpy as np
import heapq
import time
from math import radians, sin, cos, sqrt, atan2
from typing import List, Tuple, Dict, Any

TIMEOUT_SECONDS = 120 # Giới hạn thời gian tìm kiếm
AVG_SPEED_KMH = 100 # Tốc độ di chuyển trung bình (dùng để tính thời gian lái xe)
R_EARTH = 6371.0 # Bán kính Trái Đất (km)
ROAD_FACTOR = 1.25 # HỆ SỐ ƯỚC TÍNH ĐƯỜNG BỘ: 1.25 x Đường chim bay = Quãng đường thực tế

def haversine(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    lat1, lng1, lat2, lng2 = map(radians, [lat1, lng1, lat2, lng2])
    dlat = lat2 - lat1
    dlng = lng2 - lng1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlng/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    return R_EARTH * c

def find_nearest_node(lat: float, lng: float, df_charge: pd.DataFrame) -> str:
    df = df_charge.copy()
    df = df[df['lat'].notnull() & df['lng'].notnull()]
    df['dist'] = ((df['lat'].astype(float) - lat)**2 + (df['lng'].astype(float) - lng)**2).apply(np.sqrt)
    if df.empty:
        return 'unknown'
    nearest = df.loc[df['dist'].idxmin()]
    return nearest['name'] if 'name' in nearest else 'unknown'

def astar_charging_stations(df_charge: pd.DataFrame, start: str, end: str, battery_max: int, battery_start: int, avoid_toll: bool = False) -> Tuple[List[int], List[Tuple[str, int, int, float, float]], float]:
    import os
    import csv
    start_time = time.time()
    idx_start = df_charge[df_charge['name'] == start].index[0] if not df_charge[df_charge['name'] == start].empty else None
    idx_end = df_charge[df_charge['name'] == end].index[0] if not df_charge[df_charge['name'] == end].empty else None
    if idx_start is None or idx_end is None:
        return None, None, None
    end_lat, end_lng = float(df_charge.loc[idx_end, 'lat']), float(df_charge.loc[idx_end, 'lng'])
    def heuristic(idx: int) -> float:
        lat1, lng1 = float(df_charge.loc[idx, 'lat']), float(df_charge.loc[idx, 'lng'])
        return haversine(lat1, lng1, end_lat, end_lng) * ROAD_FACTOR
    f_start = 0 + heuristic(idx_start)
    initial_log = [(df_charge.loc[idx_start, 'name'], battery_start, 0, float(df_charge.loc[idx_start, 'lat']), float(df_charge.loc[idx_start, 'lng']))]
    heap = [(f_start, 0, idx_start, battery_start, [idx_start], initial_log)]
    visited = dict()
    graph_path = os.path.join(os.path.dirname(__file__), 'graph.csv')
    toll_edges = set()
    if avoid_toll:
        try:
            with open(graph_path, encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row.get('toll') and str(row['toll']).strip() == '1':
                        toll_edges.add((row['from'], row['to']))
        except Exception:
            pass
    while heap:
        if time.time() - start_time > TIMEOUT_SECONDS:
            return None, None, None
        f_score, total_dist, current, battery, path, charge_log = heapq.heappop(heap)
        if (current, battery) in visited and visited[(current, battery)] <= total_dist:
            continue
        visited[(current, battery)] = total_dist
        if current == idx_end:
            return path, charge_log, total_dist
        lat1, lng1 = float(df_charge.loc[current, 'lat']), float(df_charge.loc[current, 'lng'])
        candidates = []
        for next_idx in df_charge.index:
            if next_idx == current:
                continue
            if avoid_toll:
                from_name = df_charge.loc[current, 'name']
                to_name = df_charge.loc[next_idx, 'name']
                if (from_name, to_name) in toll_edges or (to_name, from_name) in toll_edges:
                    continue
            lat2, lng2 = float(df_charge.loc[next_idx, 'lat']), float(df_charge.loc[next_idx, 'lng'])
            dist_km_straight = haversine(lat1, lng1, lat2, lng2)
            dist_km_road = dist_km_straight * ROAD_FACTOR
            if dist_km_road > battery_max:
                continue
            dist_to_end = haversine(lat2, lng2, end_lat, end_lng) * ROAD_FACTOR
            candidates.append((dist_to_end, next_idx, dist_km_road))
        candidates.sort()
        for _, next_idx, dist_km in candidates[:10]:
            battery_after_travel = battery - dist_km
            if battery_after_travel < 0:
                max_charge = int(battery_max * 0.9)
                charge_to = max(max_charge, int(dist_km + 1))
                charge_to = min(charge_to, battery_max)
                charge_amount = charge_to - battery
                new_battery = charge_to - dist_km
                new_charge_log = charge_log + [(df_charge.loc[current, 'name'], new_battery, charge_amount, lat1, lng1)]
            else:
                charge_to = battery
                charge_amount = 0
                new_battery = battery_after_travel
                new_charge_log = charge_log + [(df_charge.loc[current, 'name'], new_battery, charge_amount, lat1, lng1)]
            if new_battery < 0:
                continue
            new_total_dist = total_dist + dist_km
            new_f_score = new_total_dist + heuristic(next_idx)
            heapq.heappush(heap, (new_f_score, new_total_dist, next_idx, new_battery, path + [next_idx], new_charge_log))
    return None, None, None

def run_astar_search(car: Any, lat_start: float, lng_start: float, lat_end: float, lng_end: float, battery_percent: int, qua_tram_thu_phi: bool, df_charge: pd.DataFrame) -> Dict[str, Any]:
    battery_max = car.max_km_per_charge
    start_node = find_nearest_node(lat_start, lng_start, df_charge)
    end_node = find_nearest_node(lat_end, lng_end, df_charge)
    if end_node == 'unknown' or start_node == 'unknown':
        return {"error": "Không tìm thấy trạm sạc gần điểm bắt đầu hoặc kết thúc."}
    info_start_node = df_charge[df_charge['name'] == start_node].iloc[0]
    info_end_node = df_charge[df_charge['name'] == end_node].iloc[0]
    lat_first, lng_first = float(info_start_node['lat']), float(info_start_node['lng'])
    lat_last, lng_last = float(info_end_node['lat']), float(info_end_node['lng'])
    dist_to_first_road = haversine(lat_start, lng_start, lat_first, lng_first) * ROAD_FACTOR
    battery_start_actual = int(battery_max * battery_percent / 100)
    battery_at_first_station = battery_start_actual - dist_to_first_road
    if battery_at_first_station < 0:
        return {"error": f"Không đủ pin ({battery_start_actual:.0f} km) để đi tới trạm sạc đầu tiên ({dist_to_first_road:.0f} km)."}
    path, charge_log, total_dist_stations = astar_charging_stations(df_charge, start_node, end_node, battery_max, battery_at_first_station, avoid_toll=qua_tram_thu_phi)
    if path is None:
        return {"error": "Không tìm được đường đi hợp lệ (Timeout hoặc không có đường giữa các trạm)."}
    dist_to_last_road = haversine(lat_last, lng_last, lat_end, lng_end) * ROAD_FACTOR
    total_dist_full = total_dist_stations + dist_to_first_road + dist_to_last_road
    total_time_sac = 0
    total_fee = 0
    time_to_first_road = (dist_to_first_road / AVG_SPEED_KMH) * 60
    time_to_last_road = (dist_to_last_road / AVG_SPEED_KMH) * 60
    total_time_lai = total_dist_stations / AVG_SPEED_KMH * 60 + time_to_first_road + time_to_last_road
    detailed_path = []
    detailed_path.append({
        'node': "Điểm BẮT ĐẦU",
        'address': f"Di chuyển tới {start_node}",
        'charge_status': f"Pin ban đầu: {battery_start_actual:.0f} km. Pin khi tới: {battery_at_first_station:.0f} km.",
        'time_lai': time_to_first_road,
        'dist_lai': dist_to_first_road
    })
    for idx_log, (node, new_battery, charge_amount, lat, lng) in enumerate(charge_log):
        if idx_log == 0: continue
        info_row = df_charge[df_charge['name'] == node]
        if info_row.empty: continue
        info = info_row.iloc[0]
        prev_log = charge_log[idx_log-1]
        battery_before_charge = prev_log[1] if prev_log[2] == 0 else prev_log[1] - charge_amount
        dist_lai = haversine(prev_log[3], prev_log[4], lat, lng) * ROAD_FACTOR
        percent = int(new_battery / battery_max * 100)
        charge_info = ""
        fee = 0
        if charge_amount > 0:
            charge_time = charge_amount / 2
            if battery_before_charge > battery_max * 0.8:
                if charge_time <= 30:
                    fee = charge_time * 1000
                elif charge_time <= 60:
                    fee = 30 * 1000 + (charge_time - 30) * 2000
                else:
                    fee = 30 * 1000 + 30 * 2000 + (charge_time - 60) * 3000
                total_time_sac += charge_time
                total_fee += fee
                charge_info = f"SẠC {charge_amount:.0f} km. Pin tới: {new_battery:.0f} km ({percent}%). Thời gian sạc: {charge_time:.1f} phút. Phí: {fee:.0f} VND."
            else:
                charge_info = f"SẠC {charge_amount:.0f} km. Pin tới: {new_battery:.0f} km ({percent}%). Miễn phí sạc."
        detailed_path.append({
            'node': info['name'] + (" (TRẠM CUỐI)" if node == end_node else ""),
            'address': info['address'],
            'charge_status': charge_info if charge_amount > 0 else f"Pin còn lại {new_battery:.0f} km ({percent}%) khi tới.",
            'time_lai': (dist_lai / AVG_SPEED_KMH) * 60,
            'dist_lai': dist_lai
        })
    detailed_path.append({
        'node': "Điểm KẾT THÚC",
        'address': f"Di chuyển từ {end_node}",
        'charge_status': f"Di chuyển: {dist_to_last_road:.1f} km. Kết thúc hành trình.",
        'time_lai': time_to_last_road,
        'dist_lai': dist_to_last_road
    })
    return {
        "path": detailed_path,
        "total_dist": total_dist_full,
        "total_time_lai": total_time_lai,
        "total_time_sac": total_time_sac,
        "total_fee": total_fee,
        "qua_tram_thu_phi": qua_tram_thu_phi
    }

# --- HÀM TRỢ GIÚP ---
def load_charging_stations(filename='charging_stations.csv'):
    """Tải dữ liệu trạm sạc"""
    try:
        df = pd.read_csv(filename, skipinitialspace=True)
        # Đảm bảo cột lat/lng tồn tại và không rỗng
        df = df[df['lat'].notnull() & df['lng'].notnull()]
        return df.reset_index(drop=True)
    except FileNotFoundError:
        messagebox.showerror("Lỗi", f"Không tìm thấy file dữ liệu: {filename}")
        return pd.DataFrame()

# --- ỨNG DỤNG GUI CHÍNH ---
class ElectricCarRoutingApp:
    def __init__(self, master):
        self.master = master
        master.title("Hệ thống Lập kế hoạch lộ trình Xe điện")
        master.geometry("850x700")
        
        self.df_charge = load_charging_stations()
        if self.df_charge.empty:
            master.quit()
            return
            
        # Biến điều khiển xe
        self.car_names = [car.name for car in cars]
        self.selected_car = tk.StringVar(master)
        self.selected_car.set(self.car_names[0]) 

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

    def _setup_car_config(self):
        # Chọn xe
        tk.Label(self.config_frame, text="1. Chọn Mẫu Xe:", font=("Arial", 10, "bold")).pack(anchor='w', pady=(5, 0))
        tk.OptionMenu(self.config_frame, self.selected_car, *self.car_names, command=self.update_car_info).pack(fill='x', pady=2)
        
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
        self.entry_end.insert(0, "10.250,105.970") # Giá trị mặc định: Vĩnh Long
        self.entry_end.pack(fill='x', pady=2)

        # Input Pin còn lại
        tk.Label(self.config_frame, text="3. % Pin còn lại (0-100):", font=("Arial", 10, "bold")).pack(anchor='w', pady=(10, 0))
        self.entry_pin = tk.Entry(self.config_frame, width=35)
        self.entry_pin.insert(0, "100")
        self.entry_pin.pack(fill='x', pady=2)
        
        # Checkbox cầu đường (chưa tích hợp logic hoàn toàn)
        self.qua_tram_thu_phi_var = tk.BooleanVar()
        tk.Checkbutton(self.config_frame, text="Ưu tiên tránh trạm thu phí", variable=self.qua_tram_thu_phi_var).pack(anchor='w', pady=5)

    def _setup_buttons(self):
        self.btn_search = tk.Button(self.config_frame, text="TÌM LỘ TRÌNH TỐI ƯU (A*)", command=self.run_search, bg="#4CAF50", fg="white", font=("Arial", 11, "bold"))
        self.btn_search.pack(fill='x', pady=15)
        # Thêm nút xuất PDF
        self.btn_export_pdf = tk.Button(self.config_frame, text="Xuất file PDF", command=self.export_pdf, bg="#2196F3", fg="white", font=("Arial", 11, "bold"))
        self.btn_export_pdf.pack(fill='x', pady=5)

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
        self.lbl_start_station = tk.Label(self.summary_frame, text="Trạm bắt đầu: N/A", anchor='w', fg="#333", font=("Arial", 10))
        self.lbl_start_station.pack(fill='x')
        self.lbl_end_station = tk.Label(self.summary_frame, text="Trạm kết thúc: N/A", anchor='w', fg="#333", font=("Arial", 10))
        self.lbl_end_station.pack(fill='x')
        self.lbl_bot_fee = tk.Label(self.summary_frame, text="Tổng chi phí qua các trạm BOT: N/A", anchor='w', fg="#333", font=("Arial", 10))
        self.lbl_bot_fee.pack(fill='x')
        
        # Khung Chi tiết
        tk.Label(self.result_frame, text="CHI TIẾT LỘ TRÌNH (Trạm sạc & Hoạt động)", font=("Arial", 10, "bold")).pack(anchor='w', pady=(5, 0))
        self.txt_path = scrolledtext.ScrolledText(self.result_frame, width=50, height=20, font=("Consolas", 9), state='disabled')
        self.txt_path.pack(fill='both', expand=True)

    def update_car_info(self, car_name):
        """Cập nhật thông số xe khi chọn từ Dropdown"""
        car = self._get_selected_car()
        if car:
            info = f"Pin: {car.battery_capacity} kWh\n"
            info += f"Quãng đường: {car.max_km_per_charge} km\n"
            info += f"Tiêu thụ: {car.tinh_tieu_thu():.4f} kWh/km"
            self.lbl_car_info.config(text=info)

    def _get_selected_car(self) -> Optional[ElectricCar]:
        """Tìm đối tượng xe được chọn"""
        name = self.selected_car.get()
        for car in cars:
            if car.name == name:
                return car
        return None

    def run_search(self):
        """Thực hiện tìm kiếm và hiển thị kết quả"""
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
        
        # 2. Chạy thuật toán A*
        self.btn_search.config(text="ĐANG TÌM KIẾM...", state=tk.DISABLED, bg="#FFA500")
        self.master.update_idletasks()
        
        # Nếu chọn tránh trạm BOT, loại bỏ các trạm sạc gần BOT khỏi df_charge
        df_charge_filtered = self.df_charge.copy()
        if qua_tram_thu_phi:
            import pandas as pd
            from utils import haversine
            df_bot = pd.read_csv('BOT.csv')
            bot_coords = []
            for idx, row in df_bot.iterrows():
                vido_kinhdo = row["Vĩ độ, Kinh độ"]
                if isinstance(vido_kinhdo, str):
                    bot_lat, bot_lng = map(float, vido_kinhdo.split(','))
                    bot_coords.append((round(bot_lat, 4), round(bot_lng, 4)))
            # Loại bỏ các trạm sạc nằm trong bán kính 5km quanh bất kỳ trạm BOT nào
            def is_near_bot(lat, lng):
                for bot_lat, bot_lng in bot_coords:
                    if haversine(round(lat,4), round(lng,4), bot_lat, bot_lng) <= 5:
                        return True
                return False
            df_charge_filtered = df_charge_filtered[~df_charge_filtered.apply(lambda row: is_near_bot(row['lat'], row['lng']), axis=1)].reset_index(drop=True)
        result = run_astar_search(car, start_coords[0], start_coords[1], 
                                  end_coords[0], end_coords[1], 
                                  pin_percent, False, df_charge_filtered)

        # 2.1. Kiểm tra lộ trình đi qua trạm BOT
        route_points = []
        for step in result.get('path', []):
            # Lấy lat/lng từ chi tiết đường đi nếu có
            if 'address' in step and 'Địa chỉ' not in step['address']:
                # Nếu là trạm sạc, lấy từ df_charge
                info_row = self.df_charge[self.df_charge['name'] == step['node'].replace(' (TRẠM CUỐI)', '')]
                if not info_row.empty:
                    lat = float(info_row.iloc[0]['lat'])
                    lng = float(info_row.iloc[0]['lng'])
                    route_points.append((lat, lng))
        # Thêm điểm bắt đầu/kết thúc nếu cần
        route_points.insert(0, tuple(start_coords))
        route_points.append(tuple(end_coords))

        from utils import check_bot_stations
        bot_stations = check_bot_stations(route_points)
        # Tính tổng phí BOT duy nhất bằng regex, dùng cho cả tóm tắt và chi tiết
        import re
        total_bot_fee = 0
        bot_info_text = ""
        for bot in bot_stations:
            bot_info_text += f"- {bot['name']} ({bot['address']}): {bot['fee']}\n"
            fee_raw = str(bot['fee'])
            numbers = re.findall(r'\d+', fee_raw)
            if numbers:
                fee_int = int(''.join(numbers))
                total_bot_fee += fee_int
        self.btn_search.config(text="TÌM LỘ TRÌNH TỐI ƯU (A*)", state=tk.NORMAL, bg="#4CAF50")

        # 3. Hiển thị kết quả
        self.txt_path.config(state='normal')
        self.txt_path.delete('1.0', tk.END)
        
        if "error" in result:
            messagebox.showerror("Lỗi Tìm kiếm", result['error'])
            self.txt_path.insert(tk.END, f"LỖI: {result['error']}\nVui lòng kiểm tra lại tọa độ hoặc pin.")
            self._clear_summary()
            return

        # Hiển thị Tóm tắt: dùng lại biến tổng phí BOT đã tính bằng regex ở chi tiết
        # Lấy tên trạm bắt đầu/kết thúc từ lộ trình
        # Lấy tên trạm bắt đầu/kết thúc từ address nếu có
        if result.get('path') and len(result['path']) >= 3:
            start_info = result['path'][1]
            end_info = result['path'][-2]
            start_station = start_info.get('node', 'unknown')
            end_station = end_info.get('node', 'unknown')
        elif result.get('path') and len(result['path']) > 0:
            start_station = result['path'][0].get('node', 'unknown')
            end_station = result['path'][-1].get('node', 'unknown')
        else:
            start_station = 'unknown'
            end_station = 'unknown'
        self.lbl_start_station = getattr(self, 'lbl_start_station', None)
        self.lbl_end_station = getattr(self, 'lbl_end_station', None)
        if not self.lbl_start_station:
            self.lbl_start_station = tk.Label(self.summary_frame, text=f"Trạm bắt đầu: {start_station}", anchor='w', fg="#333", font=("Arial", 10))
            self.lbl_start_station.pack(fill='x')
        else:
            self.lbl_start_station.config(text=f"Trạm bắt đầu: {start_station}")
        if not self.lbl_end_station:
            self.lbl_end_station = tk.Label(self.summary_frame, text=f"Trạm kết thúc: {end_station}", anchor='w', fg="#333", font=("Arial", 10))
            self.lbl_end_station.pack(fill='x')
        else:
            self.lbl_end_station.config(text=f"Trạm kết thúc: {end_station}")
        self.lbl_dist.config(text=f"Tổng quãng đường di chuyển: {result['total_dist']:.2f} km (Đã nhân hệ số ROAD_FACTOR)")
        total_time_lai_hours = result['total_time_lai'] / 60
        total_time_sac_hours = result['total_time_sac'] / 60
        self.lbl_time.config(text=f"Tổng thời gian lái xe: {total_time_lai_hours:.1f} tiếng ({result['total_time_lai']:.1f} phút)")
        self.lbl_charge.config(text=f"Tổng thời gian sạc: {total_time_sac_hours:.1f} tiếng ({result['total_time_sac']:.1f} phút)")
        self.lbl_fee.config(text=f"Tổng chi phí sạc: {result['total_fee']:.0f} VND")
        self.lbl_bot_fee.config(text=f"Tổng chi phí qua các trạm BOT: {total_bot_fee} VND")
        
        # Hiển thị Chi tiết đường đi
        full_path_text = "TÌM KIẾM HOÀN TẤT!\n\n"
        # Chèn thông tin BOT vào giữa các bước lộ trình
        bot_idx = 0
        for i, step in enumerate(result['path']):
            full_path_text += f"-> {step['node']}\n"
            full_path_text += f"   Địa chỉ: {step['address']}\n"
            full_path_text += f"   Di chuyển: {step['dist_lai']:.1f} km (Thời gian: {step['time_lai']:.1f} phút)\n"
            full_path_text += f"   Hoạt động: {step['charge_status']}\n"
            # Nếu có trạm BOT đi qua gần bước này thì chèn vào
            if bot_idx < len(bot_stations):
                bot = bot_stations[bot_idx]
                # Chỉ chèn nếu vị trí BOT gần vị trí bước này
                lat_step = None
                lng_step = None
                info_row = self.df_charge[self.df_charge['name'] == step['node'].replace(' (TRẠM CUỐI)', '')]
                if not info_row.empty:
                    lat_step = float(info_row.iloc[0]['lat'])
                    lng_step = float(info_row.iloc[0]['lng'])
                if lat_step is not None and lng_step is not None:
                    from utils import haversine
                    if haversine(lat_step, lng_step, bot['lat'], bot['lng']) <= 5:
                        full_path_text += f"   >> ĐI QUA TRẠM BOT: {bot['name']} ({bot['address']}) - Phí: {bot['fee']}\n"
                        bot_idx += 1
            full_path_text += "---------------------------------------\n"
        # Nếu còn trạm BOT chưa chèn thì thêm cuối
        while bot_idx < len(bot_stations):
            bot = bot_stations[bot_idx]
            full_path_text += f"   >> ĐI QUA TRẠM BOT: {bot['name']} ({bot['address']}) - Phí: {bot['fee']}\n"
            bot_idx += 1
        # Hiển thị tổng phí BOT đã tính ở trên
        full_path_text += f"\nTổng phí BOT: {total_bot_fee} VND\n"
            
        self.txt_path.insert(tk.END, full_path_text)
        self.txt_path.see(tk.END)
        self.txt_path.config(state='disabled')
        
        # Lưu lại dữ liệu kết quả để xuất PDF
        self.last_search_result = {
            'model': car.name,
            'pin': pin_percent,
            'start': self.entry_start.get(),
            'end': self.entry_end.get(),
            'summary': f"Tổng quãng đường di chuyển: {result['total_dist']:.2f} km\\nTổng thời gian lái xe: {result['total_time_lai']:.1f} phút\\nTổng thời gian sạc: {result['total_time_sac']:.1f} phút\\nTổng chi phí sạc: {result['total_fee']:.0f} VND | Tổng chi phí qua các trạm BOT: {total_bot_fee} VND",
            'details': full_path_text
        }

    def export_pdf(self):
        """Xuất file PDF với dữ liệu kết quả tìm kiếm"""
        try:
            from pdf_utils import export_route_to_pdf
        except ImportError:
            messagebox.showerror("Lỗi", "Không tìm thấy module pdf_utils!")
            return
        if not hasattr(self, 'last_search_result'):
            messagebox.showwarning("Chưa có dữ liệu", "Vui lòng tìm lộ trình trước khi xuất PDF!")
            return
        data = self.last_search_result
        filename = export_route_to_pdf(
            data['model'],
            data['pin'],
            data['start'],
            data['end'],
            data['summary'],
            data['details']
        )
        messagebox.showinfo("Xuất PDF thành công", f"Đã xuất file PDF: {filename}")

    def _clear_summary(self):
        self.lbl_dist.config(text="Tổng quãng đường di chuyển: N/A")
        self.lbl_time.config(text="Tổng thời gian lái xe: N/A")
        self.lbl_charge.config(text="Tổng thời gian sạc: N/A")
        self.lbl_fee.config(text="Tổng chi phí sạc: N/A")
        self.lbl_start_station.config(text="Trạm bắt đầu: N/A")
        self.lbl_end_station.config(text="Trạm kết thúc: N/A")
        self.lbl_bot_fee.config(text="Tổng chi phí qua các trạm BOT: N/A")

if __name__ == "__main__":

    root = tk.Tk()
    app = ElectricCarRoutingApp(root)
    root.mainloop()

# ======================= #
# 1. HÀM TÍNH TOÁN KHOẢNG CÁCH VÀ TÌM TRẠM GẦN NHẤT
# ======================= #

import numpy as np
import heapq
import time
from math import radians, sin, cos, sqrt, atan2
from typing import List, Tuple, Dict, Any

TIMEOUT_SECONDS = 60 # Giới hạn thời gian tìm kiếm
AVG_SPEED_KMH = 60 # Tốc độ di chuyển trung bình (dùng để tính thời gian lái xe)
R_EARTH = 6371.0 # Bán kính Trái Đất (km)
ROAD_FACTOR = 1.25 # HỆ SỐ ƯỚC TÍNH ĐƯỜNG BỘ: 1.25 x Đường chim bay = Quãng đường thực tế

def haversine(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    lat1, lng1, lat2, lng2 = map(radians, [lat1, lng1, lat2, lng2])
    dlat = lat2 - lat1
    dlng = lng2 - lng1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlng/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    return R_EARTH * c

def find_nearest_node(lat: float, lng: float, df_charge: pd.DataFrame) -> str:
    df = df_charge.copy()
    df = df[df['lat'].notnull() & df['lng'].notnull()]
    df['dist'] = ((df['lat'].astype(float) - lat)**2 + (df['lng'].astype(float) - lng)**2).apply(np.sqrt)
    if df.empty:
        return 'unknown'
    nearest = df.loc[df['dist'].idxmin()]
    return nearest['name'] if 'name' in nearest else 'unknown'

def astar_charging_stations(df_charge: pd.DataFrame, start: str, end: str, battery_max: int, battery_start: int, avoid_toll: bool = False) -> Tuple[List[int], List[Tuple[str, int, int, float, float]], float]:
    import os
    import csv
    start_time = time.time()
    idx_start = df_charge[df_charge['name'] == start].index[0] if not df_charge[df_charge['name'] == start].empty else None
    idx_end = df_charge[df_charge['name'] == end].index[0] if not df_charge[df_charge['name'] == end].empty else None
    if idx_start is None or idx_end is None:
        return None, None, None
    end_lat, end_lng = float(df_charge.loc[idx_end, 'lat']), float(df_charge.loc[idx_end, 'lng'])
    def heuristic(idx: int) -> float:
        lat1, lng1 = float(df_charge.loc[idx, 'lat']), float(df_charge.loc[idx, 'lng'])
        return haversine(lat1, lng1, end_lat, end_lng) * ROAD_FACTOR
    f_start = 0 + heuristic(idx_start)
    initial_log = [(df_charge.loc[idx_start, 'name'], battery_start, 0, float(df_charge.loc[idx_start, 'lat']), float(df_charge.loc[idx_start, 'lng']))]
    heap = [(f_start, 0, idx_start, battery_start, [idx_start], initial_log)]
    visited = dict()
    graph_path = os.path.join(os.path.dirname(__file__), 'graph.csv')
    toll_edges = set()
    if avoid_toll:
        try:
            with open(graph_path, encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row.get('toll') and str(row['toll']).strip() == '1':
                        toll_edges.add((row['from'], row['to']))
        except Exception:
            pass
    while heap:
        if time.time() - start_time > TIMEOUT_SECONDS:
            return None, None, None
        f_score, total_dist, current, battery, path, charge_log = heapq.heappop(heap)
        if (current, battery) in visited and visited[(current, battery)] <= total_dist:
            continue
        visited[(current, battery)] = total_dist
        if current == idx_end:
            return path, charge_log, total_dist
        lat1, lng1 = float(df_charge.loc[current, 'lat']), float(df_charge.loc[current, 'lng'])
        candidates = []
        for next_idx in df_charge.index:
            if next_idx == current:
                continue
            if avoid_toll:
                from_name = df_charge.loc[current, 'name']
                to_name = df_charge.loc[next_idx, 'name']
                if (from_name, to_name) in toll_edges or (to_name, from_name) in toll_edges:
                    continue
            lat2, lng2 = float(df_charge.loc[next_idx, 'lat']), float(df_charge.loc[next_idx, 'lng'])
            dist_km_straight = haversine(lat1, lng1, lat2, lng2)
            dist_km_road = dist_km_straight * ROAD_FACTOR
            if dist_km_road > battery_max:
                continue
            dist_to_end = haversine(lat2, lng2, end_lat, end_lng) * ROAD_FACTOR
            candidates.append((dist_to_end, next_idx, dist_km_road))
        candidates.sort()
        for _, next_idx, dist_km in candidates[:10]:
            battery_after_travel = battery - dist_km
            if battery_after_travel < 0:
                max_charge = int(battery_max * 0.9)
                charge_to = max(max_charge, int(dist_km + 1))
                charge_to = min(charge_to, battery_max)
                charge_amount = charge_to - battery
                new_battery = charge_to - dist_km
                new_charge_log = charge_log + [(df_charge.loc[current, 'name'], new_battery, charge_amount, lat1, lng1)]
            else:
                charge_to = battery
                charge_amount = 0
                new_battery = battery_after_travel
                new_charge_log = charge_log + [(df_charge.loc[current, 'name'], new_battery, charge_amount, lat1, lng1)]
            if new_battery < 0:
                continue
            new_total_dist = total_dist + dist_km
            new_f_score = new_total_dist + heuristic(next_idx)
            heapq.heappush(heap, (new_f_score, new_total_dist, next_idx, new_battery, path + [next_idx], new_charge_log))
    return None, None, None

def run_astar_search(car: Any, lat_start: float, lng_start: float, lat_end: float, lng_end: float, battery_percent: int, qua_tram_thu_phi: bool, df_charge: pd.DataFrame) -> Dict[str, Any]:
    battery_max = car.max_km_per_charge
    start_node = find_nearest_node(lat_start, lng_start, df_charge)
    end_node = find_nearest_node(lat_end, lng_end, df_charge)
    if end_node == 'unknown' or start_node == 'unknown':
        return {"error": "Không tìm thấy trạm sạc gần điểm bắt đầu hoặc kết thúc."}
    info_start_node = df_charge[df_charge['name'] == start_node].iloc[0]
    info_end_node = df_charge[df_charge['name'] == end_node].iloc[0]
    lat_first, lng_first = float(info_start_node['lat']), float(info_start_node['lng'])
    lat_last, lng_last = float(info_end_node['lat']), float(info_end_node['lng'])
    dist_to_first_road = haversine(lat_start, lng_start, lat_first, lng_first) * ROAD_FACTOR
    battery_start_actual = int(battery_max * battery_percent / 100)
    battery_at_first_station = battery_start_actual - dist_to_first_road
    if battery_at_first_station < 0:
        return {"error": f"Không đủ pin ({battery_start_actual:.0f} km) để đi tới trạm sạc đầu tiên ({dist_to_first_road:.0f} km)."}
    path, charge_log, total_dist_stations = astar_charging_stations(df_charge, start_node, end_node, battery_max, battery_at_first_station, avoid_toll=qua_tram_thu_phi)
    if path is None:
        return {"error": "Không tìm được đường đi hợp lệ (Timeout hoặc không có đường giữa các trạm)."}
    dist_to_last_road = haversine(lat_last, lng_last, lat_end, lng_end) * ROAD_FACTOR
    total_dist_full = total_dist_stations + dist_to_first_road + dist_to_last_road
    total_time_sac = 0
    total_fee = 0
    time_to_first_road = (dist_to_first_road / AVG_SPEED_KMH) * 60
    time_to_last_road = (dist_to_last_road / AVG_SPEED_KMH) * 60
    total_time_lai = total_dist_stations / AVG_SPEED_KMH * 60 + time_to_first_road + time_to_last_road
    detailed_path = []
    detailed_path.append({
        'node': "Điểm BẮT ĐẦU",
        'address': f"Di chuyển tới {start_node}",
        'charge_status': f"Pin ban đầu: {battery_start_actual:.0f} km. Pin khi tới: {battery_at_first_station:.0f} km.",
        'time_lai': time_to_first_road,
        'dist_lai': dist_to_first_road
    })
    for idx_log, (node, new_battery, charge_amount, lat, lng) in enumerate(charge_log):
        if idx_log == 0: continue
        info_row = df_charge[df_charge['name'] == node]
        if info_row.empty: continue
        info = info_row.iloc[0]
        prev_log = charge_log[idx_log-1]
        battery_before_charge = prev_log[1] if prev_log[2] == 0 else prev_log[1] - charge_amount
        dist_lai = haversine(prev_log[3], prev_log[4], lat, lng) * ROAD_FACTOR
        percent = int(new_battery / battery_max * 100)
        charge_info = ""
        fee = 0
        if charge_amount > 0:
            charge_time = charge_amount / 2
            if battery_before_charge > battery_max * 0.8:
                if charge_time <= 30:
                    fee = charge_time * 1000
                elif charge_time <= 60:
                    fee = 30 * 1000 + (charge_time - 30) * 2000
                else:
                    fee = 30 * 1000 + 30 * 2000 + (charge_time - 60) * 3000
                total_time_sac += charge_time
                total_fee += fee
                charge_info = f"SẠC {charge_amount:.0f} km. Pin tới: {new_battery:.0f} km ({percent}%). Thời gian sạc: {charge_time:.1f} phút. Phí: {fee:.0f} VND."
            else:
                charge_info = f"SẠC {charge_amount:.0f} km. Pin tới: {new_battery:.0f} km ({percent}%). Miễn phí sạc."
        detailed_path.append({
            'node': info['name'] + (" (TRẠM CUỐI)" if node == end_node else ""),
            'address': info['address'],
            'charge_status': charge_info if charge_amount > 0 else f"Pin còn lại {new_battery:.0f} km ({percent}%) khi tới.",
            'time_lai': (dist_lai / AVG_SPEED_KMH) * 60,
            'dist_lai': dist_lai
        })
    detailed_path.append({
        'node': "Điểm KẾT THÚC",
        'address': f"Di chuyển từ {end_node}",
        'charge_status': f"Di chuyển: {dist_to_last_road:.1f} km. Kết thúc hành trình.",
        'time_lai': time_to_last_road,
        'dist_lai': dist_to_last_road
    })
    return {
        "path": detailed_path,
        "total_dist": total_dist_full,
        "total_time_lai": total_time_lai,
        "total_time_sac": total_time_sac,
        "total_fee": total_fee,
        "qua_tram_thu_phi": qua_tram_thu_phi
    }