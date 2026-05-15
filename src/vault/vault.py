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

CENTRAL_PINION_RADIUS_MM: float = 12.0
"""Pitch radius of the central pinion that engages all N racks in the
rack-and-pinion central drive variant. Sits inside the hub. Together with
``PIN_COUNT`` this sets the per-rack tangential budget — see
``RACK_BUDGET_PER_PIN_MM`` below."""

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

# --- Rack-and-pinion packing constraint -----------------------------------
RACK_BUDGET_PER_PIN_MM: float = 2 * pi * CENTRAL_PINION_RADIUS_MM / PIN_COUNT
"""Tangential perimeter each rack gets at the central pinion's pitch circle.
The N rack bodies must fit side-by-side around the pinion without
colliding, so each rack's tangential thickness must not exceed this
(minus clearance). See ``MAX_RACK_TANGENTIAL_THICKNESS_MM``."""

MAX_RACK_TANGENTIAL_THICKNESS_MM: float = RACK_BUDGET_PER_PIN_MM - CLEARANCE_MM
"""Upper bound on rack body tangential thickness:

    t  ≤  (2π · r_pinion / N)  −  clearance

This is the packing constraint that forces the 'thinned spine' geometry
visible in miniature rack-and-pinion vault builds — every rack gets a
fixed slice of the pinion's perimeter and the spine is machined down to
fit its slice."""

# --- Pin counts to compare in the study -----------------------------------
COMPARED_PIN_COUNTS: tuple[int, ...] = (6, 8, 12, 13, 24)
"""Pin counts shown side-by-side in the pin-counts comparison."""

PRIME_PIN_COUNT: int = 13
"""The 'awkward' counter-example. Mathematically valid placement, but no
exact opposing pairs and no clean quadrants."""

FRIENDLY_PIN_COUNT: int = 24
"""The flexible / highly-divisible counter-example."""

# --- Detailed mechanism (Adam Savage build) -------------------------------
# The constants above drive the *schematic* SVG diagrams (one central
# pinion, illustrative). The constants below drive the *detailed*
# build123d mechanism in ``src/vault/mechanism.py``: a 120-tooth central
# ring gear driving 12 spur gears (24 teeth each) on a 72 mm BCD, each
# spur driving one rack-and-pin via rack-and-pinion. Numbers come from
# the Adam Savage Tested video referenced in the README.

MECH_RING_GEAR_TEETH: int = 60
"""Tooth count of the central ring gear used for the *rendered* animation.

Adam's real build uses 120 teeth at module 0.5; we render with 60 teeth
at module 1.0 because ``bd_warehouse``'s involute-profile generator hits
numerical limits above ~100 teeth. The geometry stays equivalent — same
72 mm BCD, same 5:1 gear ratio (60 / 12 vs. 120 / 24) — just rendered
with chunkier teeth that read better at GIF resolution. Editing this
number re-renders the GIF in CI."""

MECH_GEAR_MODULE_MM: float = 1.0
"""Gear module for the *rendered* animation. See ``MECH_RING_GEAR_TEETH``
for why this is 1.0 here even though Adam's real build is 0.5."""

MECH_GEAR_PRESSURE_ANGLE: float = 14.5
"""Pressure angle (degrees). 14.5° is the older AGMA standard; modern
practice is 20°, but ``bd_warehouse`` refuses 20° at these tooth counts."""

MECH_SPUR_GEAR_BCD_MM: float = 72.0
"""Spur-gear centres lie on a 72 mm bolt-circle diameter (Adam's drawing)."""

MECH_SPUR_GEAR_TEETH: int = 12
"""Derived from the BCD geometry at the rendered module:
ring pitch radius = module * teeth / 2 = 1.0 * 60 / 2 = 30 mm.
Spur centres sit at BCD/2 = 36 mm, so spur pitch radius = 36 − 30 = 6 mm,
which at module 1.0 is 12 teeth. Gear ratio ring:spur = 5:1 — same as
Adam's actual 120:24."""

MECH_RING_GEAR_ID_MM: float = 50.876
"""Inner diameter of the ring gear's mounting boss — Adam's measured
2.003 inches ('two inches plus about three thousandths')."""

MECH_RACK_STOCK_MM: float = 8.0
"""Square cross-section of the rack stock (8 × 8 mm)."""

MECH_LOCKING_PIN_DIA_MM: float = 12.0
"""Diameter of the radial locking pins ('M12'). Distinct from
``PIN_DIAMETER_MM`` above, which sizes the *schematic* decorative pins."""

MECH_LOCKING_PIN_LEN_MM: float = 30.0
"""Locking pin length (Adam's 'M12 × 30')."""

MECH_DOOR_DIA_MM: float = 152.4
"""6 inches — outer diameter of the acrylic door body."""

MECH_DOOR_THICKNESS_MM: float = 31.75
"""1.25 inches — thickness of the acrylic door body."""
