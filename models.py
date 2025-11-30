class ElectricCar:
    def __init__(self, name, max_km_per_charge, battery_capacity, motor_power, max_speed, year):
        self.name = name
        self.max_km_per_charge = max_km_per_charge
        self.battery_capacity = battery_capacity
        self.motor_power = motor_power
        self.max_speed = max_speed
        self.year = year

    def tinh_tieu_thu(self):
        """Tính toán tiêu thụ năng lượng (kWh/km)"""
        if self.max_km_per_charge > 0:
            return self.battery_capacity / self.max_km_per_charge
        return 0.0

    def __str__(self):
        return (f"Tên xe: {self.name} ({self.year}) | Pin: {self.battery_capacity} kWh | "
                f"Quãng đường/lần sạc: {self.max_km_per_charge} km | "
                f"Công suất: {self.motor_power} kW | Tốc độ tối đa: {self.max_speed} km/h")

# Danh sách xe (giữ nguyên)
cars = [
    # VinFast
    ElectricCar("VinFast VF e34", 285, 42, 110, 130, 2022),
    ElectricCar("VinFast VF8", 400, 87.7, 260, 200, 2023),
    ElectricCar("VinFast VF9", 423, 92, 300, 201, 2023),
    ElectricCar("VinFast VF5", 300, 37.23, 70, 130, 2023),
    ElectricCar("VinFast VF6", 399, 59.6, 150, 150, 2023),
    # Tesla
    ElectricCar("Tesla Model S", 652, 100, 615, 250, 2022),
    ElectricCar("Tesla Model 3", 614, 82, 340, 233, 2022),
    ElectricCar("Tesla Model X", 560, 100, 311, 250, 2022),
    ElectricCar("Tesla Model Y", 533, 75, 258, 217, 2022),
    # BMW
    ElectricCar("BMW i4", 590, 80.7, 250, 190, 2022),
    ElectricCar("BMW iX3", 460, 80, 210, 180, 2022),
    ElectricCar("BMW iX", 630, 111.5, 385, 200, 2022),
    # Audi
    ElectricCar("Audi e-tron GT", 488, 93.4, 350, 245, 2021),
    ElectricCar("Audi Q4 e-tron", 520, 82, 150, 180, 2022),
    ElectricCar("Audi Q8 e-tron", 582, 114, 300, 200, 2023),
    # BYD
    ElectricCar("BYD Atto 3", 420, 60.5, 150, 160, 2022),
    ElectricCar("BYD Han EV", 605, 76.9, 180, 185, 2022),
    ElectricCar("BYD Tang EV", 505, 86.4, 380, 180, 2022),
    # Mercedes-Benz
    ElectricCar("Mercedes EQS 450+", 770, 107.8, 245, 210, 2022),
    ElectricCar("Mercedes EQB 300", 419, 66.5, 168, 160, 2022),
    ElectricCar("Mercedes EQC 400", 417, 80, 300, 180, 2022),
    # Porsche
    ElectricCar("Porsche Taycan 4S", 463, 93.4, 390, 250, 2022),
    ElectricCar("Porsche Taycan Turbo S", 412, 93.4, 560, 260, 2022),
    # Hyundai
    ElectricCar("Hyundai Ioniq 5", 481, 77.4, 225, 185, 2022),
    ElectricCar("Hyundai Kona Electric", 484, 64, 150, 167, 2022),
    # Kia
    ElectricCar("Kia EV6", 528, 77.4, 239, 185, 2022),
    ElectricCar("Kia Niro EV", 455, 64.8, 150, 167, 2022),
    # Nissan
    ElectricCar("Nissan Leaf", 385, 62, 160, 144, 2022),
    # MG
    ElectricCar("MG ZS EV", 440, 50.3, 143, 140, 2022),
    # Toyota
    ElectricCar("Toyota bZ4X", 500, 71.4, 150, 160, 2022),
    # Volkswagen
    ElectricCar("Volkswagen ID.4", 522, 77, 204, 160, 2022),
    ElectricCar("Volkswagen ID.3", 550, 77, 204, 160, 2022)
]

# Hàm console cho select_car và show_cars
def show_cars():
    print("\nDanh sách các mẫu xe điện:")
    for idx, car in enumerate(cars):
        print(f"[{idx+1}] {car}")

def select_car():
    show_cars()
    while True:
        print("\nChọn số thứ tự xe bạn muốn sử dụng: ", end="") 
        try:
            user_input = input().strip()
            if not user_input:
                print("Vui lòng nhập số.")
                continue

            idx = int(user_input) - 1
            if 0 <= idx < len(cars):
                return cars[idx]
            else:
                print(f"Số thứ tự không hợp lệ, hãy chọn trong khoảng 1 đến {len(cars)}.")
        except ValueError:
            print("Lỗi: Vui lòng nhập SỐ nguyên hợp lệ.")
        except Exception:
            print("Đã xảy ra lỗi không xác định.")