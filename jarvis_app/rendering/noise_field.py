from __future__ import annotations

import numpy as np


class NoiseField:
    """Lightweight pseudo-Perlin noise field for vectorized deformation."""

    def sample(self, x: np.ndarray, y: np.ndarray, z: np.ndarray, t: float) -> np.ndarray:
        n1 = np.sin((x * 2.9) + (y * 2.1) + (z * 1.7) + (t * 0.55))
        n2 = np.cos((x * 4.2) - (y * 3.8) + (z * 2.6) - (t * 0.47))
        n3 = np.sin((x * 1.8) - (y * 5.0) - (z * 2.4) + (t * 0.71))
        return (n1 + n2 + n3) / 3.0
