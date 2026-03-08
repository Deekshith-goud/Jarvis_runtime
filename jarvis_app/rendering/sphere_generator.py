from __future__ import annotations

import numpy as np


def fibonacci_sphere(count: int, radius: float = 1.0) -> np.ndarray:
    idx = np.arange(count, dtype=np.float32)
    phi = np.pi * (3.0 - np.sqrt(5.0))
    y = 1.0 - (idx / max(float(count - 1), 1.0)) * 2.0
    r = np.sqrt(np.clip(1.0 - y * y, 0.0, 1.0))
    theta = phi * idx
    x = np.cos(theta) * r
    z = np.sin(theta) * r
    points = np.stack([x, y, z], axis=1).astype(np.float32)
    return points * float(radius)
