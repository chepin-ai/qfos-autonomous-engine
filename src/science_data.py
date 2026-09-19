"""
Science Data Management Module
Handle science data collection, processing, compression, and prioritization.
"""

import math
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum


class DataPriority(Enum):
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4
    DUMP = 5


class CompressionType(Enum):
    NONE = "none"
    LOSSLESS = "lossless"
    LOSSY = "lossy"


@dataclass
class ScienceDataProduct:
    """A science data product from an instrument."""
    product_id: str
    instrument: str
    priority: DataPriority
    size_mb: float
    raw_size_mb: float
    compression: CompressionType
    timestamp: float
    quality_score: float = 1.0  # 0.0 to 1.0
    downlinked: bool = False
    processed: bool = False


class DataCompressor:
    """
    Simulate data compression for science products.
    """
    
    # Typical compression ratios
    COMPRESSION_RATIOS = {
        ("image", CompressionType.LOSSLESS): 2.0,
        ("image", CompressionType.LOSSY): 10.0,
        ("spectrum", CompressionType.LOSSLESS): 3.0,
        ("spectrum", CompressionType.LOSSY): 5.0,
        ("timeseries", CompressionType.LOSSLESS): 5.0,
        ("timeseries", CompressionType.LOSSY): 20.0,
    }
    
    def compress(self, data_type: str, raw_size_mb: float,
                 compression: CompressionType) -> Tuple[float, float]:
        """
        Compress data and return compressed size + quality factor.
        
        Returns:
            (compressed_size_mb, quality_retention)
        """
        if compression == CompressionType.NONE:
            return raw_size_mb, 1.0
        
        ratio = self.COMPRESSION_RATIOS.get(
            (data_type, compression), 2.0
        )
        
        compressed = raw_size_mb / ratio
        
        # Quality retention
        if compression == CompressionType.LOSSLESS:
            quality = 1.0
        else:
            quality = 0.85 + 0.1 / ratio  # Better ratio = slightly worse quality
        
        return compressed, quality
    
    def estimate_size(self, data_type: str, raw_size_mb: float,
                      compression: CompressionType) -> float:
        """Estimate compressed size without quality info."""
        size, _ = self.compress(data_type, raw_size_mb, compression)
        return size


