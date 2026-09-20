"""
Unit tests for positron emission tomography module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from positron_emission_tomography import (PETEvent, CoincidenceDetector,
                                          SinogramFormer,
                                          PETReconstructor,
                                          TracerUptakeAnalyzer,
                                          PositronEmissionTomography)


class TestCoincidenceDetector(unittest.TestCase):
    """Test detector."""
    
    def setUp(self):
        self.cd = CoincidenceDetector()
    
    def test_detect(self):
        """Should detect coincidences."""
        singles = [
            {"x_mm": -100.0, "y_mm": 0.0, "time_ns": 0.0, "energy_keV": 511.0},
            {"x_mm": 100.0, "y_mm": 0.0, "time_ns": 1.0, "energy_keV": 511.0}
        ]
        e = self.cd.detect(singles)
        self.assertGreater(len(e), 0)
        print(f"  [PASS] Det: {len(e)} events")
    
    def test_count_rate(self):
        """Should compute count rate."""
        singles = [
            {"x_mm": -100.0, "y_mm": 0.0, "time_ns": 0.0, "energy_keV": 511.0},
            {"x_mm": 100.0, "y_mm": 0.0, "time_ns": 1.0, "energy_keV": 511.0}
        ]
        self.cd.detect(singles)
        r = self.cd.count_rate(1.0)
        self.assertGreater(r, 0)
        print(f"  [PASS] Rate: {r:.2f}")


class TestSinogramFormer(unittest.TestCase):
    """Test sinogram."""
    
    def setUp(self):
        self.sf = SinogramFormer()
    
    def test_lor(self):
        """Should compute LOR."""
        e = PETEvent(-100.0, 0.0, 100.0, 0.0, 0.0, 511.0)
        a, d = self.sf.line_of_response(e)
        self.assertAlmostEqual(abs(a), 0.0, places=2)
        print(f"  [PASS] LOR: a={a:.4f}, d={d:.4f}")
    
    def test_form(self):
        """Should form sinogram."""
        events = [PETEvent(-100.0, 0.0, 100.0, 0.0, 0.0, 511.0)]
        s = self.sf.form(events)
        self.assertEqual(len(s), 180)
        print(f"  [PASS] Sino: {len(s)}x{len(s[0])}")


class TestPETReconstructor(unittest.TestCase):
    """Test reconstructor."""
    
    def setUp(self):
        self.pr = PETReconstructor(32)
    
    def test_back_project(self):
        """Should back-project."""
        sino = [[1.0] * 128 for _ in range(180)]
        img = self.pr.simple_back_project(sino, 180, 200.0)
        self.assertEqual(len(img), 32)
        print(f"  [PASS] BP: {len(img)}x{len(img[0])}")


class TestTracerUptakeAnalyzer(unittest.TestCase):
    """Test uptake."""
    
    def setUp(self):
        self.tua = TracerUptakeAnalyzer()
    
    def test_roi(self):
        """Should compute ROI uptake."""
        img = [[1.0, 2.0], [3.0, 4.0]]
        mask = [[True, False], [False, True]]
        u = self.tua.roi_uptake(img, mask)
        self.assertEqual(u, 2.5)
        print(f"  [PASS] ROI: {u}")
    
    def test_suv(self):
        """Should compute SUV."""
        suv = self.tua.suv(100.0, 5.0, 70.0)
        self.assertGreater(suv, 0)
        print(f"  [PASS] SUV: {suv:.4f}")


class TestPositronEmissionTomography(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.pet = PositronEmissionTomography(32)
    
    def test_acquire(self):
        """Should acquire."""
        singles = [
            {"x_mm": -100.0, "y_mm": 0.0, "time_ns": 0.0, "energy_keV": 511.0},
            {"x_mm": 100.0, "y_mm": 0.0, "time_ns": 1.0, "energy_keV": 511.0}
        ]
        self.pet.acquire(singles)
        self.assertGreater(len(self.pet.events), 0)
        print("  [PASS] Acq")
    
    def test_reconstruct(self):
        """Should reconstruct."""
        singles = [
            {"x_mm": -100.0, "y_mm": 0.0, "time_ns": 0.0, "energy_keV": 511.0},
            {"x_mm": 100.0, "y_mm": 0.0, "time_ns": 1.0, "energy_keV": 511.0}
        ]
        self.pet.acquire(singles)
        img = self.pet.reconstruct()
        self.assertEqual(len(img), 32)
        print("  [PASS] Rec")
    
    def test_inspect(self):
        """Should inspect."""
        singles = [
            {"x_mm": -100.0, "y_mm": 0.0, "time_ns": 0.0, "energy_keV": 511.0},
            {"x_mm": 100.0, "y_mm": 0.0, "time_ns": 1.0, "energy_keV": 511.0}
        ]
        self.pet.acquire(singles)
        self.pet.reconstruct()
        r = self.pet.inspect()
        self.assertIn("events", r)
        print(f"  [PASS] Insp: {r}")
    
    def test_summary(self):
        """Should summarize."""
        s = self.pet.pet_summary()
        self.assertIn("image_size", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
