from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

from jarvis_app.rendering.flow_field import FlowField
from jarvis_app.rendering.noise_field import NoiseField
from jarvis_app.rendering.sphere_generator import fibonacci_sphere


@dataclass
class RenderBatches:
    deep_space: np.ndarray
    background: np.ndarray
    neural_points: np.ndarray
    neural_lines: np.ndarray
    core_points: np.ndarray
    core_trails: np.ndarray
    core_glow: np.ndarray
    core_lines: np.ndarray
    camera_orbit: tuple[float, float, float]


def _rotation_matrix(ax: float, ay: float, az: float) -> np.ndarray:
    cx, sx = math.cos(ax), math.sin(ax)
    cy, sy = math.cos(ay), math.sin(ay)
    cz, sz = math.cos(az), math.sin(az)

    rx = np.array([[1, 0, 0], [0, cx, -sx], [0, sx, cx]], dtype=np.float32)
    ry = np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]], dtype=np.float32)
    rz = np.array([[cz, -sz, 0], [sz, cz, 0], [0, 0, 1]], dtype=np.float32)
    return rz @ ry @ rx


class ParticleEngine:
    def __init__(
        self,
        particle_count: int = 70000,
        deep_space_count: int = 6500,
        bg_count: int = 7500,
        neural_count: int = 3000,
        seed: int = 42,
    ) -> None:
        self.core_count = int(np.clip(particle_count, 50000, 120000))
        self.deep_space_count = int(np.clip(deep_space_count, 5000, 10000))
        self.bg_count = int(np.clip(bg_count, 5000, 10000))
        self.neural_count = int(np.clip(neural_count, 2000, 5000))

        self._rng = np.random.default_rng(seed)
        self._time = 0.0
        self._pulse = 0.0

        self._noise = NoiseField()
        self._flow = FlowField()

        self._core_base = fibonacci_sphere(self.core_count, radius=1.0)
        self._core_rand = self._rng.normal(0.0, 1.0, size=(self.core_count, 3)).astype(np.float32)
        self._core_points = (self._core_base + (self._core_rand * 0.012)).astype(np.float32)
        self._core_vel = self._rng.normal(0.0, 0.003, size=(self.core_count, 3)).astype(np.float32)

        self._deep_points = self._rng.uniform(-1.2, 1.2, size=(self.deep_space_count, 3)).astype(np.float32)
        self._deep_vel = self._rng.normal(0.0, 0.00006, size=(self.deep_space_count, 3)).astype(np.float32)

        self._bg_points = self._rng.uniform(-1.0, 1.0, size=(self.bg_count, 3)).astype(np.float32)
        self._bg_vel = self._rng.normal(0.0, 0.0002, size=(self.bg_count, 3)).astype(np.float32)

        self._neural_theta = self._rng.uniform(0.0, 2.0 * math.pi, size=self.neural_count).astype(np.float32)
        self._neural_phi = self._rng.uniform(0.0, math.pi, size=self.neural_count).astype(np.float32)
        self._neural_orbit = self._rng.uniform(1.25, 1.7, size=self.neural_count).astype(np.float32)
        self._neural_speed = self._rng.uniform(0.05, 0.22, size=self.neural_count).astype(np.float32)

        self._attractor_count = int(self._rng.integers(3, 7))
        self._attractor_phase = self._rng.uniform(0.0, math.tau, size=self._attractor_count).astype(np.float32)
        self._attractor_phi = self._rng.uniform(0.35, math.pi - 0.35, size=self._attractor_count).astype(np.float32)
        self._attractor_speed = self._rng.uniform(0.12, 0.28, size=self._attractor_count).astype(np.float32)
        self._attractor_strength = self._rng.uniform(0.04, 0.10, size=self._attractor_count).astype(np.float32)
        self._attractor_radius = self._rng.uniform(0.72, 1.06, size=self._attractor_count).astype(np.float32)

        self._trail_length = 8
        trail_sample_count = int(np.clip(self.core_count // 8, 7000, 18000))
        self._trail_sample_idx = np.linspace(0, self.core_count - 1, num=trail_sample_count, dtype=np.int32)
        self._trail_buffer = np.zeros((self._trail_length, trail_sample_count, 3), dtype=np.float32)
        self._trail_speed = np.zeros((self._trail_length, trail_sample_count), dtype=np.float32)
        self._trail_ptr = 0

        conn_sample_count = int(np.clip(self.core_count // 42, 1400, 2600))
        self._conn_sample_idx = np.linspace(0, self.core_count - 1, num=conn_sample_count, dtype=np.int32)
        self._conn_frame = 0
        self._cached_connection_lines = np.zeros((0, 7), dtype=np.float32)

        self._core_glow_base = self._rng.normal(0.0, 1.0, size=(2200, 3)).astype(np.float32)

        self._active_agents: dict[str, float] = {}

    def set_density(self, count: int) -> None:
        self.__init__(particle_count=count)

    def set_agent_activity(self, name: str, active: bool) -> None:
        if active:
            self._active_agents[name] = 1.0
        elif name in self._active_agents:
            self._active_agents[name] = 0.4

    def update(self, dt: float, audio_level: float, phase: str) -> RenderBatches:
        self._time += dt
        amp = float(np.clip(audio_level, 0.0, 1.0))

        deep = self._update_deep_space(dt)
        bg = self._update_background(dt, amp)
        neural_points, neural_lines = self._update_neural_field(dt, phase)
        core_points, core_lines = self._update_core(dt, amp, phase)
        core_trails = self._build_trails()
        core_glow = self._build_core_glow(phase)

        cam = (
            float(math.sin(self._time * 0.07) * 0.22),
            float(math.cos(self._time * 0.06) * 0.14),
            3.25,
        )

        return RenderBatches(
            deep_space=deep,
            background=bg,
            neural_points=neural_points,
            neural_lines=neural_lines,
            core_points=core_points,
            core_trails=core_trails,
            core_glow=core_glow,
            core_lines=core_lines,
            camera_orbit=cam,
        )

    def _update_deep_space(self, dt: float) -> np.ndarray:
        self._deep_points += self._deep_vel * (max(dt, 1.0 / 120.0) * 60.0)
        self._deep_points = np.where(self._deep_points > 1.2, -1.2, self._deep_points)
        self._deep_points = np.where(self._deep_points < -1.2, 1.2, self._deep_points)

        depth = self._deep_points[:, 2] + 2.4
        alpha = np.clip(depth / 5.2, 0.02, 0.1)
        size = np.clip((1.2 - self._deep_points[:, 2]) * 0.35, 0.35, 0.9)

        color = np.zeros((self.deep_space_count, 4), dtype=np.float32)
        color[:, 0] = 0.67
        color[:, 1] = 0.75
        color[:, 2] = 0.95
        color[:, 3] = alpha

        return np.column_stack([self._deep_points, color, size]).astype(np.float32)

    def _update_background(self, dt: float, amp: float) -> np.ndarray:
        self._bg_points += self._bg_vel * (max(dt, 1.0 / 120.0) * 60.0)
        self._bg_points = np.where(self._bg_points > 1.0, -1.0, self._bg_points)
        self._bg_points = np.where(self._bg_points < -1.0, 1.0, self._bg_points)

        depth = self._bg_points[:, 2] + 1.9
        alpha = np.clip(depth / 3.0, 0.06, 0.36)
        size = np.clip((1.5 - self._bg_points[:, 2]) * 0.75, 0.7, 2.2)

        color = np.zeros((self.bg_count, 4), dtype=np.float32)
        color[:, 0] = 0.30
        color[:, 1] = 0.66 + (0.08 * amp)
        color[:, 2] = 0.95
        color[:, 3] = alpha
        return np.column_stack([self._bg_points, color, size]).astype(np.float32)

    def _update_neural_field(self, dt: float, phase: str) -> tuple[np.ndarray, np.ndarray]:
        phase_gain = 1.0
        if phase == "planning":
            phase_gain = 1.5
        elif phase == "thinking":
            phase_gain = 1.25

        self._neural_theta += self._neural_speed * dt * phase_gain
        self._neural_phi += (self._neural_speed * 0.45) * dt

        x = np.cos(self._neural_theta) * np.sin(self._neural_phi) * self._neural_orbit
        y = np.cos(self._neural_phi) * self._neural_orbit
        z = np.sin(self._neural_theta) * np.sin(self._neural_phi) * self._neural_orbit
        points = np.stack([x, y, z], axis=1).astype(np.float32)

        energy = np.clip(0.4 + 0.6 * (np.sin(self._neural_theta * 2.0 + self._time) * 0.5 + 0.5), 0.2, 1.0)
        color = np.zeros((self.neural_count, 4), dtype=np.float32)
        color[:, 0] = 0.15
        color[:, 1] = 0.84
        color[:, 2] = 0.94
        color[:, 3] = 0.18 + (energy * (0.28 if phase == "planning" else 0.18))
        size = 1.1 + energy * 2.0
        neural_points = np.column_stack([points, color, size]).astype(np.float32)

        # Connection lines in GPU batches.
        step = 14 if phase == "planning" else 28
        idx_a = np.arange(0, self.neural_count, step, dtype=np.int32)
        idx_b = (idx_a + step + int((self._time * 8.0) % step)) % self.neural_count

        pa = points[idx_a]
        pb = points[idx_b]
        line_count = len(idx_a)
        line_color = np.zeros((line_count, 4), dtype=np.float32)
        line_color[:, 0] = 0.22
        line_color[:, 1] = 0.75
        line_color[:, 2] = 0.98
        line_color[:, 3] = 0.10 if phase != "planning" else 0.3

        line_vertices = np.zeros((line_count * 2, 7), dtype=np.float32)
        line_vertices[0::2, 0:3] = pa
        line_vertices[1::2, 0:3] = pb
        line_vertices[0::2, 3:7] = line_color
        line_vertices[1::2, 3:7] = line_color

        return neural_points, line_vertices

    def _moving_attractors(self) -> np.ndarray:
        theta = (self._time * self._attractor_speed) + self._attractor_phase
        phi = self._attractor_phi + (0.28 * np.sin((self._time * (self._attractor_speed * 0.67)) + self._attractor_phase))
        radius = self._attractor_radius + (0.10 * np.sin((self._time * (self._attractor_speed * 0.43)) + (self._attractor_phase * 0.7)))
        x = np.cos(theta) * np.sin(phi) * radius
        y = np.cos(phi) * radius
        z = np.sin(theta) * np.sin(phi) * radius
        return np.column_stack([x, y, z]).astype(np.float32)

    def _velocity_to_color(self, energy: np.ndarray) -> np.ndarray:
        knot = np.array([0.0, 0.58, 1.0], dtype=np.float32)
        r = np.interp(energy, knot, np.array([0.08, 0.55, 0.98], dtype=np.float32))
        g = np.interp(energy, knot, np.array([0.91, 0.36, 0.27], dtype=np.float32))
        b = np.interp(energy, knot, np.array([0.98, 0.98, 0.86], dtype=np.float32))
        return np.column_stack([r, g, b]).astype(np.float32)

    def _build_connection_lines(self, points: np.ndarray, energy: np.ndarray, phase: str) -> np.ndarray:
        self._conn_frame += 1
        interval = 1 if phase == "thinking" else 2
        if self._cached_connection_lines.size > 0 and (self._conn_frame % interval) != 0:
            return self._cached_connection_lines

        sample = points[self._conn_sample_idx]
        sample_energy = energy[self._conn_sample_idx]
        n = int(sample.shape[0])
        if n < 4:
            return np.zeros((0, 7), dtype=np.float32)

        threshold = 0.15 if phase == "thinking" else 0.12
        threshold2 = threshold * threshold
        max_conn = 6 if phase == "thinking" else 4

        diff = sample[:, None, :] - sample[None, :, :]
        dist2 = np.sum(diff * diff, axis=2)
        np.fill_diagonal(dist2, np.float32(1e9))

        nearest_idx = np.argpartition(dist2, kth=max_conn, axis=1)[:, :max_conn]
        nearest_dist2 = np.take_along_axis(dist2, nearest_idx, axis=1)
        valid = nearest_dist2 < threshold2

        i_idx = np.repeat(np.arange(n, dtype=np.int32), max_conn)
        j_idx = nearest_idx.reshape(-1).astype(np.int32)
        valid_flat = valid.reshape(-1)

        unique_mask = valid_flat & (i_idx < j_idx)
        if not np.any(unique_mask):
            self._cached_connection_lines = np.zeros((0, 7), dtype=np.float32)
            return self._cached_connection_lines

        ia = i_idx[unique_mask]
        ib = j_idx[unique_mask]

        pa = sample[ia]
        pb = sample[ib]
        pair_energy = (sample_energy[ia] + sample_energy[ib]) * 0.5

        alpha = np.clip(0.04 + (pair_energy * (0.20 if phase == "thinking" else 0.13)), 0.03, 0.26)
        c_r = np.interp(pair_energy, [0.0, 0.6, 1.0], [0.08, 0.46, 0.92]).astype(np.float32)
        c_g = np.interp(pair_energy, [0.0, 0.6, 1.0], [0.84, 0.44, 0.25]).astype(np.float32)
        c_b = np.interp(pair_energy, [0.0, 0.6, 1.0], [0.98, 0.98, 0.84]).astype(np.float32)
        c = np.column_stack([c_r, c_g, c_b, alpha]).astype(np.float32)

        lines = np.zeros((ia.size * 2, 7), dtype=np.float32)
        lines[0::2, 0:3] = pa
        lines[1::2, 0:3] = pb
        lines[0::2, 3:7] = c
        lines[1::2, 3:7] = c
        self._cached_connection_lines = lines
        return lines

    def _build_trails(self) -> np.ndarray:
        order = (self._trail_ptr - np.arange(1, self._trail_length + 1)) % self._trail_length
        pos = self._trail_buffer[order]
        speed = self._trail_speed[order]
        if pos.size == 0:
            return np.zeros((0, 8), dtype=np.float32)

        age = np.linspace(1.0, 0.16, self._trail_length, dtype=np.float32)[:, None]
        energy = np.clip(speed * 30.0, 0.0, 1.0)
        rgb = self._velocity_to_color(energy.reshape(-1)).reshape(self._trail_length, -1, 3)
        alpha = np.clip((0.03 + (energy * 0.11)) * age, 0.015, 0.12)
        size = np.clip(0.62 + (energy * 1.2) + (age * 0.8), 0.55, 2.8)

        trail = np.zeros((self._trail_length, pos.shape[1], 8), dtype=np.float32)
        trail[:, :, 0:3] = pos
        trail[:, :, 3:6] = rgb
        trail[:, :, 6] = alpha
        trail[:, :, 7] = size
        return trail.reshape(-1, 8)

    def _build_core_glow(self, phase: str) -> np.ndarray:
        glow_amp = 0.10 + (0.04 * math.sin(self._time * 2.8)) + (0.09 * self._pulse)
        if phase == "thinking":
            glow_amp += 0.045
        pos = self._core_glow_base * glow_amp

        d = np.linalg.norm(pos, axis=1)
        alpha = np.clip(0.10 + ((0.16 - d) * 1.8), 0.02, 0.19)
        size = np.clip(2.6 + ((0.18 - d) * 22.0), 1.4, 4.2)

        glow = np.zeros((pos.shape[0], 8), dtype=np.float32)
        glow[:, 0:3] = pos
        glow[:, 3] = 0.68
        glow[:, 4] = 0.90
        glow[:, 5] = 1.0
        glow[:, 6] = alpha
        glow[:, 7] = size
        return glow

    def _update_core(self, dt: float, amp: float, phase: str) -> tuple[np.ndarray, np.ndarray]:
        step = max(dt, 1.0 / 240.0) * 60.0
        base = self._core_base
        x = base[:, 0]
        y = base[:, 1]
        z = base[:, 2]

        breathing = 0.026 * math.sin(self._time * 1.18)
        radius_noise = self._noise.sample(x, y, z, self._time)
        target_radius = 1.0 + breathing + (0.08 * radius_noise)
        if phase == "listening":
            target_radius += (0.012 + amp * 0.05) * np.sin((x * 13.0) + (self._time * 9.5))
        elif phase == "thinking":
            target_radius -= 0.01
        elif phase == "speaking":
            target_radius += 0.02

        target = base * target_radius[:, None]

        attractors = self._moving_attractors()
        delta = attractors[None, :, :] - self._core_points[:, None, :]
        dist = np.linalg.norm(delta, axis=2) + 1e-5
        weight = self._attractor_strength[None, :] * np.exp(-(dist * dist) * 1.7)
        attractor_force = np.sum((delta / dist[:, :, None]) * weight[:, :, None], axis=1)

        flow = self._flow.sample(self._core_points + (self._time * 0.14), self._time)
        flow_gain = 0.052 + (0.032 * amp)
        if phase == "thinking":
            flow_gain *= 2.0
        elif phase == "planning":
            flow_gain *= 1.35

        spring = (target - self._core_points) * 0.074
        jitter = self._core_rand * (0.00045 + amp * 0.0007)
        acc = spring + (flow * flow_gain) + attractor_force + jitter

        if phase == "speaking":
            self._pulse = min(1.0, self._pulse + (0.07 + amp * 0.16))
        else:
            self._pulse *= 0.91

        dist_now = np.linalg.norm(self._core_points, axis=1)
        radial_dir = self._core_points / np.maximum(dist_now[:, None], 1e-6)
        ripple_amp = (0.010 + (0.048 * self._pulse)) if phase == "speaking" else (0.004 * self._pulse)
        ripple = np.sin((dist_now * 17.0) - (self._time * 11.2)) * ripple_amp
        if phase == "speaking":
            acc += radial_dir * (ripple[:, None] * 0.85)

        damping = 0.92 if phase == "thinking" else 0.94
        self._core_vel = (self._core_vel + (acc * step)) * damping
        self._core_points = self._core_points + (self._core_vel * step)

        dist = np.linalg.norm(self._core_points, axis=1)
        max_r = 1.22 if phase == "thinking" else 1.18
        out = dist > max_r
        if np.any(out):
            self._core_points[out] *= (max_r / np.maximum(dist[out], 1e-6))[:, None]
            self._core_vel[out] *= 0.7

        speed = np.linalg.norm(self._core_vel, axis=1)
        energy = np.clip(speed * 30.0, 0.0, 1.0)
        center = np.clip(1.0 - (dist / 1.2), 0.0, 1.0)
        energy = np.clip((energy * 0.72) + (center * 0.28) + (self._pulse * 0.26), 0.0, 1.0)
        rgb = self._velocity_to_color(energy)

        brightness = np.clip(0.44 + (center * 0.40) + (self._pulse * 0.22), 0.3, 1.0)
        rgb = np.clip(rgb * brightness[:, None], 0.0, 1.0)
        alpha = np.clip(0.22 + (energy * 0.34) + (center * 0.16), 0.16, 0.92)
        size = np.clip(1.0 + (energy * 1.8) + (center * 1.3), 0.95, 5.5)

        core_points = np.zeros((self.core_count, 8), dtype=np.float32)
        core_points[:, 0:3] = self._core_points
        core_points[:, 3:6] = rgb
        core_points[:, 6] = alpha
        core_points[:, 7] = size

        sample_pos = self._core_points[self._trail_sample_idx]
        sample_speed = speed[self._trail_sample_idx]
        self._trail_buffer[self._trail_ptr] = sample_pos
        self._trail_speed[self._trail_ptr] = sample_speed
        self._trail_ptr = (self._trail_ptr + 1) % self._trail_length

        connection_lines = self._build_connection_lines(self._core_points, energy, phase)

        if self._active_agents:
            names = sorted(self._active_agents.keys())
            verts = []
            kept: dict[str, float] = {}
            for i, name in enumerate(names):
                life = max(0.0, self._active_agents[name] - 0.01)
                if life > 0.03:
                    kept[name] = life
                a = (i * 0.9) + (self._time * 0.24)
                outer = np.array([math.cos(a) * 2.0, math.sin(a) * 1.4, math.sin(a * 0.7) * 0.3], dtype=np.float32)
                inner = np.array([math.cos(a * 1.2) * 1.0, math.sin(a * 1.2) * 1.0, 0.0], dtype=np.float32)
                c = np.array([0.45, 0.83, 0.99, min(0.65, 0.18 + life * 0.6)], dtype=np.float32)
                verts.append(np.concatenate([outer, c]))
                verts.append(np.concatenate([inner, c]))
            self._active_agents = kept
            agent_lines = np.asarray(verts, dtype=np.float32) if verts else np.zeros((0, 7), dtype=np.float32)
        else:
            agent_lines = np.zeros((0, 7), dtype=np.float32)

        if connection_lines.size and agent_lines.size:
            core_lines = np.vstack([connection_lines, agent_lines]).astype(np.float32)
        elif connection_lines.size:
            core_lines = connection_lines
        else:
            core_lines = agent_lines

        return core_points, core_lines
