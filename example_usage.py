#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Example script demonstrating how to use the routing algorithms programmatically.
This can be used for testing or integrating the algorithms into other applications.
"""

import pandas as pd
from models import cars
from file import run_astar_search, run_ucs_search


def example_basic_search():
    """Example: Basic route search using A* algorithm"""
    print("=" * 60)
    print("VÍ DỤ 1: Tìm lộ trình cơ bản với thuật toán A*")
    print("=" * 60)
    
    # Load charging stations data
    df_charge = pd.read_csv('charging_stations.csv')
    
    # Select a car (VinFast VF8)
    car = cars[1]  # VinFast VF8
    print(f"\nXe được chọn: {car.name}")
    print(f"Pin: {car.battery_capacity} kWh")
    print(f"Quãng đường tối đa: {car.max_km_per_charge} km")
    
    # Define route
    start_lat, start_lng = 20.825, 105.351  # Near Hòa Bình
    end_lat, end_lng = 10.771, 106.701      # Near HCM
    battery_percent = 80  # Start with 80% battery
    avoid_toll = False    # Don't avoid toll stations
    
    print(f"\nĐiểm bắt đầu: ({start_lat}, {start_lng})")
    print(f"Điểm kết thúc: ({end_lat}, {end_lng})")
    print(f"Pin ban đầu: {battery_percent}%")
    
    # Run A* search
    print("\nĐang tìm kiếm lộ trình...")
    result = run_astar_search(
        car, start_lat, start_lng, end_lat, end_lng,
        battery_percent, avoid_toll, df_charge
    )
    
    # Display results
    if "error" in result:
        print(f"\nLỖI: {result['error']}")
    else:
        print(f"\n✓ Tìm thấy lộ trình!")
        print(f"  - Tổng quãng đường: {result['total_dist']:.2f} km")
        print(f"  - Tổng thời gian lái: {result['total_time_lai']:.0f} phút ({result['total_time_lai']/60:.1f} giờ)")
        print(f"  - Tổng thời gian sạc: {result['total_time_sac']:.0f} phút ({result['total_time_sac']/60:.1f} giờ)")
        print(f"  - Tổng chi phí sạc: {result['total_fee']:.0f} VND")
        print(f"  - Số trạm sạc: {len(result['path']) - 2}")  # Exclude start and end


def example_compare_algorithms():
    """Example: Compare A* and UCS algorithms"""
    print("\n" + "=" * 60)
    print("VÍ DỤ 2: So sánh thuật toán A* và UCS")
    print("=" * 60)
    
    # Load charging stations data
    df_charge = pd.read_csv('charging_stations.csv')
    
    # Select a car
    car = cars[0]  # VinFast VF e34
    
    # Define a shorter route for comparison
    start_lat, start_lng = 20.825, 105.351
    end_lat, end_lng = 20.734567, 105.267891
    battery_percent = 70
    avoid_toll = False
    
    print(f"\nXe: {car.name} | Pin: {battery_percent}%")
    print(f"Lộ trình: ({start_lat}, {start_lng}) → ({end_lat}, {end_lng})")
    
    # Run A*
    print("\n--- Thuật toán A* ---")
    import time
    start_time = time.time()
    result_astar = run_astar_search(
        car, start_lat, start_lng, end_lat, end_lng,
        battery_percent, avoid_toll, df_charge
    )
    astar_time = time.time() - start_time
    
    if "error" not in result_astar:
        print(f"  Thời gian xử lý: {astar_time:.3f} giây")
        print(f"  Quãng đường: {result_astar['total_dist']:.2f} km")
        print(f"  Chi phí sạc: {result_astar['total_fee']:.0f} VND")
    else:
        print(f"  Lỗi: {result_astar['error']}")
    
    # Run UCS
    print("\n--- Thuật toán UCS ---")
    start_time = time.time()
    result_ucs = run_ucs_search(
        car, start_lat, start_lng, end_lat, end_lng,
        battery_percent, avoid_toll, df_charge
    )
    ucs_time = time.time() - start_time
    
    if "error" not in result_ucs:
        print(f"  Thời gian xử lý: {ucs_time:.3f} giây")
        print(f"  Quãng đường: {result_ucs['total_dist']:.2f} km")
        print(f"  Chi phí sạc: {result_ucs['total_fee']:.0f} VND")
    else:
        print(f"  Lỗi: {result_ucs['error']}")


def example_avoid_toll():
    """Example: Find route while avoiding toll stations"""
    print("\n" + "=" * 60)
    print("VÍ DỤ 3: Tìm lộ trình tránh trạm BOT")
    print("=" * 60)
    
    # Load charging stations data
    df_charge = pd.read_csv('charging_stations.csv')
    
    # Select a car
    car = cars[2]  # VinFast VF9
    start_lat, start_lng = 20.825, 105.351
    end_lat, end_lng = 20.5, 105.5
    battery_percent = 90
    
    print(f"\nXe: {car.name}")
    
    # Without avoiding toll
    print("\n--- Không tránh trạm BOT ---")
    result_no_avoid = run_astar_search(
        car, start_lat, start_lng, end_lat, end_lng,
        battery_percent, False, df_charge
    )
    
    if "error" not in result_no_avoid:
        print(f"  Quãng đường: {result_no_avoid['total_dist']:.2f} km")
        print(f"  Số trạm sạc: {len(result_no_avoid['path']) - 2}")
    
    # With avoiding toll
    print("\n--- Có tránh trạm BOT ---")
    result_avoid = run_astar_search(
        car, start_lat, start_lng, end_lat, end_lng,
        battery_percent, True, df_charge
    )
    
    if "error" not in result_avoid:
        print(f"  Quãng đường: {result_avoid['total_dist']:.2f} km")
        print(f"  Số trạm sạc: {len(result_avoid['path']) - 2}")


def example_all_cars():
    """Example: Test route planning with different car models"""
    print("\n" + "=" * 60)
    print("VÍ DỤ 4: So sánh các mẫu xe khác nhau")
    print("=" * 60)
    
    # Load charging stations data
    df_charge = pd.read_csv('charging_stations.csv')
    
    # Define route
    start_lat, start_lng = 20.825, 105.351
    end_lat, end_lng = 20.6, 105.6
    battery_percent = 80
    avoid_toll = False
    
    print(f"\nLộ trình cố định: ({start_lat}, {start_lng}) → ({end_lat}, {end_lng})")
    print(f"Pin ban đầu: {battery_percent}%\n")
    
    # Test first 5 cars
    for i, car in enumerate(cars[:5], 1):
        print(f"{i}. {car.name} ({car.battery_capacity} kWh, {car.max_km_per_charge} km)")
        result = run_astar_search(
            car, start_lat, start_lng, end_lat, end_lng,
            battery_percent, avoid_toll, df_charge
        )
        
        if "error" not in result:
            print(f"   → Quãng đường: {result['total_dist']:.2f} km")
            print(f"   → Số lần sạc: {sum(1 for step in result['path'] if step.get('charge_status', '').startswith('SẠC'))}")
            print(f"   → Chi phí: {result['total_fee']:.0f} VND")
        else:
            print(f"   → {result['error']}")
        print()


if __name__ == "__main__":
    print("CHƯƠNG TRÌNH VÍ DỤ SỬ DỤNG THUẬT TOÁN TÌM ĐƯỜNG")
    print("=" * 60)
    
    try:
        # Run examples
        example_basic_search()
        example_compare_algorithms()
        example_avoid_toll()
        example_all_cars()
        
        print("\n" + "=" * 60)
        print("✓ Hoàn thành tất cả ví dụ!")
        print("=" * 60)
        
    except FileNotFoundError as e:
        print(f"\nLỖI: Không tìm thấy file dữ liệu: {e}")
        print("Vui lòng đảm bảo file 'charging_stations.csv' tồn tại trong thư mục hiện tại.")
    except Exception as e:
        print(f"\nLỖI: {e}")
        import traceback
        traceback.print_exc()
