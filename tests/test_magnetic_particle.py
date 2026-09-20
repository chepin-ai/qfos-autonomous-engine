"""
Unit tests for magnetic particle inspection module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from magnetic_particle import (MagnetizationType, ParticleType,
                               MagneticIndication, Magnetizer,
                               ParticleSuspension, UVIndicationDetector,
                               Demagnetizer, MagneticParticleInspection)


class TestMagnetizer(unittest.TestCase):
    """Test magnetizer."""
    
    def setUp(self):
        self.mag = Magnetizer()
    
    def test_current(self):
        """Should compute current."""
        I = self.mag.required_current(50.0, 3)
        self.assertGreater(I, 0)
        print(f"  [PASS] I: {I:.1f}A")
    
    def test_flux(self):
        """Should compute flux density."""
        B = self.mag.magnetic_flux_density(1000.0)
        self.assertGreater(B, 0)
        print(f"  [PASS] B: {B:.4f}T")
    
    def test_type(self):
        """Should have type."""
        self.assertEqual(self.mag.mag_type, MagnetizationType.CIRCUMFERENTIAL)
        print("  [PASS] Type")


class TestParticleSuspension(unittest.TestCase):
    """Test particle suspension."""
    
    def setUp(self):
        self.ps = ParticleSuspension()
    
    def test_density(self):
        """Should compute density."""
        d = self.ps.particle_density()
        self.assertGreater(d, 0)
        print(f"  [PASS] Dens: {d:.0f}")
    
    def test_uv(self):
        """Should compute UV response."""
        r = self.ps.uv_response(0.5)
        self.assertGreater(r, 0)
        print(f"  [PASS] UV: {r:.3f}")
    
    def test_settling(self):
        """Should compute settling."""
        t = self.ps.settling_time(5.0)
        self.assertGreater(t, 0)
        print(f"  [PASS] Settle: {t:.1f}min")


class TestUVIndicationDetector(unittest.TestCase):
    """Test UV indication detector."""
    
    def setUp(self):
        self.uvd = UVIndicationDetector()
    
    def test_detect(self):
        """Should detect indications."""
        uv = [0.05] * 5 + [0.5, 0.7, 0.5] + [0.05] * 5
        pos = [(float(i), 0.0) for i in range(len(uv))]
        inds = self.uvd.detect(uv, pos)
        self.assertGreater(len(inds), 0)
        print(f"  [PASS] Inds: {len(inds)}")
    
    def test_contrast(self):
        """Should compute contrast."""
        c = self.uvd.contrast_ratio(0.8, 0.2)
        self.assertAlmostEqual(c, 4.0)
        print(f"  [PASS] C: {c}")


class TestDemagnetizer(unittest.TestCase):
    """Test demagnetizer."""
    
    def setUp(self):
        self.demag = Demagnetizer()
    
    def test_decay(self):
        """Should decay field."""
        f = self.demag.decay_field(1000.0, 2)
        self.assertEqual(f, 250.0)
        print(f"  [PASS] Decay: {f}")
    
    def test_sequence(self):
        """Should generate sequence."""
        seq = self.demag.alternating_decay(1000.0)
        self.assertGreater(len(seq), 0)
        print(f"  [PASS] Seq: {seq[:4]}")
    
    def test_residual(self):
        """Should estimate residual."""
        r = self.demag.residual_field(1000.0, 500.0)
        self.assertGreater(r, 0)
        print(f"  [PASS] Res: {r:.1f}")


class TestMagneticParticleInspection(unittest.TestCase):
    """Test unified MPI."""
    
    def setUp(self):
        self.mpi = MagneticParticleInspection()
    
    def test_inspect(self):
        """Should inspect."""
        uv = [0.05] * 5 + [0.6, 0.8, 0.6] + [0.05] * 5
        pos = [(float(i), 0.0) for i in range(len(uv))]
        r = self.mpi.inspect(uv, pos, 50.0, 1000.0)
        self.assertIn("flux_density_T", r)
        print(f"  [PASS] Insp: B={r['flux_density_T']:.4f}T")
    
    def test_set_mag(self):
        """Should set magnetization."""
        self.mpi.set_magnetization(MagnetizationType.LONGITUDINAL)
        self.assertEqual(self.mpi.magnetizer.mag_type, MagnetizationType.LONGITUDINAL)
        print("  [PASS] SetMag")
    
    def test_summary(self):
        """Should summarize."""
        uv = [0.05] * 10
        pos = [(float(i), 0.0) for i in range(10)]
        self.mpi.inspect(uv, pos)
        s = self.mpi.inspection_summary()
        self.assertIn("inspections", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
