"""
Communication Link Budget Module
RF communication link analysis for deep space missions.
"""

import math
from typing import Dict, Tuple
from dataclasses import dataclass


@dataclass
class LinkBudgetResult:
    """Result of a link budget calculation."""
    carrier_frequency_hz: float
    wavelength_m: float
    path_loss_db: float
    received_power_dbm: float
    noise_power_dbm: float
    snr_db: float
    eb_no_db: float
    margin_db: float
    data_rate_bps: float
    status: str  # 'OK' or 'MARGINAL' or 'FAIL'


class LinkBudgetCalculator:
    """
    Calculate RF link budget for spacecraft-ground communication.
    
    Supports S-band, X-band, and Ka-band communications.
    """
    
    # Physical constants
    BOLTZMANN = 1.380649e-23  # J/K
    C = 299792458.0  # m/s
    
    # Standard bands
    BANDS = {
        'S': {'freq_ghz': 2.29, 'typical_dish_m': 3.0},
        'X': {'freq_ghz': 8.4, 'typical_dish_m': 3.0},
        'Ka': {'freq_ghz': 32.0, 'typical_dish_m': 1.0},
    }
    
    def __init__(self, system_noise_temp_k: float = 290.0):
        self.T_sys = system_noise_temp_k
    
    def calculate_link(self,
                       tx_power_w: float,
                       tx_dish_diameter_m: float,
                       rx_dish_diameter_m: float,
                       distance_km: float,
                       frequency_ghz: float,
                       data_rate_bps: float,
                       tx_efficiency: float = 0.55,
                       rx_efficiency: float = 0.55,
                       required_margin_db: float = 3.0) -> LinkBudgetResult:
        """
        Calculate complete link budget.
        
        Args:
            tx_power_w: Transmitter power (W)
            tx_dish_diameter_m: Transmit antenna diameter (m)
            rx_dish_diameter_m: Receive antenna diameter (m)
            distance_km: Distance between transmitter and receiver (km)
            frequency_ghz: Carrier frequency (GHz)
            data_rate_bps: Data rate (bits/s)
            tx_efficiency: Transmit antenna efficiency
            rx_efficiency: Receive antenna efficiency
            required_margin_db: Required link margin (dB)
        
        Returns:
            LinkBudgetResult with all calculated parameters
        """
        # Frequency and wavelength
        f_hz = frequency_ghz * 1e9
        wavelength = self.C / f_hz
        
        # Antenna gains (parabolic dish)
        tx_gain_db = self._parabolic_gain(tx_dish_diameter_m, wavelength, tx_efficiency)
        rx_gain_db = self._parabolic_gain(rx_dish_diameter_m, wavelength, rx_efficiency)
        
        # Free space path loss
        distance_m = distance_km * 1000.0
        path_loss_db = 20.0 * math.log10(4.0 * math.pi * distance_m / wavelength)
        
        # Transmit power in dBm
        tx_power_dbm = 10.0 * math.log10(tx_power_w * 1000.0)
        
        # Effective isotropic radiated power
        eirp_dbm = tx_power_dbm + tx_gain_db
        
        # Received power
        rx_power_dbm = eirp_dbm - path_loss_db + rx_gain_db
        
        # Noise power
        noise_power_dbm = 10.0 * math.log10(self.BOLTZMANN * self.T_sys * data_rate_bps * 1000.0)
        
        # Signal-to-noise ratio
        snr_db = rx_power_dbm - noise_power_dbm
        
        # Energy per bit to noise density (Eb/N0)
        # Assuming data_rate_bps is the noise bandwidth
        eb_no_db = snr_db  # Simplified: for digital comm, Eb/N0 = SNR when BW = data rate
        
        # Link margin
        # Typical required Eb/N0 for BPSK ~ 10 dB, QPSK ~ 13 dB
        required_eb_no_db = 10.0  # BPSK with moderate coding
        margin_db = eb_no_db - required_eb_no_db
        
        if margin_db >= required_margin_db:
            status = 'OK'
        elif margin_db >= 0:
            status = 'MARGINAL'
        else:
            status = 'FAIL'
        
        return LinkBudgetResult(
            carrier_frequency_hz=f_hz,
            wavelength_m=wavelength,
            path_loss_db=path_loss_db,
            received_power_dbm=rx_power_dbm,
            noise_power_dbm=noise_power_dbm,
            snr_db=snr_db,
            eb_no_db=eb_no_db,
            margin_db=margin_db,
            data_rate_bps=data_rate_bps,
            status=status
        )
    
    def _parabolic_gain(self, diameter_m: float, wavelength_m: float, 
                        efficiency: float = 0.55) -> float:
        """Calculate parabolic dish gain in dBi."""
        area = math.pi * (diameter_m / 2.0)**2
        gain = efficiency * 4.0 * math.pi * area / (wavelength_m**2)
        return 10.0 * math.log10(gain)
    
    def calculate_for_mission_phase(self, phase: str, 
                                    distance_km: float,
                                    data_rate_bps: float,
                                    tx_power_w: float = 20.0) -> LinkBudgetResult:
        """
        Quick link budget for standard mission phases.
        
        Args:
            phase: 'launch', 'cruise', 'approach', 'surface', 'emergency'
            distance_km: Current distance to Earth
            data_rate_bps: Required data rate
            tx_power_w: Transmitter power
        """
        configs = {
            'launch': {'band': 'S', 'tx_dish': 1.0, 'rx_dish': 34.0},
            'cruise': {'band': 'X', 'tx_dish': 3.0, 'rx_dish': 70.0},
            'approach': {'band': 'X', 'tx_dish': 3.0, 'rx_dish': 34.0},
            'surface': {'band': 'UHF', 'tx_dish': 0.5, 'rx_dish': 10.0},
            'emergency': {'band': 'S', 'tx_dish': 0.5, 'rx_dish': 70.0},
        }
        
        config = configs.get(phase, configs['cruise'])
        
        # Map band to frequency
        band_freqs = {'S': 2.29, 'X': 8.4, 'Ka': 32.0, 'UHF': 0.4}
        freq_ghz = band_freqs.get(config['band'], 8.4)
        
        return self.calculate_link(
            tx_power_w=tx_power_w,
            tx_dish_diameter_m=config['tx_dish'],
            rx_dish_diameter_m=config['rx_dish'],
            distance_km=distance_km,
            frequency_ghz=freq_ghz,
            data_rate_bps=data_rate_bps
        )
    
    def max_data_rate(self,
                      tx_power_w: float,
                      tx_dish_diameter_m: float,
                      rx_dish_diameter_m: float,
                      distance_km: float,
                      frequency_ghz: float,
                      min_margin_db: float = 3.0) -> float:
        """
        Calculate maximum achievable data rate for given link parameters.
        
        Returns:
            Maximum data rate in bits per second
        """
        # Work backwards from required Eb/N0
        required_eb_no_db = 10.0 + min_margin_db  # BPSK + margin
        
        # Calculate available signal power
        result = self.calculate_link(
            tx_power_w=tx_power_w,
            tx_dish_diameter_m=tx_dish_diameter_m,
            rx_dish_diameter_m=rx_dish_diameter_m,
            distance_km=distance_km,
            frequency_ghz=frequency_ghz,
            data_rate_bps=1.0  # Placeholder, will recalculate
        )
        
        # Eb/N0 = Pr / (k * T * data_rate)
        # data_rate = Pr / (k * T * 10^(EbN0_required/10))
        pr_watts = 10.0 ** ((result.received_power_dbm - 30.0) / 10.0)
        required_eb_no_linear = 10.0 ** (required_eb_no_db / 10.0)
        
        max_rate = pr_watts / (self.BOLTZMANN * self.T_sys * required_eb_no_linear)
        
        return max_rate