class ScienceDataManager:
    """
    Manage science data lifecycle from collection to downlink.
    """
    
    def __init__(self, storage_capacity_mb: float = 10000.0):
        self.capacity_mb = storage_capacity_mb
        self.used_mb = 0.0
        self.products: Dict[str, ScienceDataProduct] = {}
        self.compressor = DataCompressor()
        self.downlinked_mb = 0.0
    
    def ingest_data(self, product: ScienceDataProduct) -> bool:
        """
        Ingest a new science data product.
        
        Returns:
            True if successfully stored
        """
        if self.used_mb + product.size_mb > self.capacity_mb:
            # Try to make room by deleting lowest priority un-downlinked data
            if not self._make_room(product.size_mb):
                return False
        
        self.products[product.product_id] = product
        self.used_mb += product.size_mb
        return True
    
    def _make_room(self, required_mb: float) -> bool:
        """Delete low priority data to make room."""
        # Sort by priority (low first) and downlink status
        candidates = sorted(
            [p for p in self.products.values() if not p.downlinked],
            key=lambda x: (x.priority.value, x.quality_score),
            reverse=True  # Lowest priority first for deletion
        )
        
        freed = 0.0
        for p in candidates:
            if freed >= required_mb:
                break
            freed += p.size_mb
            self.used_mb -= p.size_mb
            del self.products[p.product_id]
        
        return freed >= required_mb
    
    def process_data(self, product_id: str, 
                     processing_gain: float = 1.2) -> Optional[ScienceDataProduct]:
        """
        Process raw data to enhance quality.
        
        Args:
            product_id: Data product to process
            processing_gain: Quality improvement factor
        
        Returns:
            Updated product or None
        """
        if product_id not in self.products:
            return None
        
        product = self.products[product_id]
        product.processed = True
        product.quality_score = min(1.0, product.quality_score * processing_gain)
        
        return product
    
    def select_for_downlink(self, available_capacity_mb: float) -> List[ScienceDataProduct]:
        """
        Select data products for downlink based on priority and quality.
        
        Returns:
            List of products to downlink
        """
        # Sort by priority (critical first), then quality
        candidates = sorted(
            [p for p in self.products.values() if not p.downlinked],
            key=lambda x: (x.priority.value, -x.quality_score)
        )
        
        selected = []
        remaining = available_capacity_mb
        
        for product in candidates:
            if product.size_mb <= remaining:
                selected.append(product)
                remaining -= product.size_mb
            else:
                break
        
        return selected
    
    def mark_downlinked(self, product_ids: List[str]):
        """Mark products as successfully downlinked."""
        for pid in product_ids:
            if pid in self.products:
                self.products[pid].downlinked = True
                self.used_mb -= self.products[pid].size_mb
                self.downlinked_mb += self.products[pid].size_mb
    
    def get_storage_status(self) -> Dict:
        """Get current storage status."""
        by_priority = {p: 0.0 for p in DataPriority}
        by_instrument: Dict[str, float] = {}
        
        for product in self.products.values():
            if not product.downlinked:
                by_priority[product.priority] += product.size_mb
                by_instrument[product.instrument] = by_instrument.get(product.instrument, 0.0) + product.size_mb
        
        return {
            "capacity_mb": self.capacity_mb,
            "used_mb": round(self.used_mb, 2),
            "free_mb": round(self.capacity_mb - self.used_mb, 2),
            "utilization_percent": round(self.used_mb / self.capacity_mb * 100, 1),
            "total_products": len(self.products),
            "pending_downlink": sum(1 for p in self.products.values() if not p.downlinked),
            "by_priority_mb": {k.name: round(v, 2) for k, v in by_priority.items()},
            "by_instrument_mb": {k: round(v, 2) for k, v in by_instrument.items()},
            "downlinked_total_mb": round(self.downlinked_mb, 2)
        }
    
    def generate_quicklook(self, product_id: str) -> Optional[Dict]:
        """
        Generate a quick-look summary of a data product.
        
        Returns:
            Quick-look metadata
        """
        if product_id not in self.products:
            return None
        
        product = self.products[product_id]
        
        return {
            "product_id": product.product_id,
            "instrument": product.instrument,
            "priority": product.priority.name,
            "size_mb": product.size_mb,
            "compression": product.compression.value,
            "quality": round(product.quality_score, 3),
            "processed": product.processed,
            "ready_for_downlink": not product.downlinked
        }
    
    def auto_compress_storage(self, target_utilization: float = 0.8) -> Dict:
        """
        Automatically compress data to reduce storage usage.
        
        Returns:
            Compression results
        """
        if self.used_mb / self.capacity_mb <= target_utilization:
            return {"action": "none", "reason": "utilization_below_target"}
        
        compressed_count = 0
        freed_mb = 0.0
        
        for product in self.products.values():
            if product.downlinked:
                continue
            
            if product.compression == CompressionType.NONE and product.priority.value >= 3:
                # Compress medium/low priority data with lossy compression
                new_size, quality = self.compressor.compress(
                    product.instrument, product.raw_size_mb, CompressionType.LOSSY
                )
                
                if new_size < product.size_mb:
                    freed_mb += product.size_mb - new_size
                    self.used_mb -= product.size_mb - new_size
                    product.size_mb = new_size
                    product.compression = CompressionType.LOSSY
                    product.quality_score *= quality
                    compressed_count += 1
        
        return {
            "action": "compress",
            "products_compressed": compressed_count,
            "freed_mb": round(freed_mb, 2),
            "new_utilization_percent": round(self.used_mb / self.capacity_mb * 100, 1)
        }
