"""
Zero Trust Module
Zero-trust access control, attestation, and
policy engine for spacecraft security.
"""

import time
import hashlib
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass, field
from enum import Enum


class TrustLevel(Enum):
    """Trust classification levels."""
    UNTRUSTED = 0
    UNVERIFIED = 1
    VERIFIED = 2
    TRUSTED = 3
    HIGHLY_TRUSTED = 4


@dataclass
class DeviceIdentity:
    """Identity of a device in the zero-trust network."""
    device_id: str
    public_key_hash: str
    attestation_score: float = 0.0
    last_attestation: float = 0.0
    trust_level: TrustLevel = TrustLevel.UNVERIFIED
    capabilities: List[str] = field(default_factory=list)


@dataclass
class AccessPolicy:
    """Access control policy."""
    resource: str
    required_trust: TrustLevel
    required_capabilities: List[str] = field(default_factory=list)
    time_restrictions: Optional[Tuple[float, float]] = None


class AttestationEngine:
    """
    Device attestation engine.
    
    Verifies device integrity through challenge-response.
    """
    
    def __init__(self):
        self.challenges: Dict[str, Dict] = {}
        self.attestation_history: Dict[str, List[float]] = {}
    
    def generate_challenge(self, device_id: str) -> str:
        """
        Generate attestation challenge.
        
        Args:
            device_id: Device to challenge
        
        Returns:
            Challenge string
        """
        import secrets
        challenge = secrets.token_hex(32)
        self.challenges[device_id] = {
            "challenge": challenge,
            "timestamp": time.time(),
            "expires": time.time() + 300.0
        }
        return challenge
    
    def verify_response(self, device_id: str, response: str,
                       expected_hash: str) -> bool:
        """
        Verify attestation response.
        
        Args:
            device_id: Device ID
            response: Response to verify
            expected_hash: Expected response hash
        
        Returns:
            Validity
        """
        if device_id not in self.challenges:
            return False
        
        challenge_info = self.challenges[device_id]
        
        if time.time() > challenge_info["expires"]:
            return False
        
        # Verify response hash
        expected = hashlib.sha256(
            (challenge_info["challenge"] + expected_hash).encode()
        ).hexdigest()
        
        valid = response == expected
        
        if valid:
            if device_id not in self.attestation_history:
                self.attestation_history[device_id] = []
            self.attestation_history[device_id].append(time.time())
        
        return valid
    
    def get_attestation_score(self, device_id: str) -> float:
        """
        Calculate attestation score.
        
        Args:
            device_id: Device ID
        
        Returns:
            Score 0.0-1.0
        """
        history = self.attestation_history.get(device_id, [])
        
        if not history:
            return 0.0
        
        # Score based on attestation frequency and recency
        now = time.time()
        recent = [t for t in history if now - t < 86400]  # 24 hours
        
        if not recent:
            return 0.1
        
        # More attestations = higher score, decay with time
        score = min(1.0, len(recent) / 10.0)
        last_age = (now - recent[-1]) / 3600.0  # hours
        decay = max(0.0, 1.0 - last_age / 24.0)
        
        return score * decay


