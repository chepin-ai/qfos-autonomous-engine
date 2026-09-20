"""
Unit tests for quantum chemistry module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from quantum_chemistry import (BasisSet, MolecularHamiltonian,
                                ChemistryVQE, QuantumChemistry)


class TestBasisSet(unittest.TestCase):
    """Test basis set."""
    
    def setUp(self):
        self.bs = BasisSet("STO-3G")
    
    def test_add(self):
        """Should add Gaussian."""
        self.bs.add_gaussian((0.0, 0.0, 0.0), 1.0, 0.5)
        self.assertEqual(len(self.bs.functions), 1)
        print("  [PASS] Add")
    
    def test_overlap(self):
        """Should compute overlap."""
        self.bs.add_gaussian((0.0, 0.0, 0.0), 1.0, 1.0)
        self.bs.add_gaussian((0.0, 0.0, 0.0), 1.0, 1.0)
        s = self.bs.overlap(0, 1)
        self.assertGreater(s, 0)
        print(f"  [PASS] Overlap: {s:.4f}")


class TestMolecularHamiltonian(unittest.TestCase):
    """Test molecular Hamiltonian."""
    
    def setUp(self):
        self.mh = MolecularHamiltonian(2)
    
    def test_h_core(self):
        """Should set h_core."""
        self.mh.set_h_core(0, 0, -1.0)
        self.assertEqual(self.mh.h_core[0][0], -1.0)
        print("  [PASS] h_core")
    
    def test_eri(self):
        """Should set ERI."""
        self.mh.set_eri(0, 0, 0, 0, 0.5)
        self.assertEqual(self.mh.eri[(0, 0, 0, 0)], 0.5)
        print("  [PASS] ERI")
    
    def test_nuclear(self):
        """Should compute nuclear repulsion."""
        e = self.mh.nuclear_repulsion([1, 1], [(0.0, 0.0, 0.0), (1.0, 0.0, 0.0)])
        self.assertGreater(e, 0)
        print(f"  [PASS] Nuc: {e:.4f}")
    
    def test_hf(self):
        """Should compute HF energy."""
        self.mh.set_h_core(0, 0, -1.0)
        self.mh.set_eri(0, 0, 0, 0, 0.5)
        e = self.mh.hf_energy(2)
        self.assertLess(e, 0)
        print(f"  [PASS] HF: {e:.4f}")


class TestChemistryVQE(unittest.TestCase):
    """Test chemistry VQE."""
    
    def setUp(self):
        self.vqe = ChemistryVQE(4)
    
    def test_ansatz(self):
        """Should generate ansatz."""
        state = self.vqe.ansatz([0.1] * 4)
        self.assertEqual(len(state), 16)
        norm = sum(abs(z)**2 for z in state)
        self.assertAlmostEqual(norm, 1.0, places=5)
        print(f"  [PASS] Ansatz: norm={norm:.4f}")
    
    def test_expectation(self):
        """Should compute expectation."""
        mh = MolecularHamiltonian(2)
        mh.set_h_core(0, 0, -1.0)
        state = self.vqe.ansatz([0.0] * 4)
        e = self.vqe.expectation(mh, state)
        self.assertIsNotNone(e)
        print(f"  [PASS] Exp: {e:.4f}")
    
    def test_optimize(self):
        """Should optimize."""
        mh = MolecularHamiltonian(2)
        mh.set_h_core(0, 0, -1.0)
        r = self.vqe.optimize(mh, 20)
        self.assertIn("energy", r)
        print(f"  [PASS] Opt: E={r['energy']:.4f}")


class TestQuantumChemistry(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.qc = QuantumChemistry()
    
    def test_basis(self):
        """Should build basis."""
        self.qc.build_basis("STO-3G")
        self.assertIsNotNone(self.qc.basis)
        print("  [PASS] Basis")
    
    def test_hamiltonian(self):
        """Should build Hamiltonian."""
        self.qc.build_hamiltonian(2)
        self.assertIsNotNone(self.qc.hamiltonian)
        print("  [PASS] H")
    
    def test_vqe(self):
        """Should run VQE."""
        r = self.qc.run_vqe(2, 10)
        self.assertIn("energy", r)
        print(f"  [PASS] VQE: E={r['energy']:.4f}")
    
    def test_summary(self):
        """Should summarize."""
        self.qc.run_vqe(2, 5)
        s = self.qc.chemistry_summary()
        self.assertIn("vqe_runs", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
