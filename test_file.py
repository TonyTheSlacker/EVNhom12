import unittest
from models import ElectricCar, cars
from file import haversine, find_nearest_node
import pandas as pd


class TestElectricCar(unittest.TestCase):
    def test_tinh_tieu_thu(self):
        # 40 kWh / 200 km = 0.2 kWh/km
        xe = ElectricCar("Test", 200, 40, 100, 150, 2023) 
        self.assertAlmostEqual(xe.tinh_tieu_thu(), 0.2)

    def test_tinh_tieu_thu_zero(self):
        xe = ElectricCar("Zero Range", 0, 40, 100, 150, 2023)
        self.assertEqual(xe.tinh_tieu_thu(), 0.0) # Tránh lỗi chia cho 0
    
    def test_car_attributes(self):
        """Test that car has all required attributes"""
        xe = ElectricCar("Test Car", 300, 60, 150, 180, 2023)
        self.assertEqual(xe.name, "Test Car")
        self.assertEqual(xe.max_km_per_charge, 300)
        self.assertEqual(xe.battery_capacity, 60)
        self.assertEqual(xe.motor_power, 150)
        self.assertEqual(xe.max_speed, 180)
        self.assertEqual(xe.year, 2023)
    
    def test_cars_list_not_empty(self):
        """Test that the cars list is not empty"""
        self.assertGreater(len(cars), 0)
    
    def test_all_cars_have_valid_consumption(self):
        """Test that all cars in the list have valid consumption"""
        for car in cars:
            consumption = car.tinh_tieu_thu()
            self.assertGreaterEqual(consumption, 0)
            self.assertLess(consumption, 1)  # Reasonable upper bound


class TestHaversine(unittest.TestCase):
    def test_haversine_same_point(self):
        """Test haversine distance between same point is 0"""
        dist = haversine(21.0285, 105.854, 21.0285, 105.854)
        self.assertAlmostEqual(dist, 0.0, places=5)
    
    def test_haversine_hanoi_hcm(self):
        """Test haversine distance between Hanoi and HCM (approximately 1160km)"""
        # Hanoi: 21.0285, 105.854
        # HCM: 10.771, 106.701
        dist = haversine(21.0285, 105.854, 10.771, 106.701)
        # Expected distance is approximately 1160 km
        self.assertGreater(dist, 1100)
        self.assertLess(dist, 1200)
    
    def test_haversine_returns_positive(self):
        """Test that haversine always returns positive distance"""
        dist1 = haversine(21.0, 105.0, 10.0, 106.0)
        dist2 = haversine(10.0, 106.0, 21.0, 105.0)
        self.assertGreater(dist1, 0)
        self.assertAlmostEqual(dist1, dist2, places=5)
    
    def test_haversine_invalid_latitude(self):
        """Test that haversine raises ValueError for invalid latitude"""
        with self.assertRaises(ValueError):
            haversine(91.0, 105.0, 10.0, 106.0)  # lat > 90
        with self.assertRaises(ValueError):
            haversine(21.0, 105.0, -91.0, 106.0)  # lat < -90
    
    def test_haversine_invalid_longitude(self):
        """Test that haversine raises ValueError for invalid longitude"""
        with self.assertRaises(ValueError):
            haversine(21.0, 181.0, 10.0, 106.0)  # lng > 180
        with self.assertRaises(ValueError):
            haversine(21.0, 105.0, 10.0, -181.0)  # lng < -180


class TestFindNearestNode(unittest.TestCase):
    def setUp(self):
        """Create sample charging station data for testing"""
        self.df_charge = pd.DataFrame({
            'name': ['Station A', 'Station B', 'Station C'],
            'address': ['Address A', 'Address B', 'Address C'],
            'lat': [21.0, 20.5, 20.0],
            'lng': [105.0, 105.5, 106.0]
        })
    
    def test_find_nearest_node_exact_match(self):
        """Test finding nearest node when coordinates match exactly"""
        nearest = find_nearest_node(21.0, 105.0, self.df_charge)
        self.assertEqual(nearest, 'Station A')
    
    def test_find_nearest_node_approximate(self):
        """Test finding nearest node with approximate coordinates"""
        nearest = find_nearest_node(20.1, 106.1, self.df_charge)
        self.assertEqual(nearest, 'Station C')
    
    def test_find_nearest_node_empty_dataframe(self):
        """Test behavior with empty dataframe"""
        df_empty = pd.DataFrame(columns=['name', 'address', 'lat', 'lng'])
        nearest = find_nearest_node(21.0, 105.0, df_empty)
        self.assertEqual(nearest, 'unknown')


if __name__ == "__main__":
    unittest.main()