"""
Unit tests for quantum generative modeling module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from quantum_generative_modeling import (QCBMCircuit, MMDLoss,
                                          QuantumBornMachineTrainer,
                                          QuantumGenerativeModeling)


class TestQCBMCircuit(unittest.TestCase):
    """Test QCBM circuit."""
    
    def setUp(self):
        self.qc = QCBMCircuit(3, 2)
    
    def test_run(self):
        """Should run."""
        state = self.qc.run()
        self.assertEqual(len(state), 8)
        print("  [PASS] Run")
    
    def test_probabilities(self):
        """Should get probabilities."""
        p = self.qc.probabilities()
        self.assertEqual(len(p), 8)
        self.assertAlmostEqual(sum(p), 1.0, places=5)
        print(f"  [PASS] Prob: sum={sum(p):.4f}")
    
    def test_sample(self):
        """Should sample."""
        s = self.qc.sample(50)
        self.assertEqual(len(s), 50)
        print(f"  [PASS] Sample: {len(s)}")


class TestMMDLoss(unittest.TestCase):
    """Test MMD."""
    
    def setUp(self):
        self.mmd = MMDLoss()
    
    def test_kernel(self):
        """Should compute kernel."""
        k = self.mmd.gaussian_kernel(0, 3)
        self.assertGreater(k, 0)
        print(f"  [PASS] Kernel: {k:.4f}")
    
    def test_mmd(self):
        """Should compute MMD."""
        p = [0.5, 0.5, 0.0, 0.0]
        q = [0.5, 0.5, 0.0, 0.0]
        m = self.mmd.mmd(p, q)
        self.assertGreaterEqual(m, 0)
        print(f"  [PASS] MMD: {m:.4f}")


class TestQuantumBornMachineTrainer(unittest.TestCase):
    """Test QCBM trainer."""
    
    def setUp(self):
        self.qc = QCBMCircuit(2, 1)
        self.target = [0.5, 0.0, 0.0, 0.5]
        self.trainer = QuantumBornMachineTrainer(self.qc, self.target, 0.05)
    
    def test_gradient(self):
        """Should compute gradient."""
        g = self.trainer.compute_gradient(0, 0)
        self.assertIsNotNone(g)
        print(f"  [PASS] Grad: {g:.4f}")
    
    def test_train_step(self):
        """Should do one step."""
        self.trainer.train_step()
        print("  [PASS] Step")
    
    def test_train(self):
        """Should train."""
        self.trainer.train(3)
        self.assertEqual(len(self.trainer.loss_history), 3)
        print(f"  [PASS] Train: {self.trainer.loss_history}")


class TestQuantumGenerativeModeling(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.qgm = QuantumGenerativeModeling()
    
    def test_create(self):
        """Should create circuit."""
        self.qgm.create_circuit(3, 2)
        self.assertIsNotNone(self.qgm.circuit)
        print("  [PASS] Create")
    
    def test_train(self):
        """Should train."""
        target = [0.5, 0.0, 0.0, 0.5]
        r = self.qgm.train(target, 2, 0.05)
        self.assertIn("final_loss", r)
        print(f"  [PASS] Train: {r}")
    
    def test_generate(self):
        """Should generate."""
        s = self.qgm.generate(20)
        self.assertEqual(len(s), 20)
        print(f"  [PASS] Gen: {len(s)}")
    
    def test_summary(self):
        """Should summarize."""
        self.qgm.create_circuit(3, 2)
        s = self.qgm.qgm_summary()
        self.assertIn("qubits", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
