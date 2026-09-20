"""
Unit tests for quantum data compression module.
"""

import unittest
import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from quantum_data_compression import (QuantumCompressor, QuantumAutoencoder,
                                      QuantumPCA, QuantumDataCompression)


class TestQuantumCompressor(unittest.TestCase):
    """Test quantum compressor."""
    
    def setUp(self):
        self.qc = QuantumCompressor(4, 2)
    
    def test_compress(self):
        """Should compress."""
        state = [complex(1.0, 0.0)] + [complex(0.0, 0.0)] * 15
        c = self.qc.compress(state)
        self.assertEqual(len(c), 4)
        norm = sum(abs(z)**2 for z in c)
        self.assertAlmostEqual(norm, 1.0, places=5)
        print(f"  [PASS] Compress: norm={norm:.4f}")
    
    def test_decompress(self):
        """Should decompress."""
        comp = [complex(1.0, 0.0), complex(0.0, 0.0),
                complex(0.0, 0.0), complex(0.0, 0.0)]
        d = self.qc.decompress(comp)
        self.assertEqual(len(d), 16)
        norm = sum(abs(z)**2 for z in d)
        self.assertAlmostEqual(norm, 1.0, places=5)
        print(f"  [PASS] Decompress: norm={norm:.4f}")


class TestQuantumAutoencoder(unittest.TestCase):
    """Test quantum autoencoder."""
    
    def setUp(self):
        self.qae = QuantumAutoencoder(4, 2)
    
    def test_encode(self):
        """Should encode."""
        state = self.qae.encode_classical([0.5, 0.5, 0.5, 0.5])
        self.assertEqual(len(state), 16)
        norm = sum(abs(z)**2 for z in state)
        self.assertAlmostEqual(norm, 1.0, places=5)
        print(f"  [PASS] Encode: norm={norm:.4f}")
    
    def test_decode(self):
        """Should decode."""
        state = [complex(0.5, 0.0)] * 4 + [complex(0.0, 0.0)] * 12
        d = self.qae.decode_classical(state)
        self.assertEqual(len(d), 4)
        print(f"  [PASS] Decode: {d}")
    
    def test_forward(self):
        """Should forward."""
        rec, lat = self.qae.forward([0.5, 0.5, 0.5, 0.5])
        self.assertEqual(len(rec), 4)
        self.assertEqual(len(lat), 4)
        print("  [PASS] Forward")
    
    def test_error(self):
        """Should compute error."""
        err = self.qae.reconstruction_error([1.0, 0.0, 0.0, 0.0],
                                            [0.9, 0.1, 0.0, 0.0])
        self.assertGreater(err, 0)
        print(f"  [PASS] Error: {err:.4f}")


class TestQuantumPCA(unittest.TestCase):
    """Test QPCA."""
    
    def setUp(self):
        self.qpca = QuantumPCA(4, 2)
    
    def test_covariance(self):
        """Should compute covariance."""
        data = [[1.0, 2.0], [2.0, 3.0], [3.0, 4.0]]
        cov = self.qpca.covariance(data)
        self.assertEqual(len(cov), 2)
        self.assertEqual(len(cov[0]), 2)
        print("  [PASS] Cov")
    
    def test_power_iteration(self):
        """Should find eigenvalue."""
        m = [[2.0, 1.0], [1.0, 2.0]]
        val, vec = self.qpca.power_iteration(m, 30)
        self.assertGreater(val, 0)
        self.assertAlmostEqual(sum(v**2 for v in vec), 1.0, places=5)
        print(f"  [PASS] Eig: {val:.4f}")
    
    def test_fit(self):
        """Should fit."""
        data = [[1.0, 2.0, 3.0], [2.0, 3.0, 4.0], [3.0, 4.0, 5.0]]
        self.qpca.fit(data)
        self.assertEqual(len(self.qpca.eigenvalues), 2)
        print(f"  [PASS] Fit: vals={self.qpca.eigenvalues}")
    
    def test_transform(self):
        """Should transform."""
        data = [[1.0, 2.0, 3.0], [2.0, 3.0, 4.0], [3.0, 4.0, 5.0]]
        self.qpca.fit(data)
        proj = self.qpca.transform([1.0, 2.0, 3.0])
        self.assertEqual(len(proj), 2)
        print(f"  [PASS] Transform: {proj}")


class TestQuantumDataCompression(unittest.TestCase):
    """Test unified controller."""
    
    def setUp(self):
        self.qdc = QuantumDataCompression()
    
    def test_build_ae(self):
        """Should build autoencoder."""
        self.qdc.build_autoencoder(4, 2)
        self.assertIsNotNone(self.qdc.autoencoder)
        print("  [PASS] BuildAE")
    
    def test_compress(self):
        """Should compress."""
        r = self.qdc.compress_data([0.5, 0.5, 0.5, 0.5])
        self.assertIn("compression_ratio", r)
        print(f"  [PASS] Compress: ratio={r['compression_ratio']:.2f}")
    
    def test_qpca(self):
        """Should fit QPCA."""
        data = [[1.0, 2.0, 3.0], [2.0, 3.0, 4.0]]
        self.qdc.fit_qpca(data, 2)
        self.assertIsNotNone(self.qdc.qpca)
        print("  [PASS] QPCA")
    
    def test_summary(self):
        """Should summarize."""
        self.qdc.compress_data([0.5, 0.5, 0.5, 0.5])
        s = self.qdc.compression_summary()
        self.assertIn("compressions", s)
        print(f"  [PASS] Sum: {s}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
