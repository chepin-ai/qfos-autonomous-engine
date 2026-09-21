"""
Unit tests for quantum crystallography advanced module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from quantum_crystallography_advanced import (MillerIndices, QuantumDiffraction,
                                              StructureFactor,
                                              PhaseRetrieval,
                                              ElectronDensityMap,
                                              QuantumCrystallographyAdvanced)


class TestQuantumDiffraction(unittest.TestCase):
    """Test diffraction."""
    
    def setUp(self):
        self.qd = QuantumDiffraction()
    
    def test_bragg(self):
        """Should compute angle."""
        a = self.qd.bragg_angle(2.0)
        self.assertGreater(a, 0)
        print(f"  [PASS] 2th: {a:.2f}")
    
    def test_d_spacing(self):
        """Should compute d."""
        d = self.qd.d_spacing(MillerIndices(1, 1, 1), 3.6)
        self.assertAlmostEqual(d, 2.078, delta=0.01)
        print(f"  [PASS] d: {d:.3f}")


class TestStructureFactor(unittest.TestCase):
    """Test structure factor."""
    
    def setUp(self):
        self.sf = StructureFactor()
    
    def test_scattering(self):
        """Should compute f."""
        f = self.sf.atomic_scattering_factor(0.2)
        self.assertGreater(f, 0)
        print(f"  [PASS] f: {f:.2f}")
    
    def test_amplitude(self):
        """Should compute |F|."""
        atoms = [(0.0, 0.0, 0.0, 26.0), (0.5, 0.5, 0.5, 26.0)]
        amp = self.sf.structure_factor_amplitude(atoms, MillerIndices(1, 0, 0))
        self.assertAlmostEqual(amp, 0.0, delta=1e-10)
        print(f"  [PASS] |F|: {amp:.1f}")


class TestPhaseRetrieval(unittest.TestCase):
    """Test phase."""
    
    def setUp(self):
        self.pr = PhaseRetrieval()
    
    def test_error_reduction(self):
        """Should reduce."""
        amps, phases = self.pr.error_reduction([1.0, 2.0], [0.0, 0.0], [True, True])
        self.assertEqual(len(amps), 2)
        print(f"  [PASS] ER: {len(amps)} pts")
    
    def test_phase_error(self):
        """Should compute error."""
        e = self.pr.phase_error([0.0, 90.0], [10.0, 80.0])
        self.assertAlmostEqual(e, 10.0, delta=1e-10)
        print(f"  [PASS] Err: {e:.1f}")


class TestElectronDensityMap(unittest.TestCase):
    """Test density."""
    
    def setUp(self):
        self.edm = ElectronDensityMap()
    
    def test_density(self):
        """Should compute density."""
        f = [complex(1.0, 0.0)]
        hkl = [MillerIndices(0, 0, 0)]
        d = self.edm.electron_density(f, hkl, 0.0, 0.0, 0.0)
        self.assertEqual(d, 1.0)
        print(f"  [PASS] Rho: {d:.2f}")
    
    def test_peak(self):
        """Should find peak."""
        p = self.edm.peak_height([0.5, 1.0, 0.3])
        self.assertEqual(p, 1.0)
        print(f"  [PASS] Peak: {p:.2f}")


class TestQuantumCrystallographyAdvanced(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.qca = QuantumCrystallographyAdvanced()
    
    def test_summary(self):
        """Should summarize."""
        s = self.qca.crystallography_summary()
        self.assertIn("methods", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
