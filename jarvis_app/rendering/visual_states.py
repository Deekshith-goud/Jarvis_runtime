from __future__ import annotations

from dataclasses import dataclass


@dataclass
class VisualState:
    scale: float
    glow: float
    ring: float
    vibration: float
    flow: float
    link_intensity: float


_STATE_TARGETS: dict[str, VisualState] = {
    "idle": VisualState(scale=1.00, glow=0.18, ring=0.06, vibration=0.05, flow=0.06, link_intensity=0.06),
    "ambient": VisualState(scale=1.00, glow=0.18, ring=0.06, vibration=0.05, flow=0.06, link_intensity=0.06),
    "listening": VisualState(scale=1.06, glow=0.28, ring=0.18, vibration=0.24, flow=0.14, link_intensity=0.12),
    "thinking": VisualState(scale=0.96, glow=0.34, ring=0.34, vibration=0.12, flow=0.52, link_intensity=0.2),
    "planning": VisualState(scale=0.98, glow=0.38, ring=0.42, vibration=0.1, flow=0.34, link_intensity=0.75),
    "speaking": VisualState(scale=1.08, glow=0.52, ring=0.52, vibration=0.30, flow=0.24, link_intensity=0.22),
}


class VisualStateController:
    def __init__(self) -> None:
        self.current = VisualState(scale=1.0, glow=0.2, ring=0.08, vibration=0.08, flow=0.1, link_intensity=0.1)
        self._target = _STATE_TARGETS["idle"]

    def set_phase(self, phase: str) -> None:
        self._target = _STATE_TARGETS.get(phase, _STATE_TARGETS["idle"])

    def update(self, dt: float) -> VisualState:
        speed = min(max(dt * 6.5, 0.02), 0.35)
        self.current = VisualState(
            scale=self.current.scale + (self._target.scale - self.current.scale) * speed,
            glow=self.current.glow + (self._target.glow - self.current.glow) * speed,
            ring=self.current.ring + (self._target.ring - self.current.ring) * speed,
            vibration=self.current.vibration + (self._target.vibration - self.current.vibration) * speed,
            flow=self.current.flow + (self._target.flow - self.current.flow) * speed,
            link_intensity=self.current.link_intensity + (self._target.link_intensity - self.current.link_intensity) * speed,
        )
        return self.current
