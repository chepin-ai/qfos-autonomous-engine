"""
Unit tests for particle size analysis module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from particle_size_analysis import (Particle, SieveAnalysis,
                                    LaserDiffraction,
                                    DynamicLightScattering,
                                    ParticleDistribution,
                                    ParticleSizeAnalysis)


class TestSieveAnalysis(unittest.TestCase):
    """Test sieve."""
    
    def setUp(self):
        self.sa = SieveAnalysis()
        self.particles = [Particle(100.0, 1e6), Particle(50.0, 1e5),
                         Particle(10.0, 1e3), Particle(5.0, 1e2)]
    
    def test_analyze(self):
        """Should analyze."""
        r = self.sa.analyze(self.particles)
        self.assertGreater(len(r), 0)
        print(f"  [PASS] Sieve: {len(r)} fractions")
    
    def test_d50(self):
        """Should compute D50."""
        d = self.sa.d50(self.particles)
        self.assertGreater(d, 0)
        print(f"  [PASS] D50: {d:.1f} um")


class TestLaserDiffraction(unittest.TestCase):
    """Test laser."""
    
    def setUp(self):
        self.ld = LaserDiffraction(633.0)
    
    def test_angle(self):
        """Should compute angle."""
        a = self.ld.diffraction_angle(10.0)
        self.assertGreater(a, 0)
        print(f"  [PASS] Ang: {a:.6f} rad")
    
    def test_size(self):
        """Should compute size."""
        s = self.ld.size_from_angle(0.0633)
        self.assertAlmostEqual(s, 10.0, places=1)
        print(f"  [PASS] Size: {s:.1f} um")


class TestDynamicLightScattering(unittest.TestCase):
    """Test DLS."""
    
    def setUp(self):
        self.dls = DynamicLightScattering()
    
    def test_hydrodynamic(self):
        """Should compute diameter."""
        d = self.dls.hydrodynamic_diameter(2.2e-12)
        self.assertGreater(d, 0)
        print(f"  [PASS] Hd: {d:.1f} nm")
    
    def test_diffusion(self):
        """Should compute D."""
        D = self.dls.diffusion_coefficient(100.0)
        self.assertGreater(D, 0)
        print(f"  [PASS] D: {D:.2e} m2/s")


class TestParticleDistribution(unittest.TestCase):
    """Test distribution."""
    
    def setUp(self):
        self.pd = ParticleDistribution()
        self.particles = [Particle(10.0, 1e3), Particle(20.0, 8e3),
                         Particle(30.0, 27e3)]
    
    def test_mean(self):
        """Should compute mean."""
        m = self.pd.mean_diameter(self.particles)
        self.assertEqual(m, 20.0)
        print(f"  [PASS] Mean: {m}")
    
    def test_std(self):
        """Should compute std."""
        s = self.pd.std_deviation(self.particles)
        self.assertGreater(s, 0)
        print(f"  [PASS] Std: {s:.2f}")
    
    def test_span(self):
        """Should compute span."""
        sp = self.pd.span(self.particles)
        self.assertGreaterEqual(sp, 0)
        print(f"  [PASS] Span: {sp:.4f}")
    
    def test_ssa(self):
        """Should compute SSA."""
        ssa = self.pd.specific_surface_area(self.particles)
        self.assertGreater(ssa, 0)
        print(f"  [PASS] SSA: {ssa:.4f} m2/g")


class TestParticleSizeAnalysis(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.psa = ParticleSizeAnalysis()
    
    def test_load(self):
        """Should load."""
        self.psa.load_particles([Particle(10.0, 1e3)])
        self.assertEqual(len(self.psa.particles), 1)
        print("  [PASS] Load")
    
    def test_full(self):
        """Should analyze."""
        self.psa.load_particles([Particle(10.0, 1e3),
                                 Particle(50.0, 1e5)])
        r = self.psa.full_analysis()
        self.assertIn("d50_um", r)
        print(f"  [PASS] Full: {r}")
    
    def test_summary(self):
        """Should summarize."""
        s = self.psa.psa_summary()
        self.assertIn("methods", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
