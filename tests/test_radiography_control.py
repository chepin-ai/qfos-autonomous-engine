"""
Unit tests for radiography control module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from radiography_control import (RadiationSource, FilmType,
                                 ExposureParameters, ExposureCalculator,
                                 FilmProcessor, PenetrameterEvaluator,
                                 ScatterControl, RadiographyControl)


class TestExposureCalculator(unittest.TestCase):
    """Test exposure calculator."""
    
    def setUp(self):
        self.ec = ExposureCalculator()
    
    def test_hvl(self):
        """Should compute HVL."""
        hvl = self.ec.half_value_layer(200.0)
        self.assertGreater(hvl, 0)
        print(f"  [PASS] HVL: {hvl:.1f}mm")
    
    def test_exposure(self):
        """Should compute exposure."""
        exp = self.ec.required_exposure(20.0, 200.0, 100.0)
        self.assertGreater(exp, 0)
        print(f"  [PASS] Exp: {exp:.3f}mAs")
    
    def test_unsharpness(self):
        """Should compute Ug."""
        ug = self.ec.geometric_unsharpness(3.0, 50.0, 10.0)
        self.assertGreaterEqual(ug, 0)
        print(f"  [PASS] Ug: {ug:.3f}mm")
    
    def test_time(self):
        """Should compute time."""
        t = self.ec.exposure_time(10.0, 5.0)
        self.assertEqual(t, 2.0)
        print(f"  [PASS] T: {t}s")


class TestFilmProcessor(unittest.TestCase):
    """Test film processor."""
    
    def setUp(self):
        self.fp = FilmProcessor()
    
    def test_density(self):
        """Should compute density."""
        d = self.fp.optical_density(10.0)
        self.assertGreater(d, 0)
        print(f"  [PASS] D: {d:.2f}")
    
    def test_range(self):
        """Should compute range."""
        r = self.fp.density_range(1.0, 100.0)
        self.assertLess(r[0], r[1])
        print(f"  [PASS] Range: {r}")
    
    def test_deviation(self):
        """Should compute deviation."""
        dev = self.fp.process_deviation(3.0, 2.5)
        self.assertAlmostEqual(dev, 0.5)
        print(f"  [PASS] Dev: {dev}")


class TestPenetrameterEvaluator(unittest.TestCase):
    """Test penetrameter evaluator."""
    
    def setUp(self):
        self.pe = PenetrameterEvaluator()
    
    def test_sensitivity(self):
        """Should compute sensitivity."""
        s = self.pe.required_sensitivity(50.0)
        self.assertEqual(s, 1.0)
        print(f"  [PASS] Sens: {s}")
    
    def test_wires(self):
        """Should get wires."""
        w = self.pe.visible_wires(50.0, 3)
        self.assertEqual(len(w), 3)
        print(f"  [PASS] Wires: {w}")
    
    def test_iqi(self):
        """Should get IQI."""
        iqi = self.pe.image_quality_indicator(50.0, 3)
        self.assertIn("IQI", iqi)
        print(f"  [PASS] IQI: {iqi}")


class TestScatterControl(unittest.TestCase):
    """Test scatter control."""
    
    def setUp(self):
        self.sc = ScatterControl()
    
    def test_factor(self):
        """Should compute scatter factor."""
        sf = self.sc.scatter_factor(20.0)
        self.assertGreaterEqual(sf, 1.0)
        print(f"  [PASS] SF: {sf:.3f}")
    
    def test_lead(self):
        """Should compute lead."""
        lead = self.sc.required_lead_screen(200.0, 20.0)
        self.assertEqual(lead, 0.2)
        print(f"  [PASS] Lead: {lead}mm")


class TestRadiographyControl(unittest.TestCase):
    """Test unified radiography control."""
    
    def setUp(self):
        self.rc = RadiographyControl()
    
    def test_plan(self):
        """Should plan exposure."""
        p = self.rc.plan_exposure(20.0, 200.0, 5.0)
        self.assertGreater(p.exposure_time_s, 0)
        print(f"  [PASS] Plan: {p.kVp}kVp {p.mA}s")
    
    def test_evaluate(self):
        """Should evaluate density."""
        p = self.rc.plan_exposure(20.0)
        d = self.rc.evaluate_density(p)
        self.assertIn("optical_density", d)
        print(f"  [PASS] Dens: {d['optical_density']:.2f}")
    
    def test_inspect(self):
        """Should inspect."""
        r = self.rc.run_inspection(20.0, 200.0)
        self.assertIn("density", r)
        print(f"  [PASS] Insp: mAs={r['exposure']['mAs']:.2f}")
    
    def test_summary(self):
        """Should summarize."""
        self.rc.run_inspection(20.0)
        s = self.rc.inspection_summary()
        self.assertIn("inspections", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
