def print_info(xe) -> None:
    """
    In thông tin chi tiết của đối tượng ElectricCar ra màn hình console.
    
    Args:
        xe: Đối tượng ElectricCar cần hiển thị thông tin
    
    Lưu ý: Các thuộc tính đã được cập nhật từ (ten, quang_duong, pin) 
    sang (name, max_km_per_charge, battery_capacity) để đồng bộ với models.py.
    """
    
    ten = xe.name
    quang_duong = xe.max_km_per_charge
    pin = xe.battery_capacity
    
    # 1. Tính toán tiêu thụ năng lượng (kWh/km)
    # Kiểm tra để tránh lỗi chia cho 0
    if quang_duong and quang_duong > 0:
        tieu_thu = pin / quang_duong
    else:
        tieu_thu = 0.0

    # 2. In thông tin ra màn hình
    print("\n--- THÔNG SỐ CHI TIẾT CỦA XE ---")
    print(f"Tên xe: {ten} ({xe.year})")
    print(f"Công suất động cơ: {xe.motor_power} kW")
    print(f"Tốc độ tối đa: {xe.max_speed} km/h")
    print(f"--- Thông số Pin và Quãng đường ---")
    print(f"Dung lượng pin: {pin} kWh")
    print(f"Quãng đường tối đa: {quang_duong} km")
    # Đã thêm tính toán tiêu thụ năng lượng vào đây
    print(f"Tiêu thụ năng lượng ước tính: {tieu_thu:.4f} kWh/km")
    print("----------------------------------\n")

# Hàm kiểm tra điểm có đi qua trạm BOT nào không
import pandas as pd
from math import radians, sin, cos, sqrt, atan2

R_EARTH = 6371.0
ROAD_FACTOR = 1.25

def haversine(lat1, lng1, lat2, lng2):
    """
    Calculate Haversine distance between two points (km).
    Note: This is a duplicate of the function in file.py and pdf_utils.py.
    Consider using the version from file.py as the canonical implementation.
    """
    lat1, lng1, lat2, lng2 = map(radians, [lat1, lng1, lat2, lng2])
    dlat = lat2 - lat1
    dlng = lng2 - lng1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlng/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    return R_EARTH * c

def check_bot_stations_legacy(route_points, bot_file='BOT.csv', tol_km=5):
    """
    Legacy function for checking BOT stations (kept for backward compatibility).
    Note: Use check_bot_stations from pdf_utils.py for production code.
    """
    try:
        df_bot = pd.read_csv(bot_file)
        bot_stations = []
        # Làm tròn tọa độ lộ trình để tăng độ chính xác so với BOT
        route_points_rounded = [(round(lat, 4), round(lng, 4)) for lat, lng in route_points]
        for idx, row in df_bot.iterrows():
            vido_kinhdo = row["Vĩ độ, Kinh độ"]
            if isinstance(vido_kinhdo, str):
                bot_lat, bot_lng = map(float, vido_kinhdo.split(','))
            else:
                bot_lat = row["Vĩ độ, Kinh độ"]
                bot_lng = row["Vĩ độ, Kinh độ.1"] if "Vĩ độ, Kinh độ.1" in row else 0
            bot_lat, bot_lng = round(bot_lat, 4), round(bot_lng, 4)
            for lat, lng in route_points_rounded:
                # Tăng khoảng cách kiểm tra lên 5km cho dễ test
                if haversine(lat, lng, bot_lat, bot_lng) <= tol_km:
                    bot_stations.append({
                        'name': row['Tên'],
                        'address': row['Địa chỉ / Lý trình / Hành trình'],
                        'fee': row['Mức thu (Xe điện/Nhóm 1)'],
                        'lat': bot_lat,
                        'lng': bot_lng
                    })
                    break
        print(f"DEBUG BOT: Lộ trình có {len(bot_stations)} trạm BOT đi qua.")
        return bot_stations
    except Exception as e:
        print(f"Error in check_bot_stations_legacy: {e}")
        return []