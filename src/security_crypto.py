"""
Security Cryptography Module
Encryption, digital signatures, and key management
for secure spacecraft communications.
"""

import hashlib
import hmac
import secrets
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class KeyPair:
    """Asymmetric key pair."""
    public_key: str
    private_key: str


class SymmetricCipher:
    """
    Simple symmetric encryption using XOR + HMAC.
    
    For demonstration - production should use AES-GCM.
    """
    
    def __init__(self, key: Optional[bytes] = None):
        """
        Args:
            key: 32-byte encryption key
        """
        self.key = key or secrets.token_bytes(32)
    
    def encrypt(self, plaintext: str) -> Tuple[bytes, bytes]:
        """
        Encrypt plaintext.
        
        Args:
            plaintext: Text to encrypt
        
        Returns:
            (ciphertext, mac)
        """
        data = plaintext.encode('utf-8')
        iv = secrets.token_bytes(16)
        
        # XOR with keystream (simplified)
        keystream = hashlib.sha256(iv + self.key).digest()
        ciphertext = bytes(b ^ keystream[i % len(keystream)] for i, b in enumerate(data))
        
        # HMAC for integrity
        mac = hmac.new(self.key, iv + ciphertext, hashlib.sha256).digest()
        
        return iv + ciphertext, mac
    
    def decrypt(self, ciphertext: bytes, mac: bytes) -> Optional[str]:
        """
        Decrypt ciphertext.
        
        Args:
            ciphertext: IV + encrypted data
            mac: HMAC for verification
        
        Returns:
            Decrypted text or None
        """
        if len(ciphertext) < 16:
            return None
        
        iv = ciphertext[:16]
        encrypted = ciphertext[16:]
        
        # Verify MAC
        expected_mac = hmac.new(self.key, iv + encrypted, hashlib.sha256).digest()
        if not hmac.compare_digest(mac, expected_mac):
            return None
        
        # Decrypt
        keystream = hashlib.sha256(iv + self.key).digest()
        plaintext = bytes(b ^ keystream[i % len(keystream)] for i, b in enumerate(encrypted))
        
        try:
            return plaintext.decode('utf-8')
        except UnicodeDecodeError:
            return None


class DigitalSignature:
    """
    Digital signature using hash-based scheme.
    
    Simplified Lamport-like signature for demonstration.
    """
    
    def __init__(self):
        self.key_size = 256
    
    def generate_keypair(self) -> KeyPair:
        """Generate a new key pair."""
        private = secrets.token_hex(64)
        public = hashlib.sha256(private.encode()).hexdigest()
        return KeyPair(public_key=public, private_key=private)
    
    def sign(self, message: str, private_key: str) -> str:
        """
        Sign a message.
        
        Args:
            message: Message to sign
            private_key: Private key
        
        Returns:
            Signature hex string
        """
        data = message.encode('utf-8')
        key_data = private_key.encode('utf-8')
        signature = hmac.new(key_data, data, hashlib.sha256).hexdigest()
        return signature
    
    def verify(self, message: str, signature: str,
              public_key: str, private_key: str) -> bool:
        """
        Verify a signature.
        
        Args:
            message: Original message
            signature: Signature to verify
            public_key: Public key
            private_key: Private key (for this simplified scheme)
        
        Returns:
            Validity
        """
        expected = self.sign(message, private_key)
        return hmac.compare_digest(signature, expected)


class KeyManager:
    """
    Key lifecycle management.
    
    Handles generation, rotation, and revocation.
    """
    
    def __init__(self):
        self.keys: Dict[str, Dict] = {}
        self.signer = DigitalSignature()
    
    def generate_key(self, key_id: str, key_type: str = "symmetric") -> Dict:
        """
        Generate a new key.
        
        Args:
            key_id: Key identifier
            key_type: "symmetric" or "asymmetric"
        
        Returns:
            Key metadata
        """
        if key_type == "symmetric":
            key_data = secrets.token_hex(32)
        else:
            kp = self.signer.generate_keypair()
            key_data = {"public": kp.public_key, "private": kp.private_key}
        
        self.keys[key_id] = {
            "type": key_type,
            "data": key_data,
            "created": self._timestamp(),
            "status": "active",
            "usage_count": 0
        }
        
        return self.keys[key_id]
    
    def get_key(self, key_id: str) -> Optional[Dict]:
        """Get key by ID."""
        return self.keys.get(key_id)
    
    def revoke_key(self, key_id: str) -> bool:
        """Revoke a key."""
        if key_id in self.keys:
            self.keys[key_id]["status"] = "revoked"
            return True
        return False
    
    def rotate_key(self, key_id: str) -> Optional[Dict]:
        """
        Rotate a key.
        
        Args:
            key_id: Key to rotate
        
        Returns:
            New key metadata
        """
        if key_id not in self.keys:
            return None
        
        old_key = self.keys[key_id]
        new_id = f"{key_id}_v{self._get_version(key_id) + 1}"
        
        return self.generate_key(new_id, old_key["type"])
    
    def _get_version(self, key_id: str) -> int:
        """Extract version from key ID."""
        parts = key_id.split("_v")
        if len(parts) > 1 and parts[-1].isdigit():
            return int(parts[-1])
        return 1
    
    def _timestamp(self) -> int:
        """Get current timestamp."""
        import time
        return int(time.time())
    
    def key_summary(self) -> Dict:
        """Get key management summary."""
        active = sum(1 for k in self.keys.values() if k["status"] == "active")
        revoked = sum(1 for k in self.keys.values() if k["status"] == "revoked")
        
        return {
            "total_keys": len(self.keys),
            "active": active,
            "revoked": revoked
        }


class SecureChannel:
    """
    Secure communication channel.
    
    Combines encryption and authentication.
    """
    
    def __init__(self, cipher: Optional[SymmetricCipher] = None):
        self.cipher = cipher or SymmetricCipher()
        self.sequence_number = 0
        self.message_log: List[Dict] = []
    
    def send(self, message: str) -> Dict:
        """
        Securely send a message.
        
        Args:
            message: Plaintext message
        
        Returns:
            Packet dict
        """
        ciphertext, mac = self.cipher.encrypt(message)
        
        packet = {
            "seq": self.sequence_number,
            "data": ciphertext.hex(),
            "mac": mac.hex()
        }
        
        self.sequence_number += 1
        self.message_log.append({"seq": packet["seq"], "type": "sent"})
        
        return packet
    
    def receive(self, packet: Dict) -> Optional[str]:
        """
        Receive and decrypt a message.
        
        Args:
            packet: Received packet
        
        Returns:
            Decrypted message or None
        """
        try:
            ciphertext = bytes.fromhex(packet["data"])
            mac = bytes.fromhex(packet["mac"])
        except (KeyError, ValueError):
            return None
        
        plaintext = self.cipher.decrypt(ciphertext, mac)
        
        if plaintext:
            self.message_log.append({"seq": packet.get("seq", -1), "type": "received"})
        
        return plaintext
    
    def channel_stats(self) -> Dict:
        """Get channel statistics."""
        sent = sum(1 for m in self.message_log if m["type"] == "sent")
        received = sum(1 for m in self.message_log if m["type"] == "received")
        
        return {
            "messages_sent": sent,
            "messages_received": received,
            "sequence_number": self.sequence_number
        }
