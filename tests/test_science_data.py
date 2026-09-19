"""
Unit tests for science data management module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from science_data import (
    ScienceDataManager, DataCompressor, ScienceDataProduct,
    DataPriority, CompressionType
)


class TestDataCompressor(unittest.TestCase):
    """Test data compression."""
    
    def setUp(self):
        self.compressor = DataCompressor()
    
    def test_lossless_compression(self):
        """Lossless should reduce size with full quality."""
        size, quality = self.compressor.compress("image", 100.0, CompressionType.LOSSLESS)
        self.assertLess(size, 100.0)
        self.assertEqual(quality, 1.0)
        print(f"  [PASS] Lossless: {100.0:.1f}MB -> {size:.1f}MB, quality={quality}")
    
    def test_lossy_compression(self):
        """Lossy should reduce size more with slight quality loss."""
        size, quality = self.compressor.compress("image", 100.0, CompressionType.LOSSY)
        self.assertLess(size, 100.0)
        self.assertLess(quality, 1.0)
        self.assertGreater(quality, 0.8)
        print(f"  [PASS] Lossy: {100.0:.1f}MB -> {size:.1f}MB, quality={quality:.3f}")
    
    def test_no_compression(self):
        """No compression should preserve size."""
        size, quality = self.compressor.compress("image", 100.0, CompressionType.NONE)
        self.assertEqual(size, 100.0)
        self.assertEqual(quality, 1.0)
        print("  [PASS] No compression: size unchanged")


class TestScienceDataManager(unittest.TestCase):
    """Test science data management."""
    
    def setUp(self):
        self.dm = ScienceDataManager(storage_capacity_mb=100.0)
    
    def test_ingest_data(self):
        """Should store data product."""
        product = ScienceDataProduct(
            product_id="IMG_001", instrument="camera",
            priority=DataPriority.HIGH, size_mb=10.0,
            raw_size_mb=20.0, compression=CompressionType.LOSSLESS,
            timestamp=0.0
        )
        success = self.dm.ingest_data(product)
        self.assertTrue(success)
        self.assertEqual(self.dm.used_mb, 10.0)
        print(f"  [PASS] Ingest: {self.dm.used_mb:.1f}MB used")
    
    def test_storage_full(self):
        """Should reject data when storage full."""
        # Fill storage
        for i in range(15):
            product = ScienceDataProduct(
                product_id=f"IMG_{i:03d}", instrument="camera",
                priority=DataPriority.LOW, size_mb=10.0,
                raw_size_mb=20.0, compression=CompressionType.LOSSLESS,
                timestamp=float(i)
            )
            self.dm.ingest_data(product)
        
        # Try to add more
        extra = ScienceDataProduct(
            product_id="EXTRA", instrument="camera",
            priority=DataPriority.LOW, size_mb=10.0,
            raw_size_mb=20.0, compression=CompressionType.LOSSLESS,
            timestamp=100.0
        )
        success = self.dm.ingest_data(extra)
        # Should have deleted low priority to make room
        self.assertTrue(success)
        print(f"  [PASS] Storage management: {self.dm.used_mb:.1f}MB / {self.dm.capacity_mb:.1f}MB")
    
    def test_select_for_downlink(self):
        """Should select high priority data for downlink."""
        # Add products with different priorities
        for i, priority in enumerate([DataPriority.LOW, DataPriority.MEDIUM, DataPriority.HIGH, DataPriority.CRITICAL]):
            product = ScienceDataProduct(
                product_id=f"PROD_{i}", instrument="camera",
                priority=priority, size_mb=10.0,
                raw_size_mb=20.0, compression=CompressionType.LOSSLESS,
                timestamp=float(i)
            )
            self.dm.ingest_data(product)
        
        selected = self.dm.select_for_downlink(available_capacity_mb=25.0)
        self.assertEqual(len(selected), 2)  # CRITICAL + HIGH
        self.assertEqual(selected[0].priority, DataPriority.CRITICAL)
        self.assertEqual(selected[1].priority, DataPriority.HIGH)
        print(f"  [PASS] Downlink selection: {len(selected)} products (CRITICAL+HIGH)")
    
    def test_mark_downlinked(self):
        """Should free storage after downlink."""
        product = ScienceDataProduct(
            product_id="IMG_001", instrument="camera",
            priority=DataPriority.HIGH, size_mb=10.0,
            raw_size_mb=20.0, compression=CompressionType.LOSSLESS,
            timestamp=0.0
        )
        self.dm.ingest_data(product)
        initial_used = self.dm.used_mb
        
        self.dm.mark_downlinked(["IMG_001"])
        self.assertLess(self.dm.used_mb, initial_used)
        print(f"  [PASS] Downlink: {initial_used:.1f}MB -> {self.dm.used_mb:.1f}MB")
    
    def test_process_data(self):
        """Processing should improve quality."""
        product = ScienceDataProduct(
            product_id="IMG_001", instrument="camera",
            priority=DataPriority.HIGH, size_mb=10.0,
            raw_size_mb=20.0, compression=CompressionType.LOSSLESS,
            timestamp=0.0, quality_score=0.8
        )
        self.dm.ingest_data(product)
        
        processed = self.dm.process_data("IMG_001", processing_gain=1.2)
        self.assertIsNotNone(processed)
        self.assertTrue(processed.processed)
        self.assertGreater(processed.quality_score, 0.8)
        print(f"  [PASS] Processing: quality {0.8} -> {processed.quality_score:.3f}")
    
    def test_storage_status(self):
        """Should provide detailed storage status."""
        for i in range(3):
            product = ScienceDataProduct(
                product_id=f"PROD_{i}", instrument="camera" if i < 2 else "spectrometer",
                priority=DataPriority.HIGH, size_mb=10.0,
                raw_size_mb=20.0, compression=CompressionType.LOSSLESS,
                timestamp=float(i)
            )
            self.dm.ingest_data(product)
        
        status = self.dm.get_storage_status()
        self.assertIn("capacity_mb", status)
        self.assertIn("by_priority_mb", status)
        self.assertIn("by_instrument_mb", status)
        print(f"  [PASS] Storage status: {status['used_mb']:.1f}MB, {status['total_products']} products")
    
    def test_auto_compress(self):
        """Should auto-compress when over target utilization."""
        # Fill near capacity
        for i in range(9):
            product = ScienceDataProduct(
                product_id=f"IMG_{i:03d}", instrument="image",
                priority=DataPriority.MEDIUM, size_mb=10.0,
                raw_size_mb=20.0, compression=CompressionType.NONE,
                timestamp=float(i)
            )
            self.dm.ingest_data(product)
        
        result = self.dm.auto_compress_storage(target_utilization=0.5)
        self.assertEqual(result["action"], "compress")
        self.assertGreater(result["products_compressed"], 0)
        self.assertLess(self.dm.used_mb / self.dm.capacity_mb, 0.9)
        print(f"  [PASS] Auto-compress: {result['products_compressed']} products, freed {result['freed_mb']:.1f}MB")
    
    def test_quicklook(self):
        """Should generate quick-look metadata."""
        product = ScienceDataProduct(
            product_id="IMG_001", instrument="camera",
            priority=DataPriority.HIGH, size_mb=10.0,
            raw_size_mb=20.0, compression=CompressionType.LOSSLESS,
            timestamp=0.0, quality_score=0.95
        )
        self.dm.ingest_data(product)
        
        ql = self.dm.generate_quicklook("IMG_001")
        self.assertIsNotNone(ql)
        self.assertEqual(ql["priority"], "HIGH")
        self.assertEqual(ql["quality"], 0.95)
        print(f"  [PASS] Quicklook: {ql}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
