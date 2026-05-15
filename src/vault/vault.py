"""Canonical parameters for the vault-door mechanism study.

This module is the single source of truth shared by every vault topic
module — analogous to ``src/explainers/card.py`` for the gear card. Every
diagram, table, and prose constant is derived from the values here. Edit a
number, re-run ``uv run vault build``, and every page reflects it.

The values describe a fan-made educational mechanism: a circular vault
door with N radial locking pins, driven by one central rotation. They are
*illustrative* — useful for teaching geometry, symmetry, and pin-count
trade-offs — not an engineered product.
"""

from __future__ import annotations

from math import pi, radians

# --- Door body -------------------------------------------------------------
DOOR_DIAMETER_MM: float = 160.0
"""Outer diameter of the circular door slab."""

DOOR_THICKNESS_MM: float = 8.0
"""Slab thickness."""

PLATE_THICKNESS_MM: float = 4.0
"""Inner cam plate / wheel thickness."""

# --- Pins ------------------------------------------------------------------
PIN_COUNT: int = 12
"""Default pin count for the *primary* layout. Twelve divides cleanly into
2, 3, 4, 6, and 12 — supports opposing pairs, quadrant layout, and
clock-like visual logic. The 13-pin study compares against this baseline."""

PIN_DIAMETER_MM: float = 4.0
PIN_LENGTH_MM: float = 20.0
PIN_TRAVEL_MM: float = 8.0
"""How far each pin extends radially outward when locked."""

PIN_RADIUS_MM: float = 70.0
"""Pitch-circle radius the pin centres sit on."""

# --- Central drive ---------------------------------------------------------
HUB_DIAMETER_MM: float = 35.0
"""Central shaft / hub diameter."""

WHEEL_DIAMETER_MM: float = 45.0
"""Cam-wheel / drive-disc diameter."""

CAM_ROTATION_DEG: float = 10.0
"""Working stroke of the central cam rotation. A small input rotation that
must produce useful radial pin travel via the cam slots / linkages."""

CLEARANCE_MM: float = 0.3
"""Sliding clearance between adjacent moving parts."""

# --- Derived ---------------------------------------------------------------
ANGLE_STEP_DEG: float = 360.0 / PIN_COUNT
"""Angular spacing between adjacent pins (default layout). 360/12 = 30°."""

PIN_CIRCUMFERENCE_MM: float = 2 * pi * PIN_RADIUS_MM
"""Circumference of the pin pitch circle."""

ARC_PER_STEP_MM: float = PIN_CIRCUMFERENCE_MM / PIN_COUNT
"""Arc length between adjacent pins along the pitch circle."""

ARC_AT_10DEG_MM: float = PIN_RADIUS_MM * radians(CAM_ROTATION_DEG)
"""Arc length swept at the pin radius for one CAM_ROTATION_DEG of input.
Note: this is *arc travel*, not necessarily linear pin travel — that
depends on the actuator (cam slot, rack, linkage)."""

# --- Pin counts to compare in the study -----------------------------------
COMPARED_PIN_COUNTS: tuple[int, ...] = (6, 8, 12, 13, 24)
"""Pin counts shown side-by-side in the pin-counts comparison."""

PRIME_PIN_COUNT: int = 13
"""The 'awkward' counter-example. Mathematically valid placement, but no
exact opposing pairs and no clean quadrants."""

FRIENDLY_PIN_COUNT: int = 24
"""The flexible / highly-divisible counter-example."""