class PolicyEngine:
    """
    Zero-trust policy engine.
    
    Evaluates access requests against policies.
    """
    
    def __init__(self):
        self.policies: Dict[str, AccessPolicy] = {}
        self.access_log: List[Dict] = []
    
    def add_policy(self, policy: AccessPolicy):
        """Add an access policy."""
        self.policies[policy.resource] = policy
    
    def evaluate(self, device: DeviceIdentity,
                resource: str, action: str = "read") -> Dict:
        """
        Evaluate access request.
        
        Args:
            device: Requesting device
            resource: Requested resource
            action: Requested action
        
        Returns:
            Decision dict
        """
        if resource not in self.policies:
            return {"granted": False, "reason": "no_policy"}
        
        policy = self.policies[resource]
        
        # Check trust level
        if device.trust_level.value < policy.required_trust.value:
            self._log_access(device.device_id, resource, action, False, "insufficient_trust")
            return {
                "granted": False,
                "reason": "insufficient_trust",
                "required": policy.required_trust.name,
                "actual": device.trust_level.name
            }
        
        # Check capabilities
        missing_caps = [cap for cap in policy.required_capabilities
                       if cap not in device.capabilities]
        
        if missing_caps:
            self._log_access(device.device_id, resource, action, False, "missing_capabilities")
            return {
                "granted": False,
                "reason": "missing_capabilities",
                "missing": missing_caps
            }
        
        # Check time restrictions
        if policy.time_restrictions:
            now = time.time()
            if not (policy.time_restrictions[0] <= now <= policy.time_restrictions[1]):
                self._log_access(device.device_id, resource, action, False, "time_restricted")
                return {"granted": False, "reason": "time_restricted"}
        
        self._log_access(device.device_id, resource, action, True, "authorized")
        return {"granted": True, "reason": "authorized"}
    
    def _log_access(self, device_id: str, resource: str,
                   action: str, granted: bool, reason: str):
        """Log access attempt."""
        self.access_log.append({
            "timestamp": time.time(),
            "device": device_id,
            "resource": resource,
            "action": action,
            "granted": granted,
            "reason": reason
        })
    
    def get_access_stats(self) -> Dict:
        """Get access statistics."""
        total = len(self.access_log)
        granted = sum(1 for e in self.access_log if e["granted"])
        denied = total - granted
        
        return {
            "total_requests": total,
            "granted": granted,
            "denied": denied,
            "grant_rate": round(granted / max(1, total), 2)
        }


class ZeroTrustController:
    """
    Unified zero-trust controller.
    
    Combines attestation and policy evaluation.
    """
    
    def __init__(self):
        self.attestation = AttestationEngine()
        self.policy = PolicyEngine()
        self.devices: Dict[str, DeviceIdentity] = {}
    
    def register_device(self, device_id: str,
                       public_key_hash: str,
                       capabilities: Optional[List[str]] = None) -> DeviceIdentity:
        """
        Register a new device.
        
        Args:
            device_id: Device identifier
            public_key_hash: Hash of public key
            capabilities: Device capabilities
        
        Returns:
            Device identity
        """
        device = DeviceIdentity(
            device_id=device_id,
            public_key_hash=public_key_hash,
            capabilities=capabilities or []
        )
        self.devices[device_id] = device
        return device
    
    def update_trust(self, device_id: str):
        """
        Update device trust level based on attestation.
        
        Args:
            device_id: Device to update
        """
        if device_id not in self.devices:
            return
        
        device = self.devices[device_id]
        score = self.attestation.get_attestation_score(device_id)
        device.attestation_score = score
        device.last_attestation = time.time()
        
        # Update trust level based on score
        if score >= 0.9:
            device.trust_level = TrustLevel.HIGHLY_TRUSTED
        elif score >= 0.7:
            device.trust_level = TrustLevel.TRUSTED
        elif score >= 0.4:
            device.trust_level = TrustLevel.VERIFIED
        elif score >= 0.1:
            device.trust_level = TrustLevel.UNVERIFIED
        else:
            device.trust_level = TrustLevel.UNTRUSTED
    
    def request_access(self, device_id: str,
                      resource: str, action: str = "read") -> Dict:
        """
        Process access request.
        
        Args:
            device_id: Requesting device
            resource: Requested resource
            action: Requested action
        
        Returns:
            Access decision
        """
        if device_id not in self.devices:
            return {"granted": False, "reason": "unknown_device"}
        
        device = self.devices[device_id]
        
        # Update trust before evaluation
        self.update_trust(device_id)
        
        return self.policy.evaluate(device, resource, action)
    
    def get_device_status(self, device_id: str) -> Optional[Dict]:
        """Get device security status."""
        if device_id not in self.devices:
            return None
        
        device = self.devices[device_id]
        
        return {
            "device_id": device.device_id,
            "trust_level": device.trust_level.name,
            "attestation_score": round(device.attestation_score, 2),
            "capabilities": device.capabilities,
            "last_attestation": device.last_attestation
        }
    
    def network_summary(self) -> Dict:
        """Get zero-trust network summary."""
        trust_levels = {level.name: 0 for level in TrustLevel}
        for device in self.devices.values():
            trust_levels[device.trust_level.name] += 1
        
        return {
            "devices": len(self.devices),
            "trust_distribution": trust_levels,
            "access_stats": self.policy.get_access_stats()
        }
