import pandas as pd
import numpy as np
import heapq
import time
from math import radians, sin, cos, sqrt, atan2
from typing import Optional, List, Tuple, Dict, Any

# --- CẤU HÌNH ---
TIMEOUT_SECONDS = 60 # Giới hạn thời gian tìm kiếm
AVG_SPEED_KMH = 60 # Tốc độ di chuyển trung bình (dùng để tính thời gian lái xe)
R_EARTH = 6371.0 # Bán kính Trái Đất (km)
ROAD_FACTOR = 1.25 # HỆ SỐ ƯỚC TÍNH ĐƯỜNG BỘ: 1.25 x Đường chim bay = Quãng đường thực tế

# ======================= #
# 1. HÀM TÍNH TOÁN KHOẢNG CÁCH VÀ TÌM TRẠM GẦN NHẤT
# ======================= #

def haversine(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Tính khoảng cách Haversine (Đường chim bay) giữa hai điểm (km)"""
    lat1, lng1, lat2, lng2 = map(radians, [lat1, lng1, lat2, lng2])
    dlat = lat2 - lat1
    dlng = lng2 - lng1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlng/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    return R_EARTH * c

def find_nearest_node(lat: float, lng: float, df_charge: pd.DataFrame) -> str:
    """Tìm trạm sạc gần nhất (dùng khoảng cách Euclidean để tăng tốc độ)"""
    df = df_charge.copy()
    df = df[df['lat'].notnull() & df['lng'].notnull()]
    df['dist'] = ((df['lat'].astype(float) - lat)**2 + (df['lng'].astype(float) - lng)**2).apply(np.sqrt)
    
    if df.empty:
        return 'unknown'
        
    nearest = df.loc[df['dist'].idxmin()]
    return nearest['name'] if 'name' in nearest else 'unknown'

# ======================= #
# 2. THUẬT TOÁN A* TÌM ĐƯỜNG
# ======================= #

def astar_charging_stations(df_charge: pd.DataFrame, start: str, end: str, battery_max: int, battery_start: int, avoid_toll: bool = False) -> Tuple[Optional[List[int]], Optional[List[Tuple[str, int, int, float, float]]], Optional[float]]:
    """
    Thuật toán A* tìm đường đi qua các trạm sạc.
    Lưu ý: dist_km_straight (Haversine) * ROAD_FACTOR được dùng để tính g_score (total_dist) và tiêu thụ pin.
    """
    start_time = time.time()
    
    # 1. Khởi tạo Index
    idx_start = df_charge[df_charge['name'] == start].index[0] if not df_charge[df_charge['name'] == start].empty else None
    idx_end = df_charge[df_charge['name'] == end].index[0] if not df_charge[df_charge['name'] == end].empty else None

    if idx_start is None or idx_end is None:
        return None, None, None

    end_lat, end_lng = float(df_charge.loc[idx_end, 'lat']), float(df_charge.loc[idx_end, 'lng'])
    
    def heuristic(idx: int) -> float:
        """Ước tính khoảng cách Haversine * ROAD_FACTOR (f_score)"""
        lat1, lng1 = float(df_charge.loc[idx, 'lat']), float(df_charge.loc[idx, 'lng'])
        # Heuristic phải là Haversine * ROAD_FACTOR
        return haversine(lat1, lng1, end_lat, end_lng) * ROAD_FACTOR

    # Heap: (f_score, total_dist, current_idx, battery, path, charge_log)
    f_start = 0 + heuristic(idx_start)
    
    # Khởi tạo log (Pin còn lại khi đến trạm start - sau khi đi từ điểm START thực tế)
    # Chúng ta sẽ xử lý chặng Start -> Trạm đầu tiên ở hàm run_astar_search (Hậu xử lý)
    initial_log = [(df_charge.loc[idx_start, 'name'], battery_start, 0, float(df_charge.loc[idx_start, 'lat']), float(df_charge.loc[idx_start, 'lng']))]
    heap = [(f_start, 0, idx_start, battery_start, [idx_start], initial_log)]
    
    # visited: (idx, battery) -> total_dist (g_score)
    visited = dict() 

    # Đọc dữ liệu graph.csv để lấy thông tin trạm thu phí
    import os
    import csv
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
            return None, None, None # Timeout

        f_score, total_dist, current, battery, path, charge_log = heapq.heappop(heap)
        
        # Kiểm tra state đã thăm
        if (current, battery) in visited and visited[(current, battery)] <= total_dist:
            continue
        visited[(current, battery)] = total_dist

        if current == idx_end:
            return path, charge_log, total_dist # total_dist chỉ tính giữa các trạm

        lat1, lng1 = float(df_charge.loc[current, 'lat']), float(df_charge.loc[current, 'lng'])
        
        candidates = []
        for next_idx in df_charge.index:
            if next_idx == current:
                continue
            # Kiểm tra nếu cần tránh trạm thu phí
            if avoid_toll:
                from_name = df_charge.loc[current, 'name']
                to_name = df_charge.loc[next_idx, 'name']
                if (from_name, to_name) in toll_edges or (to_name, from_name) in toll_edges:
                    continue
            lat2, lng2 = float(df_charge.loc[next_idx, 'lat']), float(df_charge.loc[next_idx, 'lng'])
            # Tính khoảng cách đường chim bay
            dist_km_straight = haversine(lat1, lng1, lat2, lng2)
            # ƯỚC TÍNH khoảng cách đường bộ (dùng cho tiêu thụ pin và total_dist)
            dist_km_road = dist_km_straight * ROAD_FACTOR
            if dist_km_road > battery_max:
                continue
            dist_to_end = haversine(lat2, lng2, end_lat, end_lng) * ROAD_FACTOR
            candidates.append((dist_to_end, next_idx, dist_km_road))

        candidates.sort()

        # Chỉ xét tối đa 10 trạm gần nhất (tham lam A*)
        for _, next_idx, dist_km in candidates[:10]:
            
            # --- Logic Sạc Pin ---
            
            battery_after_travel = battery - dist_km # Dùng dist_km_road
            
            if battery_after_travel < 0:
                # PHẢI SẠC
                max_charge = int(battery_max * 0.9) 
                charge_to = max(max_charge, int(dist_km + 1)) 
                charge_to = min(charge_to, battery_max) 
                
                charge_amount = charge_to - battery
                new_battery = charge_to - dist_km
                
                new_charge_log = charge_log + [(df_charge.loc[current, 'name'], new_battery, charge_amount, lat1, lng1)]
            
            else:
                # KHÔNG SẠC
                charge_to = battery
                charge_amount = 0
                new_battery = battery_after_travel
                
                new_charge_log = charge_log + [(df_charge.loc[current, 'name'], new_battery, charge_amount, lat1, lng1)]

            if new_battery < 0:
                continue
            
            # Thêm vào heap (A*): f_score = total_dist + dist_km + heuristic(next_idx)
            new_total_dist = total_dist + dist_km # Dùng dist_km_road
            new_f_score = new_total_dist + heuristic(next_idx)
            
            # Chỉ ghi lại trạng thái của trạm kế tiếp
            heapq.heappush(heap, (new_f_score, new_total_dist, next_idx, new_battery, path + [next_idx], new_charge_log))
            
    return None, None, None

# ======================= #
# 3. HÀM CHÍNH (DÙNG CHO GUI)
# ======================= #

def run_astar_search(car: Any, lat_start: float, lng_start: float, lat_end: float, lng_end: float, battery_percent: int, qua_tram_thu_phi: bool, df_charge: pd.DataFrame) -> Dict[str, Any]:
    """
    Hàm entry point chính cho thuật toán A* (Dùng cho GUI).
    """
    
    # 1. Tiền xử lý
    battery_max = car.max_km_per_charge
    start_node = find_nearest_node(lat_start, lng_start, df_charge)
    end_node = find_nearest_node(lat_end, lng_end, df_charge)

    if end_node == 'unknown' or start_node == 'unknown':
        return {"error": "Không tìm thấy trạm sạc gần điểm bắt đầu hoặc kết thúc."}

    info_start_node = df_charge[df_charge['name'] == start_node].iloc[0]
    info_end_node = df_charge[df_charge['name'] == end_node].iloc[0]
    lat_first, lng_first = float(info_start_node['lat']), float(info_start_node['lng'])
    lat_last, lng_last = float(info_end_node['lat']), float(info_end_node['lng'])
    
    # Tính quãng đường START -> TRẠM ĐẦU
    dist_to_first_road = haversine(lat_start, lng_start, lat_first, lng_first) * ROAD_FACTOR
    
    # Pin còn lại khi tới trạm đầu tiên
    battery_start_actual = int(battery_max * battery_percent / 100)
    battery_at_first_station = battery_start_actual - dist_to_first_road
    
    if battery_at_first_station < 0:
        return {"error": f"Không đủ pin ({battery_start_actual:.0f} km) để đi tới trạm sạc đầu tiên ({dist_to_first_road:.0f} km)."}
    
    # 2. Chạy Thuật toán A*
    # total_dist_stations là tổng quãng đường giữa các trạm (đã nhân ROAD_FACTOR)
    path, charge_log, total_dist_stations = astar_charging_stations(df_charge, start_node, end_node, battery_max, battery_at_first_station, avoid_toll=qua_tram_thu_phi)

    if path is None:
        return {"error": "Không tìm được đường đi hợp lệ (Timeout hoặc không có đường giữa các trạm)."}

    # 3. Hậu xử lý và Tổng kết
    
    # Tính quãng đường TRẠM CUỐI -> END
    dist_to_last_road = haversine(lat_last, lng_last, lat_end, lng_end) * ROAD_FACTOR
    
    # Tổng quãng đường toàn bộ hành trình
    total_dist_full = total_dist_stations + dist_to_first_road + dist_to_last_road

    # Tính toán chi phí và thời gian
    total_time_sac = 0
    total_fee = 0
    
    # Thời gian lái xe đã bao gồm chặng Start -> Trạm đầu và Trạm cuối -> End
    time_to_first_road = (dist_to_first_road / AVG_SPEED_KMH) * 60
    time_to_last_road = (dist_to_last_road / AVG_SPEED_KMH) * 60
    
    total_time_lai = total_dist_stations / AVG_SPEED_KMH * 60 + time_to_first_road + time_to_last_road
    
    
    # --- Chuẩn bị chi tiết lộ trình ---
    detailed_path = []
    
    # A. CHẶNG 1: START -> TRẠM ĐẦU TIÊN
    detailed_path.append({
        'node': "Điểm BẮT ĐẦU",
        'address': f"Di chuyển tới {start_node}",
        'charge_status': f"Pin ban đầu: {battery_start_actual:.0f} km. Pin khi tới: {battery_at_first_station:.0f} km.",
        'time_lai': time_to_first_road,
        'dist_lai': dist_to_first_road
    })

    # B. CHẶNG 2: GIỮA CÁC TRẠM (Từ log A*)
    # charge_log đã bao gồm cả điểm start_node, chúng ta sẽ loại bỏ entry đầu tiên vì nó chỉ là pin ban đầu
    for idx_log, (node, new_battery, charge_amount, lat, lng) in enumerate(charge_log):
        # Bỏ qua entry đầu tiên (đã xử lý ở A)
        if idx_log == 0: continue
            
        info_row = df_charge[df_charge['name'] == node]
        if info_row.empty: continue
        info = info_row.iloc[0]
        
        # Lấy pin trước khi đến trạm hiện tại (lấy từ log trước đó)
        prev_log = charge_log[idx_log-1]
        battery_before_charge = prev_log[1] if prev_log[2] == 0 else prev_log[1] - charge_amount
        
        # Khoảng cách giữa trạm trước và trạm này (đã có trong thuật toán)
        dist_lai = haversine(prev_log[3], prev_log[4], lat, lng) * ROAD_FACTOR
        
        percent = int(new_battery / battery_max * 100)
        
        charge_info = ""
        fee = 0
        
        if charge_amount > 0:
            charge_time = charge_amount / 2  # Giả sử tốc độ sạc là 2 km/phút
            
            if battery_before_charge > battery_max * 0.8: # Phí cao hơn
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

    # C. CHẶNG 3: TRẠM CUỐI -> ĐIỂM END
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

if __name__ == "__main__":
    pass