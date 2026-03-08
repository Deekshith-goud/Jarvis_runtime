from __future__ import annotations

import numpy as np


class FlowField:
    """Vectorized curl-noise-inspired flow used for neural internal motion."""

    def sample(self, points: np.ndarray, t: float) -> np.ndarray:
        p = points.astype(np.float32, copy=False)
        x = p[:, 0]
        y = p[:, 1]
        z = p[:, 2]

        # Curl(A) where A is a trigonometric vector potential; cheap and stable.
        cx = (-1.4 * np.sin((1.4 * y) - (0.9 * t))) - (1.9 * np.cos((1.9 * z) - (0.5 * t)))
        cy = (-1.3 * np.sin((1.3 * z) - (0.7 * t))) - (1.6 * np.cos((1.6 * x) + (0.6 * t)))
        cz = (-1.5 * np.sin((1.5 * x) + (0.8 * t))) - (1.7 * np.cos((1.7 * y) + (0.9 * t)))

        # Secondary octave introduces richer vortices.
        cx += 0.42 * np.sin((y * 3.1) + (z * 2.2) + (t * 1.2))
        cy += 0.42 * np.sin((z * 2.7) + (x * 2.9) + (t * 1.1))
        cz += 0.42 * np.sin((x * 3.0) + (y * 2.8) + (t * 1.3))

        flow = np.stack([cx, cy, cz], axis=1).astype(np.float32)
        norm = np.linalg.norm(flow, axis=1, keepdims=True)
        return flow / np.maximum(norm, 1e-5)
