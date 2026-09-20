"""
Unit tests for quantum state tomography module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from quantum_state_tomography import (PauliBasis, MeasurementResult,
                                      DensityMatrix, StateTomography,
                                      POVM, TomographyFidelity,
                                      QuantumStateTomography)


class TestDensityMatrix(unittest.TestCase):
    """Test density matrix."""
    
    def test_purity_mixed(self):
        """Should have purity 0.5 for maximally mixed."""
        rho = DensityMatrix()
        self.assertAlmostEqual(rho.purity(), 0.5)
        print("  [PASS] Purity mixed")
    
    def test_purity_pure(self):
        """Should have purity 1.0 for pure state."""
        rho = DensityMatrix()
        rho.from_bloch(0.0, 0.0, 1.0)
        self.assertAlmostEqual(rho.purity(), 1.0)
        print("  [PASS] Purity pure")
    
    def test_physical(self):
        """Should detect physical state."""
        rho = DensityMatrix()
        rho.from_bloch(0.5, 0.5, 0.5)
        self.assertTrue(rho.is_physical())
        print("  [PASS] Physical")
    
    def test_non_physical(self):
        """Should detect non-physical state."""
        rho = DensityMatrix()
        rho.from_bloch(2.0, 0.0, 0.0)
        self.assertFalse(rho.is_physical())
        print("  [PASS] Non-physical")
    
    def test_fidelity_same(self):
        """Should have fidelity 1 for same state."""
        rho1 = DensityMatrix()
        rho1.from_bloch(0.0, 0.0, 1.0)
        rho2 = DensityMatrix()
        rho2.from_bloch(0.0, 0.0, 1.0)
        self.assertAlmostEqual(rho1.fidelity(rho2), 1.0)
        print("  [PASS] Fidelity same")
    
    def test_fidelity_orthogonal(self):
        """Should have fidelity 0 for orthogonal."""
        rho1 = DensityMatrix()
        rho1.from_bloch(0.0, 0.0, 1.0)
        rho2 = DensityMatrix()
        rho2.from_bloch(0.0, 0.0, -1.0)
        self.assertAlmostEqual(rho1.fidelity(rho2), 0.0)
        print("  [PASS] Fidelity orth")


class TestStateTomography(unittest.TestCase):
    """Test state tomography."""
    
    def setUp(self):
        self.st = StateTomography()
    
    def test_linear_inversion(self):
        """Should reconstruct via linear inversion."""
        # Measure |0> state: Z=+1, X=0, Y=0
        self.st.add_measurement(MeasurementResult(PauliBasis.Z, 1, 100))
        self.st.add_measurement(MeasurementResult(PauliBasis.X, 1, 50))
        self.st.add_measurement(MeasurementResult(PauliBasis.X, -1, 50))
        self.st.add_measurement(MeasurementResult(PauliBasis.Y, 1, 50))
        self.st.add_measurement(MeasurementResult(PauliBasis.Y, -1, 50))
        
        rho = self.st.linear_inversion()
        self.assertAlmostEqual(rho.r[2], 1.0, places=1)
        print(f"  [PASS] LI: rz={rho.r[2]:.2f}")
    
    def test_ml_physical(self):
        """Should return physical state from ML."""
        self.st.add_measurement(MeasurementResult(PauliBasis.Z, 1, 100))
        rho = self.st.maximum_likelihood()
        self.assertTrue(rho.is_physical())
        print("  [PASS] ML physical")
    
    def test_expectation(self):
        """Should estimate expectation."""
        self.st.add_measurement(MeasurementResult(PauliBasis.Z, 1, 100))
        e = self.st.estimate_expectation(PauliBasis.Z)
        self.assertAlmostEqual(e, 1.0)
        print(f"  [PASS] Exp: {e}")


class TestPOVM(unittest.TestCase):
    """Test POVM."""
    
    def setUp(self):
        self.povm = POVM()
    
    def test_completeness(self):
        """Should check completeness."""
        # Add projectors onto |0> and |1>
        self.povm.add_operator([[1, 0], [0, 0]])
        self.povm.add_operator([[0, 0], [0, 1]])
        self.assertTrue(self.povm.completeness())
        print("  [PASS] Complete")
    
    def test_incomplete(self):
        """Should detect incomplete."""
        self.povm.add_operator([[0.5, 0], [0, 0]])
        self.assertFalse(self.povm.completeness())
        print("  [PASS] Incomplete")
    
    def test_probability(self):
        """Should compute probability."""
        self.povm.add_operator([[1, 0], [0, 0]])
        rho = DensityMatrix()
        rho.from_bloch(0.0, 0.0, 1.0)
        p = self.povm.probability(rho, 0)
        self.assertAlmostEqual(p, 1.0)
        print(f"  [PASS] Prob: {p}")


class TestTomographyFidelity(unittest.TestCase):
    """Test tomography fidelity."""
    
    def test_reconstruction(self):
        """Should compute reconstruction fidelity."""
        tf = TomographyFidelity()
        true = DensityMatrix()
        true.from_bloch(0.0, 0.0, 1.0)
        tf.set_true_state(true)
        
        est = DensityMatrix()
        est.from_bloch(0.0, 0.0, 0.9)
        f = tf.reconstruction_fidelity(est)
        self.assertGreater(f, 0.9)
        print(f"  [PASS] Rec fid: {f:.4f}")
    
    def test_statistical_error(self):
        """Should estimate error."""
        tf = TomographyFidelity()
        e = tf.statistical_error(100)
        self.assertAlmostEqual(e, 0.1)
        print(f"  [PASS] Error: {e:.3f}")


class TestQuantumStateTomography(unittest.TestCase):
    """Test unified tomography."""
    
    def setUp(self):
        self.qst = QuantumStateTomography()
    
    def test_measure(self):
        """Should record measurement."""
        self.qst.measure(PauliBasis.Z, 1, 100)
        self.assertEqual(len(self.qst.tomography.measurements), 1)
        print("  [PASS] Measure")
    
    def test_reconstruct(self):
        """Should reconstruct."""
        self.qst.measure(PauliBasis.Z, 1, 100)
        self.qst.measure(PauliBasis.X, 1, 50)
        self.qst.measure(PauliBasis.X, -1, 50)
        rho = self.qst.reconstruct()
        self.assertIsNotNone(rho)
        print("  [PASS] Reconstruct")
    
    def test_summary(self):
        """Should provide summary."""
        self.qst.measure(PauliBasis.Z, 1, 100)
        self.qst.reconstruct()
        s = self.qst.tomography_summary()
        self.assertIn("purity", s)
        print(f"  [PASS] Summary: purity={s['purity']:.3f}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
