from __future__ import annotations

import numpy as np


class NoiseGenerator:
    """Fast deterministic pseudo-3D noise for particle deformation."""

    def sample(self, x: np.ndarray, y: np.ndarray, z: np.ndarray, t: float) -> np.ndarray:
        # Blend harmonic fields to avoid directional artifacts.
        n1 = np.sin((x * 3.1) + (y * 2.3) + (z * 1.7) + (t * 0.7))
        n2 = np.cos((x * 4.7) - (y * 3.9) + (z * 2.1) - (t * 0.5))
        n3 = np.sin((x * 2.2) - (y * 5.2) - (z * 3.4) + (t * 0.9))
        return (n1 + n2 + n3) / 3.0
