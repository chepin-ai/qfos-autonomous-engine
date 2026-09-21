"""
Unit tests for quantum density matrix module.
"""

import unittest
import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from quantum_density_matrix import (DensityMatrix, DensityMatrixBuilder,
                                    DensityMatrixOperations,
                                    PartialTrace,
                                    EntanglementMeasures,
                                    QuantumDensityMatrix)


class TestDensityMatrixBuilder(unittest.TestCase):
    """Test builder."""
    
    def setUp(self):
        self.b = DensityMatrixBuilder()
    
    def test_pure_state(self):
        """Should build from pure state."""
        rho = self.b.from_pure_state([1.0, 0.0])
        self.assertEqual(rho.matrix[0][0], 1.0)
        print("  [PASS] Pure")
    
    def test_maximally_mixed(self):
        """Should build mixed state."""
        rho = self.b.maximally_mixed(2)
        self.assertEqual(rho.matrix[0][0], 0.5)
        print("  [PASS] Mixed")
    
    def test_bell(self):
        """Should build Bell state."""
        rho = self.b.bell_state_density()
        self.assertEqual(rho.dim, 4)
        print("  [PASS] Bell")


class TestDensityMatrixOperations(unittest.TestCase):
    """Test operations."""
    
    def setUp(self):
        self.ops = DensityMatrixOperations()
        self.b = DensityMatrixBuilder()
    
    def test_trace(self):
        """Should compute trace."""
        rho = self.b.from_pure_state([1.0, 0.0])
        tr = self.ops.trace(rho)
        self.assertAlmostEqual(tr.real, 1.0, places=5)
        print(f"  [PASS] Tr: {tr.real:.3f}")
    
    def test_hermitian(self):
        """Should check Hermitian."""
        rho = self.b.from_pure_state([1.0 / math.sqrt(2), 1.0 / math.sqrt(2)])
        self.assertTrue(self.ops.is_hermitian(rho))
        print("  [PASS] Herm")
    
    def test_purity(self):
        """Should compute purity."""
        rho = self.b.from_pure_state([1.0, 0.0])
        p = self.ops.purity(rho)
        self.assertAlmostEqual(p, 1.0, places=5)
        print(f"  [PASS] Pur: {p:.3f}")
    
    def test_entropy(self):
        """Should compute entropy."""
        rho = self.b.maximally_mixed(2)
        s = self.ops.von_neumann_entropy(rho)
        self.assertGreater(s, 0)
        print(f"  [PASS] S: {s:.4f}")


class TestPartialTrace(unittest.TestCase):
    """Test partial trace."""
    
    def setUp(self):
        self.pt = PartialTrace()
        self.b = DensityMatrixBuilder()
    
    def test_trace_out(self):
        """Should trace out B."""
        rho = self.b.bell_state_density()
        rho_a = self.pt.trace_out_b(rho, 2, 2)
        self.assertEqual(rho_a.dim, 2)
        print("  [PASS] TrB")


class TestEntanglementMeasures(unittest.TestCase):
    """Test entanglement."""
    
    def setUp(self):
        self.em = EntanglementMeasures()
        self.b = DensityMatrixBuilder()
    
    def test_concurrence(self):
        """Should compute concurrence."""
        rho = self.b.bell_state_density()
        c = self.em.concurrence(rho)
        self.assertGreater(c, 0)
        print(f"  [PASS] C: {c:.3f}")
    
    def test_entanglement_entropy(self):
        """Should compute entanglement entropy."""
        rho = self.b.bell_state_density()
        s = self.em.entanglement_entropy(rho)
        self.assertGreater(s, 0)
        print(f"  [PASS] SEE: {s:.4f}")


class TestQuantumDensityMatrix(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.qdm = QuantumDensityMatrix()
    
    def test_summary(self):
        """Should summarize."""
        s = self.qdm.density_summary()
        self.assertIn("operations", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
