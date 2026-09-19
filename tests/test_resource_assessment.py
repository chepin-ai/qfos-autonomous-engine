"""
Unit tests for resource assessment module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from resource_assessment import GroundPenetratingRadar, RegolithAnalyzer, ResourceMapper


class TestGroundPenetratingRadar(unittest.TestCase):
    """Test GPR."""
    
    def setUp(self):
        self.gpr = GroundPenetratingRadar(frequency_mhz=20.0)
    
    def test_simulate_reading(self):
        """Should simulate reading."""
        reading = self.gpr.simulate_reading(0.0, 0.0, ice_purity=0.8, depth_ice_m=1.0)
        self.assertGreater(reading.dielectric_constant, 3.0)
        print(f"  [PASS] GPR: eps={reading.dielectric_constant}, atten={reading.attenuation_db_m}")
    
    def test_detect_ice(self):
        """Should detect ice."""
        reading = self.gpr.simulate_reading(0.0, 0.0, ice_purity=0.99, depth_ice_m=2.0)
        result = self.gpr.detect_ice(reading)
        self.assertTrue(result["ice_detected"])
        self.assertGreater(result["confidence"], 0.5)
        print(f"  [PASS] Ice detect: {result['ice_detected']}, conf={result['confidence']}")
    
    def test_no_ice(self):
        """Should not detect ice in dry regolith."""
        reading = self.gpr.simulate_reading(0.0, 0.0, ice_purity=0.0)
        result = self.gpr.detect_ice(reading)
        self.assertFalse(result["ice_detected"])
        print("  [PASS] No ice: correct rejection")


class TestRegolithAnalyzer(unittest.TestCase):
    """Test regolith analyzer."""
    
    def setUp(self):
        self.analyzer = RegolithAnalyzer()
    
    def test_analyze_sample(self):
        """Should analyze sample."""
        result = self.analyzer.analyze_sample(sample_mass_kg=10.0, water_content_percent=5.0)
        self.assertGreater(result["extractable_water_kg"], 0.0)
        self.assertGreater(result["extractable_oxygen_kg"], 0.0)
        print(f"  [PASS] Sample: water={result['extractable_water_kg']:.3f}kg, O2={result['extractable_oxygen_kg']:.3f}kg")
    
    def test_water_extraction_rate(self):
        """Should compute extraction rate."""
        rate = self.analyzer.water_extraction_rate(1.0, water_content_percent=3.0)
        self.assertGreater(rate, 0.0)
        print(f"  [PASS] Extraction rate: {rate:.4f} kg/s")


class TestResourceMapper(unittest.TestCase):
    """Test resource mapper."""
    
    def setUp(self):
        self.gpr = GroundPenetratingRadar()
        self.analyzer = RegolithAnalyzer()
        self.mapper = ResourceMapper(self.gpr, self.analyzer)
    
    def test_add_reading(self):
        """Should add reading."""
        reading = self.gpr.simulate_reading(0.0, 0.0, ice_purity=0.9)
        self.mapper.add_reading(reading)
        self.assertEqual(len(self.mapper.readings), 1)
        print("  [PASS] Reading added")
    
    def test_identify_deposits(self):
        """Should identify deposits."""
        for i in range(3):
            reading = self.gpr.simulate_reading(float(i), 0.0, ice_purity=0.99, depth_ice_m=1.0)
            self.mapper.add_reading(reading)
        
        deposits = self.mapper.identify_deposits(min_confidence=0.5)
        self.assertGreater(len(deposits), 0)
        print(f"  [PASS] Deposits: {len(deposits)} found")
    
    def test_resource_summary(self):
        """Should summarize resources."""
        reading = self.gpr.simulate_reading(0.0, 0.0, ice_purity=0.9)
        self.mapper.add_reading(reading)
        self.mapper.identify_deposits()
        
        summary = self.mapper.resource_summary()
        self.assertIn("num_deposits", summary)
        print(f"  [PASS] Summary: {summary['num_deposits']} deposits, {summary['total_extractable_water_kg']:.1f}kg water")


if __name__ == '__main__':
    unittest.main(verbosity=2)
