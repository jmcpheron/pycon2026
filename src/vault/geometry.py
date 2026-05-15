"""Pure-math helpers for the vault layout.

No drawsvg dependency — these functions can be tested and reused without
the ``vault`` extra installed.

Coordinate convention matches ``src/explainers/diagrams.py``: SVG with
y-axis pointing down. ``polar_to_cartesian`` returns coordinates in that
frame. ``angle_degrees=0`` points along +x; ``angle_degrees=-90`` points
upward (the natural top-of-circle in screen space).
"""

from __future__ import annotations

from math import cos, radians, sin


def angle_step(pin_count: int) -> float:
    """Return the angular spacing (degrees) between adjacent pins."""
    if pin_count <= 0:
        raise ValueError(f"pin_count must be positive, got {pin_count}")
    return 360.0 / pin_count


def pin_angles(pin_count: int, start_angle: float = -90.0) -> list[float]:
    """Return the angles (degrees) of every pin, evenly spaced.

    Default ``start_angle=-90`` puts pin 0 at the top of the circle (12
    o'clock in screen coordinates).
    """
    step = angle_step(pin_count)
    return [start_angle + i * step for i in range(pin_count)]


def polar_to_cartesian(
    cx: float, cy: float, radius: float, angle_degrees: float
) -> tuple[float, float]:
    """Convert polar (radius, angle) to SVG cartesian (x, y).

    SVG y-axis points down. ``angle_degrees=0`` is +x; ``-90`` is up.
    """
    theta = radians(angle_degrees)
    return (cx + radius * cos(theta), cy + radius * sin(theta))


def opposite_partner_index(i: int, pin_count: int) -> int | None:
    """Return the index of the pin exactly 180° opposite pin ``i``.

    For even ``pin_count`` this is ``(i + pin_count // 2) % pin_count``.
    For odd ``pin_count`` no pin lands exactly opposite — return ``None``.
    """
    if pin_count <= 0:
        raise ValueError(f"pin_count must be positive, got {pin_count}")
    if not 0 <= i < pin_count:
        raise ValueError(f"pin index {i} out of range for {pin_count} pins")
    if pin_count % 2 != 0:
        return None
    return (i + pin_count // 2) % pin_count


def divisors(n: int) -> list[int]:
    """Return sorted divisors of n, ascending. ``divisors(12) == [1,2,3,4,6,12]``."""
    if n <= 0:
        raise ValueError(f"n must be positive, got {n}")
    out = []
    i = 1
    while i * i <= n:
        if n % i == 0:
            out.append(i)
            if i != n // i:
                out.append(n // i)
        i += 1
    return sorted(out)
