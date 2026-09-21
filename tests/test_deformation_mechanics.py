"""
Unit tests for deformation mechanics module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from deformation_mechanics import (StressState, ElasticDeformation,
                                   PlasticDeformation,
                                   CreepDeformation,
                                   WorkHardening,
                                   DeformationMechanics)


class TestElasticDeformation(unittest.TestCase):
    """Test elastic."""
    
    def setUp(self):
        self.ed = ElasticDeformation()
    
    def test_strain(self):
        """Should compute strain."""
        e = self.ed.axial_strain(200.0)
        self.assertEqual(e, 1.0)
        print(f"  [PASS] Eps: {e:.3f}")
    
    def test_lateral(self):
        """Should compute lateral strain."""
        e = self.ed.lateral_strain(1.0)
        self.assertEqual(e, -0.3)
        print(f"  [PASS] Lat: {e:.2f}")
    
    def test_shear(self):
        """Should compute G."""
        g = self.ed.shear_modulus()
        self.assertAlmostEqual(g, 76.92, delta=0.1)
        print(f"  [PASS] G: {g:.2f}")
    
    def test_bulk(self):
        """Should compute K."""
        k = self.ed.bulk_modulus()
        self.assertAlmostEqual(k, 166.67, delta=0.1)
        print(f"  [PASS] K: {k:.2f}")


class TestPlasticDeformation(unittest.TestCase):
    """Test plastic."""
    
    def setUp(self):
        self.pd = PlasticDeformation()
    
    def test_von_mises(self):
        """Should compute VM."""
        s = StressState(100.0, 50.0, 0.0)
        v = self.pd.von_mises_stress(s)
        self.assertAlmostEqual(v, 86.6, delta=0.5)
        print(f"  [PASS] VM: {v:.1f}")
    
    def test_yielding(self):
        """Should detect yielding."""
        s = StressState(300.0, 0.0, 0.0)
        y = self.pd.is_yielding(s)
        self.assertTrue(y)
        print(f"  [PASS] Y: {y}")
    
    def test_safety(self):
        """Should compute SF."""
        s = StressState(100.0, 0.0, 0.0)
        sf = self.pd.safety_factor(s)
        self.assertEqual(sf, 2.5)
        print(f"  [PASS] SF: {sf:.2f}")


class TestCreepDeformation(unittest.TestCase):
    """Test creep."""
    
    def setUp(self):
        self.cd = CreepDeformation()
    
    def test_rate(self):
        """Should compute rate."""
        r = self.cd.steady_state_creep_rate(100.0)
        self.assertGreater(r, 0)
        print(f"  [PASS] CR: {r:.2e}")
    
    def test_strain(self):
        """Should compute strain."""
        e = self.cd.creep_strain(1e-6, 1000.0)
        self.assertEqual(e, 1e-3)
        print(f"  [PASS] Epsc: {e:.2e}")


class TestWorkHardening(unittest.TestCase):
    """Test hardening."""
    
    def setUp(self):
        self.wh = WorkHardening()
    
    def test_flow(self):
        """Should compute flow stress."""
        f = self.wh.flow_stress(0.1)
        self.assertGreater(f, 0)
        print(f"  [PASS] FS: {f:.2f}")
    
    def test_tangent(self):
        """Should compute tangent modulus."""
        t = self.wh.tangent_modulus(0.1)
        self.assertGreater(t, 0)
        print(f"  [PASS] Et: {t:.2f}")


class TestDeformationMechanics(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.dm = DeformationMechanics()
    
    def test_summary(self):
        """Should summarize."""
        s = self.dm.deformation_summary()
        self.assertIn("regimes", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
