import unittest
from models import ElectricCar

class TestElectricCar(unittest.TestCase):
    def test_tinh_tieu_thu(self):
        # 40 kWh / 200 km = 0.2 kWh/km
        xe = ElectricCar("Test", 200, 40, 100, 150, 2023) 
        self.assertAlmostEqual(xe.tinh_tieu_thu(), 0.2)

    def test_tinh_tieu_thu_zero(self):
        xe = ElectricCar("Zero Range", 0, 40, 100, 150, 2023)
        self.assertEqual(xe.tinh_tieu_thu(), 0.0) # Tránh lỗi chia cho 0

if __name__ == "__main__":
    unittest.main()