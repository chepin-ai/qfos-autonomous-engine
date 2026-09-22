"""
Unit tests for corrosion modeling module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from corrosion_modeling import (ElectrochemicalParameters, ElectrochemicalCorrosion,
                                PolarizationCurves,
                                CorrosionRatePrediction,
                                ProtectionDesign,
                                CorrosionModeling)


class TestElectrochemicalCorrosion(unittest.TestCase):
    """Test electrochemical."""
    
    def setUp(self):
        self.ec = ElectrochemicalCorrosion()
    
    def test_tafel(self):
        """Should compute Tafel."""
        i = self.ec.tafel_equation(-0.5, -0.6, 1e-6, 0.12)
        self.assertGreater(i, 1e-6)
        print(f"  [PASS] Tafel: {i:.2e}")
    
    def test_butler(self):
        """Should compute Butler-Volmer."""
        i = self.ec.butler_volmer(-0.5, -0.6, 1e-6, 0.12, 0.12)
        self.assertGreater(i, 0)
        print(f"  [PASS] BV: {i:.2e}")
    
    def test_est(self):
        """Should estimate E_corr."""
        e = self.ec.corrosion_potential_estimate(-0.4, 1e-4, -0.7, 1e-5)
        self.assertLess(e, -0.4)
        print(f"  [PASS] Est: {e:.3f}")


class TestPolarizationCurves(unittest.TestCase):
    """Test polarization."""
    
    def setUp(self):
        self.pc = PolarizationCurves()
    
    def test_anodic(self):
        """Should compute anodic."""
        i = self.pc.anodic_current(-0.5, -0.6, 1e-6, 0.12)
        self.assertGreater(i, 1e-6)
        print(f"  [PASS] Anod: {i:.2e}")
    
    def test_cathodic(self):
        """Should compute cathodic."""
        i = self.pc.cathodic_current(-0.7, -0.6, 1e-6, 0.12)
        self.assertGreater(i, 1e-6)
        print(f"  [PASS] Cath: {i:.2e}")
    
    def test_rp(self):
        """Should compute Rp."""
        r = self.pc.polarization_resistance(0.12, 0.12, 1e-6)
        self.assertGreater(r, 0)
        print(f"  [PASS] Rp: {r:.2f}")


class TestCorrosionRatePrediction(unittest.TestCase):
    """Test rate."""
    
    def setUp(self):
        self.crp = CorrosionRatePrediction()
    
    def test_faraday(self):
        """Should compute Faraday rate."""
        r = self.crp.faraday_rate(1e-6, 27.9, 7.87)
        self.assertGreater(r, 0)
        print(f"  [PASS] Rate: {r:.4f}")
    
    def test_mpy(self):
        """Should compute mpy."""
        r = self.crp.penetration_rate_mpy(1e-6, 27.9, 7.87)
        self.assertGreater(r, 0)
        print(f"  [PASS] MPY: {r:.4f}")
    
    def test_ttf(self):
        """Should compute TTF."""
        t = self.crp.time_to_failure(0.1, 10.0)
        self.assertEqual(t, 100.0)
        print(f"  [PASS] TTF: {t:.1f}")


class TestProtectionDesign(unittest.TestCase):
    """Test protection."""
    
    def setUp(self):
        self.pd = ProtectionDesign()
    
    def test_anode(self):
        """Should compute anode mass."""
        m = self.pd.sacrificial_anode_mass(0.1, 10.0)
        self.assertGreater(m, 0)
        print(f"  [PASS] Mass: {m:.4f}")
    
    def test_impressed(self):
        """Should compute impressed current."""
        i = self.pd.impressed_current(10.0)
        self.assertAlmostEqual(i, 11.111, delta=0.001)
        print(f"  [PASS] I: {i:.3f}")
    
    def test_coating(self):
        """Should compute efficiency."""
        e = self.pd.coating_efficiency(1.0, 0.1)
        self.assertEqual(e, 90.0)
        print(f"  [PASS] Eff: {e:.1f}")


class TestCorrosionModeling(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.cm = CorrosionModeling()
    
    def test_summary(self):
        """Should summarize."""
        s = self.cm.corrosion_summary()
        self.assertIn("modules", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
