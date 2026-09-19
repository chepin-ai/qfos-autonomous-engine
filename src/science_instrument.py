"""
Science Instrument Module
Instrument control, data acquisition, and calibration
for autonomous scientific missions.
"""

import math
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field
from enum import Enum


class InstrumentState(Enum):
    """Instrument operational state."""
    IDLE = "idle"
    ACQUIRING = "acquiring"
    PROCESSING = "processing"
    CALIBRATING = "calibrating"
    ERROR = "error"
    STANDBY = "standby"


class DataQuality(Enum):
    """Data quality flag."""
    EXCELLENT = 1.0
    GOOD = 0.8
    FAIR = 0.5
    POOR = 0.2
    REJECT = 0.0


@dataclass
class ScienceData:
    """A science data packet."""
    instrument_id: str
    timestamp: float
    values: List[float]
    metadata: Dict[str, Any] = field(default_factory=dict)
    quality: DataQuality = DataQuality.GOOD
    calibrated: bool = False


class InstrumentController:
    """
    Control a science instrument.
    """
    
    def __init__(self, instrument_id: str, instrument_type: str):
        """
        Args:
            instrument_id: Unique instrument ID
            instrument_type: Instrument type (e.g., "spectrometer", "camera")
        """
        self.instrument_id = instrument_id
        self.instrument_type = instrument_type
        self.state = InstrumentState.IDLE
        self.config: Dict[str, Any] = {}
        self.calibration_offset = 0.0
        self.calibration_gain = 1.0
    
    def configure(self, params: Dict[str, Any]):
        """Configure instrument parameters."""
        self.config.update(params)
    
    def power_on(self):
        """Power on the instrument."""
        self.state = InstrumentState.IDLE
    
    def power_off(self):
        """Power off the instrument."""
        self.state = InstrumentState.STANDBY
    
    def start_acquisition(self, duration: float = 1.0) -> bool:
        """
        Start data acquisition.
        
        Args:
            duration: Acquisition duration (seconds)
        
        Returns:
            True if started
        """
        if self.state in (InstrumentState.IDLE, InstrumentState.STANDBY):
            self.state = InstrumentState.ACQUIRING
            return True
        return False
    
    def stop_acquisition(self):
        """Stop data acquisition."""
        if self.state == InstrumentState.ACQUIRING:
            self.state = InstrumentState.IDLE
    
    def acquire_data(self, values: List[float],
                    timestamp: float = 0.0) -> ScienceData:
        """
        Acquire and package data.
        
        Args:
            values: Raw sensor values
            timestamp: Acquisition timestamp
        
        Returns:
            Science data packet
        """
        data = ScienceData(
            instrument_id=self.instrument_id,
            timestamp=timestamp,
            values=values.copy(),
            metadata={"type": self.instrument_type, "config": self.config.copy()}
        )
        
        # Assess quality
        if len(values) == 0:
            data.quality = DataQuality.REJECT
        elif any(math.isnan(v) for v in values):
            data.quality = DataQuality.POOR
        elif any(abs(v) > 1e6 for v in values):
            data.quality = DataQuality.FAIR
        else:
            data.quality = DataQuality.GOOD
        
        self.state = InstrumentState.PROCESSING
        return data
    
    def calibrate(self, offset: float, gain: float):
        """
        Set calibration coefficients.
        
        Args:
            offset: Calibration offset
            gain: Calibration gain
        """
        self.calibration_offset = offset
        self.calibration_gain = gain
        self.state = InstrumentState.CALIBRATING
    
    def apply_calibration(self, data: ScienceData) -> ScienceData:
        """
        Apply calibration to data.
        
        Args:
            data: Raw science data
        
        Returns:
            Calibrated data
        """
        calibrated = ScienceData(
            instrument_id=data.instrument_id,
            timestamp=data.timestamp,
            values=[(v - self.calibration_offset) * self.calibration_gain
                   for v in data.values],
            metadata={**data.metadata, "calibrated": True},
            quality=data.quality,
            calibrated=True
        )
        return calibrated


