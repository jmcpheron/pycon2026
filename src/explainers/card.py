"""Canonical parameters for the compound-gear business card.

This module is the single source of truth shared by every explainer. The
numbers here came out of the parallel design conversation (gears designed
manually, not by Claude Code) and edits here re-render every section.
"""

from __future__ import annotations

# --- Tooth geometry --------------------------------------------------------
MODULE_MM: float = 0.6
"""Gear module (pitch diameter / tooth count). 0.6 mm balances printability
against footprint — 0.5 mm pinions get fragile on FDM, 0.7 mm pushes the
chain over the card width."""

BIG_TEETH: int = 40
PINION_TEETH: int = 10

# --- Compound gear part dimensions ----------------------------------------
GEAR_THICKNESS_MM: float = 1.0
"""Thickness of the big disc and the pinion plate (each)."""
LAYER_GAP_MM: float = 0.3
"""Vertical clearance between adjacent gear layers in the assembly."""
HUB_DIAMETER_MM: float = 3.0
"""Outer diameter of the cylindrical hub between big disc and pinion."""
POST_DIAMETER_MM: float = 2.0
"""Diameter of the axle post pressed into the card."""
POST_HOLE_MM: float = 2.2
"""Hub through-hole diameter — slightly oversized for free rotation."""

# --- Assembly counts -------------------------------------------------------
N_STAGES: int = 5
"""Gears in the chain. Each pinion-to-big mesh between consecutive gears
contributes one ratio multiplication, so N gears = N-1 meshes.
5 gears → 4 meshes → 4^4 = 256:1; 6 gears → 5 meshes → 4^5 = 1024:1."""
LEVELS: int = 3
"""Vertical bands the gears occupy. Three is the minimum that lets the
'two standard parts then one tall part' cycle keep card thickness bounded
regardless of N_STAGES."""

# --- Card body -------------------------------------------------------------
CARD_WIDTH_MM: float = 88.9
CARD_HEIGHT_MM: float = 50.8
CARD_THICKNESS_MM: float = 5.0
"""Three vertical levels at 1.0 mm gear + 0.3 mm gap = 3.9 mm of stack,
plus floor and cap, fits inside a 5 mm card thickness."""

# --- Derived ---------------------------------------------------------------
PITCH_DIA_BIG: float = MODULE_MM * BIG_TEETH
PITCH_DIA_PINION: float = MODULE_MM * PINION_TEETH
OUTER_DIA_BIG: float = PITCH_DIA_BIG + 2 * MODULE_MM
OUTER_DIA_PINION: float = PITCH_DIA_PINION + 2 * MODULE_MM
ROOT_DIA_BIG: float = PITCH_DIA_BIG - 2.5 * MODULE_MM
ROOT_DIA_PINION: float = PITCH_DIA_PINION - 2.5 * MODULE_MM

CENTER_DISTANCE_MM: float = (PITCH_DIA_BIG + PITCH_DIA_PINION) / 2
"""Post-to-post spacing: 15 mm at the canonical numbers."""

RATIO_PER_STAGE: float = BIG_TEETH / PINION_TEETH
"""Reduction at each pinion-to-big mesh. 4.0 at the canonical numbers."""

TOTAL_RATIO: float = RATIO_PER_STAGE ** (N_STAGES - 1)
"""Compound ratio across the whole chain. (N gears = N-1 meshes — gear 1
is the input, the meshes are between adjacent gears.)"""

# --- Hub variants (for the 3-level cycle) ---------------------------------
HUB_LEN_STANDARD_MM: float = GEAR_THICKNESS_MM + LAYER_GAP_MM
"""Hub length on the 'standard' part — spans one level of clearance."""
HUB_LEN_TALL_MM: float = 2 * GEAR_THICKNESS_MM + 2 * LAYER_GAP_MM + GEAR_THICKNESS_MM
"""Hub length on the 'tall' variant — spans two levels so its pinion vaults
over the intermediate big gear of its predecessor."""

# --- Print parameters -----------------------------------------------------
LAYER_HEIGHT_MM: float = 0.1
"""Print layer height. 0.1 mm gives 6 layers per 0.6 mm tooth height."""
CHAMFER_DEG: float = 45.0
"""Self-supporting overhang slope at the hub-to-pinion transition."""
