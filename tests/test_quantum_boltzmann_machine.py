"""
Unit tests for quantum Boltzmann machine module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from quantum_boltzmann_machine import (QBMState, QuantumBoltzmannMachine,
                                        QBMLearner,
                                        QuantumBoltzmannMachineController)


class TestQBMState(unittest.TestCase):
    """Test QBM state."""
    
    def test_init(self):
        """Should initialize."""
        s = QBMState(4, 4)
        self.assertEqual(len(s.visible), 4)
        self.assertEqual(len(s.hidden), 4)
        print("  [PASS] Init")
    
    def test_copy(self):
        """Should copy."""
        s = QBMState(4, 4)
        c = s.copy()
        self.assertEqual(c.visible, s.visible)
        print("  [PASS] Copy")


class TestQuantumBoltzmannMachine(unittest.TestCase):
    """Test QBM."""
    
    def setUp(self):
        self.qbm = QuantumBoltzmannMachine(4, 4)
    
    def test_energy(self):
        """Should compute energy."""
        s = QBMState(4, 4)
        e = self.qbm.energy(s)
        self.assertIsInstance(e, float)
        print(f"  [PASS] Energy: {e:.4f}")
    
    def test_probability(self):
        """Should compute probability."""
        s = QBMState(4, 4)
        p = self.qbm.probability(s)
        self.assertGreater(p, 0)
        print(f"  [PASS] Prob: {p:.6f}")
    
    def test_sample_hidden(self):
        """Should sample hidden."""
        h = self.qbm.sample_hidden([1, -1, 1, -1])
        self.assertEqual(len(h), 4)
        self.assertTrue(all(abs(x) == 1 for x in h))
        print(f"  [PASS] SampleH: {h}")
    
    def test_sample_visible(self):
        """Should sample visible."""
        v = self.qbm.sample_visible([1, -1, 1, -1])
        self.assertEqual(len(v), 4)
        self.assertTrue(all(abs(x) == 1 for x in v))
        print(f"  [PASS] SampleV: {v}")
    
    def test_gibbs(self):
        """Should Gibbs sample."""
        s = QBMState(4, 4)
        ns = self.qbm.gibbs_sample(s, 5)
        self.assertEqual(len(ns.visible), 4)
        print("  [PASS] Gibbs")
    
    def test_reconstruct(self):
        """Should reconstruct."""
        v = [1, -1, 1, -1]
        r = self.qbm.reconstruct(v, 5)
        self.assertEqual(len(r), 4)
        print(f"  [PASS] Recon: {r}")


class TestQBMLearner(unittest.TestCase):
    """Test QBM learner."""
    
    def setUp(self):
        self.qbm = QuantumBoltzmannMachine(4, 4)
        self.l = QBMLearner(self.qbm)
    
    def test_train_step(self):
        """Should train step."""
        data = [[1, 1, -1, -1], [-1, -1, 1, 1], [1, -1, 1, -1]]
        loss = self.l.train_step(data, 1)
        self.assertIsNotNone(loss)
        print(f"  [PASS] Step: loss={loss:.4f}")
    
    def test_train(self):
        """Should train."""
        data = [[1, 1, -1, -1], [-1, -1, 1, 1], [1, -1, 1, -1]]
        r = self.l.train(data, epochs=10, batch_size=2)
        self.assertIn("final_loss", r)
        print(f"  [PASS] Train: loss={r['final_loss']:.4f}")


class TestQuantumBoltzmannMachineController(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.ctrl = QuantumBoltzmannMachineController()
    
    def test_build(self):
        """Should build."""
        self.ctrl.build(4, 4)
        self.assertIsNotNone(self.ctrl.qbm)
        print("  [PASS] Build")
    
    def test_train(self):
        """Should train."""
        data = [[1, 1, -1, -1], [-1, -1, 1, 1], [1, -1, 1, -1]]
        r = self.ctrl.train(data, 10)
        self.assertIn("final_loss", r)
        print(f"  [PASS] Train: loss={r['final_loss']:.4f}")
    
    def test_generate(self):
        """Should generate."""
        self.ctrl.build(4, 4)
        s = self.ctrl.generate(5, 5)
        self.assertEqual(len(s), 5)
        print("  [PASS] Gen")
    
    def test_summary(self):
        """Should summarize."""
        self.ctrl.build(4, 4)
        s = self.ctrl.qbm_summary()
        self.assertIn("visible", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
