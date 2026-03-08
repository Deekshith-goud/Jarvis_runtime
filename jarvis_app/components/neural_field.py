from __future__ import annotations

import math

import numpy as np


class NeuralFieldSystem:
    def __init__(self, node_count: int = 140, seed: int = 19) -> None:
        self.node_count = node_count
        self._rng = np.random.default_rng(seed)
        self._angles = self._rng.uniform(0.0, 2.0 * math.pi, self.node_count)
        self._orbit = self._rng.uniform(1.18, 1.58, self.node_count)
        self._z = self._rng.uniform(-0.65, 0.65, self.node_count)
        self._speed = self._rng.uniform(0.08, 0.24, self.node_count)
        self._time = 0.0

    def update(self, dt: float, phase_gain: float = 1.0) -> tuple[np.ndarray, list[tuple[int, int]], np.ndarray]:
        self._time += dt
        self._angles += self._speed * dt * phase_gain
        x = np.cos(self._angles) * self._orbit
        y = np.sin(self._angles) * self._orbit
        z = self._z + (np.sin(self._angles * 1.7 + self._time) * 0.06)

        pts = np.stack([x, y, z], axis=1)

        # Sparse dynamic edges.
        edge_budget = max(22, int(36 * phase_gain))
        edges: list[tuple[int, int]] = []
        step = max(2, self.node_count // edge_budget)
        for i in range(0, self.node_count, step):
            j = (i + step + int((self._time * 10) % 9)) % self.node_count
            if i != j:
                edges.append((i, j))

        node_energy = np.clip(0.3 + 0.7 * (np.sin(self._angles * 2.3 + self._time) * 0.5 + 0.5), 0.2, 1.0)
        return pts, edges, node_energy
