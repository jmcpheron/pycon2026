"""Per-stage colors shared by the spin and explode pipelines.

The cascading reduction story benefits from a consistent visual signature
across every animation the repo emits — the same crimson-to-violet
gradient that reads "fast to slow" in ``spin.gif`` makes the chain in
``exploded.gif`` instantly identifiable as the same five-stage train,
even when the parts are mid-explosion.

RGB tuples are in 0..1 because that's what OpenSCAD's ``color()`` wants.
"""

from __future__ import annotations

# Hot-to-cool gradient along the reduction chain. Saturated to pop against
# the default Cornfield yellow plate / card body that both pipelines leave
# uncolored.
STAGE_COLORS: tuple[tuple[float, float, float], ...] = (
    (0.86, 0.20, 0.27),  # crimson  — stage 0, input
    (0.94, 0.43, 0.12),  # orange   — stage 1
    (0.12, 0.67, 0.43),  # emerald  — stage 2
    (0.16, 0.43, 0.78),  # azure    — stage 3
    (0.55, 0.27, 0.71),  # violet   — stage 4, output
)

AXLE_COLOR: tuple[float, float, float] = (0.30, 0.30, 0.32)
"""Dark steel for stationary axle posts — uniform, recedes from the
spinning color cascade."""


def scad_color(rgb: tuple[float, float, float]) -> str:
    """Format an (r, g, b) tuple as an OpenSCAD ``color([...])`` prefix."""
    r, g, b = rgb
    return f"color([{r:.3f},{g:.3f},{b:.3f}])"
