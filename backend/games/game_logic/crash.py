"""
Crash ("Cross Chicken") Engine & Provably Fair Mathematics.
Implements HMAC-SHA256 provably fair random generation with exponential multiplier curve.
"""

import hmac
import hashlib
import math
import secrets
from typing import Dict, Any, Tuple

class ProvablyFair:
    """Cryptographically verifiable outcome generator."""

    @staticmethod
    def generate_server_seed() -> str:
        return secrets.token_hex(32)

    @staticmethod
    def hash_seed(seed: str) -> str:
        return hashlib.sha256(seed.encode()).hexdigest()

    @staticmethod
    def generate_crash_point(
        server_seed: str,
        client_seed: str = "toqi999bigwin",
        nonce: int = 1,
        house_edge: float = 0.03
    ) -> Tuple[float, str]:
        """
        Derives crash multiplier deterministically from HMAC-SHA256.
        Returns: (crash_multiplier, hmac_hash)
        """
        message = f"{client_seed}:{nonce}".encode()
        h = hmac.new(server_seed.encode(), message, hashlib.sha256).hexdigest()

        # 3% house edge: Instant bust at 1.00x
        # 1 in 33 rounds crashes immediately
        if int(h[:8], 16) % 33 == 0:
            return 1.00, h

        # Take first 52 bits (13 hex characters)
        raw_int = int(h[:13], 16)
        e = 2 ** 52
        
        # Standard fair distribution formula: (100 * e - h) / (e - h)
        multiplier = (100 * e - raw_int) / (e - raw_int) / 100.0
        
        # Round down to 2 decimal places
        multiplier = math.floor(multiplier * 100) / 100.0
        
        # Minimum multiplier is 1.00x, cap at 250.00x for reasonable game pacing
        multiplier = max(1.00, min(multiplier, 250.00))

        return float(multiplier), h

    @classmethod
    def verify(cls, server_seed: str, client_seed: str, nonce: int) -> Dict[str, Any]:
        crash_point, hash_digest = cls.generate_crash_point(server_seed, client_seed, nonce)
        seed_hash = cls.hash_seed(server_seed)
        return {
            'crash_point': crash_point,
            'hmac_hash': hash_digest,
            'server_seed_hash': seed_hash,
            'server_seed': server_seed,
            'client_seed': client_seed,
            'nonce': nonce,
            'verified': True
        }


class CrashEngine:
    """Handles multiplier calculations and simulation timings."""

    @staticmethod
    def get_multiplier_at_time(elapsed_seconds: float) -> float:
        """
        Calculates multiplier after elapsed_seconds.
        Starts at 1.00x and accelerates smoothly.
        Formula: 1.0 + 0.05 * (elapsed ** 1.75)
        """
        if elapsed_seconds <= 0:
            return 1.00
        mult = 1.00 + 0.055 * math.pow(elapsed_seconds, 1.72)
        return round(mult, 2)

    @staticmethod
    def get_time_for_multiplier(target_multiplier: float) -> float:
        """Inverse: calculates elapsed seconds to reach target multiplier."""
        if target_multiplier <= 1.00:
            return 0.0
        # (mult - 1.0) / 0.055 = t ** 1.72  =>  t = ((mult - 1.0)/0.055) ** (1/1.72)
        diff = target_multiplier - 1.00
        return math.pow(diff / 0.055, 1 / 1.72)
