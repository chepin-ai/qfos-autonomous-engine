"""
Unit tests for quantum Monte Carlo module.
"""

import unittest
import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from quantum_monte_carlo import (TrialWavefunction, VariationalQMC,
                                  DiffusionQMC, QuantumMonteCarlo)


class TestTrialWavefunction(unittest.TestCase):
    """Test trial wavefunction."""
    
    def setUp(self):
        self.wf = TrialWavefunction(2, 1)
    
    def test_evaluate(self):
        """Should evaluate."""
        pos = [[0.0], [1.0]]
        v = self.wf.evaluate(pos)
        self.assertGreater(v, 0)
        print(f"  [PASS] Eval: {v:.4f}")
    
    def test_local_energy(self):
        """Should compute local energy."""
        pos = [[0.0], [0.0]]
        pot = lambda p: 0.5 * sum(x**2 for x in p)
        e = self.wf.local_energy(pos, pot)
        self.assertIsNotNone(e)
        print(f"  [PASS] LE: {e:.4f}")


class TestVariationalQMC(unittest.TestCase):
    """Test VQMC."""
    
    def setUp(self):
        wf = TrialWavefunction(2, 1)
        pot = lambda p: 0.5 * sum(x**2 for x in p)
        self.vqmc = VariationalQMC(wf, pot)
    
    def test_metropolis(self):
        """Should do metropolis."""
        pos = [[0.0], [0.0]]
        new = self.vqmc.metropolis_step(pos, 0.1)
        self.assertEqual(len(new), 2)
        print("  [PASS] Metro")
    
    def test_sample(self):
        """Should sample."""
        e = self.vqmc.sample(100, 10, 0.1)
        self.assertEqual(len(e), 100)
        print(f"  [PASS] Sample: {len(e)} energies")
    
    def test_estimate(self):
        """Should estimate."""
        self.vqmc.sample(100, 10, 0.1)
        mean, err = self.vqmc.energy_estimate()
        self.assertIsNotNone(mean)
        print(f"  [PASS] Est: {mean:.4f} +/- {err:.4f}")


class TestDiffusionQMC(unittest.TestCase):
    """Test DQMC."""
    
    def setUp(self):
        self.dqmc = DiffusionQMC(2, 1)
    
    def test_init(self):
        """Should initialize."""
        self.dqmc.initialize_walkers(50)
        self.assertEqual(len(self.dqmc.walkers), 50)
        print("  [PASS] Init")
    
    def test_step(self):
        """Should step."""
        self.dqmc.initialize_walkers(10)
        w = self.dqmc.drift_diffusion_step(self.dqmc.walkers[0])
        self.assertEqual(len(w), 2)
        print("  [PASS] Step")
    
    def test_branch(self):
        """Should branch."""
        self.dqmc.initialize_walkers(10)
        self.dqmc.branch([1.0] * 10)
        self.assertGreater(len(self.dqmc.walkers), 0)
        print("  [PASS] Branch")
    
    def test_energy(self):
        """Should compute energy."""
        self.dqmc.initialize_walkers(10)
        pot = lambda p: 0.5 * sum(x**2 for x in p)
        e = self.dqmc.energy_from_walkers(pot)
        self.assertGreaterEqual(e, 0)
        print(f"  [PASS] Energy: {e:.4f}")


class TestQuantumMonteCarlo(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.qmc = QuantumMonteCarlo()
    
    def test_vqmc(self):
        """Should run VQMC."""
        r = self.qmc.run_vqmc(2, 1, None, 100)
        self.assertIn("energy", r)
        print(f"  [PASS] VQMC: E={r['energy']:.4f}")
    
    def test_dqmc(self):
        """Should run DQMC."""
        r = self.qmc.run_dqmc(2, 1, None, 20, 10)
        self.assertIn("energy", r)
        print(f"  [PASS] DQMC: E={r['energy']:.4f}")
    
    def test_summary(self):
        """Should summarize."""
        self.qmc.run_vqmc(2, 1, None, 50)
        s = self.qmc.qmc_summary()
        self.assertIn("runs", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