class DataAcquisition:
    """
    Manage data acquisition from multiple instruments.
    """
    
    def __init__(self):
        self.instruments: Dict[str, InstrumentController] = {}
        self.data_buffer: List[ScienceData] = []
        self.buffer_limit = 1000
    
    def register_instrument(self, controller: InstrumentController):
        """Register an instrument."""
        self.instruments[controller.instrument_id] = controller
    
    def acquire_from(self, instrument_id: str,
                    values: List[float],
                    timestamp: float = 0.0) -> Optional[ScienceData]:
        """
        Acquire data from specific instrument.
        
        Args:
            instrument_id: Instrument ID
            values: Raw values
            timestamp: Timestamp
        
        Returns:
            Science data or None
        """
        inst = self.instruments.get(instrument_id)
        if not inst:
            return None
        
        data = inst.acquire_data(values, timestamp)
        self._buffer_data(data)
        return data
    
    def _buffer_data(self, data: ScienceData):
        """Add data to buffer."""
        self.data_buffer.append(data)
        if len(self.data_buffer) > self.buffer_limit:
            self.data_buffer.pop(0)
    
    def get_data_by_instrument(self, instrument_id: str
                               ) -> List[ScienceData]:
        """Get all data from instrument."""
        return [d for d in self.data_buffer
                if d.instrument_id == instrument_id]
    
    def get_data_by_quality(self, min_quality: DataQuality
                           ) -> List[ScienceData]:
        """Get data above quality threshold."""
        return [d for d in self.data_buffer
                if d.quality.value >= min_quality.value]
    
    def buffer_size(self) -> int:
        """Get buffer size."""
        return len(self.data_buffer)
    
    def clear_buffer(self):
        """Clear data buffer."""
        self.data_buffer.clear()


class CalibrationEngine:
    """
    Manage instrument calibration.
    """
    
    def __init__(self):
        self.calibration_data: Dict[str, List[Tuple[float, float]]] = {}
        # instrument_id -> [(raw, reference)]
    
    def add_calibration_point(self, instrument_id: str,
                             raw: float, reference: float):
        """Add calibration data point."""
        if instrument_id not in self.calibration_data:
            self.calibration_data[instrument_id] = []
        self.calibration_data[instrument_id].append((raw, reference))
    
    def compute_calibration(self, instrument_id: str
                           ) -> Optional[Tuple[float, float]]:
        """
        Compute calibration coefficients from data.
        
        Args:
            instrument_id: Instrument ID
        
        Returns:
            (offset, gain) or None
        """
        points = self.calibration_data.get(instrument_id, [])
        if len(points) < 2:
            return None
        
        # Linear regression: reference = gain * raw + offset
        n = len(points)
        sum_r = sum(r for r, _ in points)
        sum_ref = sum(ref for _, ref in points)
        sum_rr = sum(r * r for r, _ in points)
        sum_rref = sum(r * ref for r, ref in points)
        
        denom = n * sum_rr - sum_r**2
        if abs(denom) < 1e-15:
            return None
        
        gain = (n * sum_rref - sum_r * sum_ref) / denom
        offset = (sum_ref - gain * sum_r) / n
        
        return (offset, gain)
    
    def apply_to_instrument(self, instrument: InstrumentController):
        """Apply computed calibration to instrument."""
        coeffs = self.compute_calibration(instrument.instrument_id)
        if coeffs:
            instrument.calibrate(coeffs[0], coeffs[1])


class ScienceInstrument:
    """
    Unified science instrument controller.
    """
    
    def __init__(self):
        self.daq = DataAcquisition()
        self.calibration = CalibrationEngine()
    
    def register(self, instrument_id: str, instrument_type: str):
        """Register a new instrument."""
        ctrl = InstrumentController(instrument_id, instrument_type)
        self.daq.register_instrument(ctrl)
    
    def configure(self, instrument_id: str, params: Dict[str, Any]):
        """Configure instrument."""
        inst = self.daq.instruments.get(instrument_id)
        if inst:
            inst.configure(params)
    
    def acquire(self, instrument_id: str, values: List[float],
               timestamp: float = 0.0) -> Optional[ScienceData]:
        """Acquire data from instrument."""
        return self.daq.acquire_from(instrument_id, values, timestamp)
    
    def calibrate_instrument(self, instrument_id: str):
        """Apply calibration to instrument."""
        inst = self.daq.instruments.get(instrument_id)
        if inst:
            self.calibration.apply_to_instrument(inst)
    
    def get_quality_data(self, min_quality: DataQuality = DataQuality.GOOD
                        ) -> List[ScienceData]:
        """Get quality-filtered data."""
        return self.daq.get_data_by_quality(min_quality)
    
    def instrument_summary(self, instrument_id: str) -> Dict:
        """Get instrument summary."""
        inst = self.daq.instruments.get(instrument_id)
        if not inst:
            return {}
        return {
            "id": inst.instrument_id,
            "type": inst.instrument_type,
            "state": inst.state.value,
            "buffered_data": len(self.daq.get_data_by_instrument(instrument_id)),
            "calibrated": inst.calibration_gain != 1.0 or inst.calibration_offset != 0.0
        }
    
    def science_summary(self) -> Dict:
        """Get overall science summary."""
        return {
            "instruments": len(self.daq.instruments),
            "buffered_packets": self.daq.buffer_size(),
            "calibration_points": sum(len(v) for v in self.calibration.calibration_data.values())
        }
