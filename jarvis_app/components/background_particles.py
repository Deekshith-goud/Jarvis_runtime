from __future__ import annotations

import numpy as np


class BackgroundParticleSystem:
    def __init__(self, count: int = 7000, seed: int = 7) -> None:
        self.count = int(np.clip(count, 5000, 10000))
        self._rng = np.random.default_rng(seed)
        self._points = self._rng.uniform(-1.0, 1.0, size=(self.count, 3)).astype(np.float32)
        self._velocity = self._rng.normal(0.0, 0.00022, size=(self.count, 3)).astype(np.float32)
        self._depth_bias = self._rng.uniform(0.35, 1.1, size=(self.count,)).astype(np.float32)
        self._star_count = 1800
        self._stars = self._rng.uniform(-1.2, 1.2, size=(self._star_count, 3)).astype(np.float32)
        self._star_velocity = self._rng.normal(0.0, 0.00007, size=(self._star_count, 3)).astype(np.float32)

    def update(self, dt: float, drift: float = 1.0) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        dt_scale = max(dt, 1.0 / 120.0) * drift
        self._points += self._velocity * dt_scale * 60.0

        # Wrap around volume.
        self._points = np.where(self._points > 1.0, -1.0, self._points)
        self._points = np.where(self._points < -1.0, 1.0, self._points)

        x, y, z = self._points[:, 0], self._points[:, 1], self._points[:, 2]
        depth = z + 1.8
        alpha = np.clip((depth / 2.8) * self._depth_bias, 0.05, 0.42)
        size = np.clip((1.5 - z) * 0.9, 0.7, 2.2)
        return np.stack([x, y], axis=1), alpha, size

    def update_deep_space(self, dt: float) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        dt_scale = max(dt, 1.0 / 120.0)
        self._stars += self._star_velocity * dt_scale * 60.0
        self._stars = np.where(self._stars > 1.2, -1.2, self._stars)
        self._stars = np.where(self._stars < -1.2, 1.2, self._stars)

        x, y, z = self._stars[:, 0], self._stars[:, 1], self._stars[:, 2]
        depth = z + 2.4
        alpha = np.clip(depth / 5.0, 0.02, 0.12)
        size = np.clip((1.1 - z) * 0.35, 0.35, 0.95)
        return np.stack([x, y], axis=1), alpha, size
