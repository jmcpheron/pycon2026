"""Shared SVG palette and typography for the explainers.

Imported by every diagram so the four sections feel like one publication.
"""

from __future__ import annotations

# --- Palette (warm-steel gear aesthetic) ----------------------------------
INK = "#1f2937"          # primary lines and labels (slate-800)
INK_MUTED = "#6b7280"    # secondary labels, dimensions (gray-500)
PAPER = "#ffffff"        # diagram background (white)

GEAR_BIG = "#b8a169"     # warm brass for big gears
GEAR_PINION = "#d4b876"  # lighter brass for pinions
GEAR_TALL = "#9c7c4f"    # darker brass for the tall-hub variant
HUB = "#8a8a8a"          # neutral steel for hubs
POST = "#4b5563"         # darker steel for posts (gray-600)
LEVEL_LINE = "#d1d5db"   # very light gray for level guides (gray-300)

CARD = "#f3f4f6"         # card body fill (gray-100)
CARD_EDGE = "#9ca3af"    # card outline (gray-400)

ACCENT_OK = "#16a34a"    # green-600 — "this works"
ACCENT_FAIL = "#dc2626"  # red-600 — "collision"
ACCENT_HILITE = "#2563eb"  # blue-600 — callouts

# --- Typography ------------------------------------------------------------
FONT_FAMILY = "ui-monospace, 'SF Mono', 'Cascadia Mono', Menlo, monospace"
FONT_SIZE_LABEL = 11
FONT_SIZE_DIM = 9
FONT_SIZE_TITLE = 14

# --- Stroke weights -------------------------------------------------------
STROKE_THIN = 0.6
STROKE_NORMAL = 1.0
STROKE_THICK = 1.5
STROKE_DIM = 0.5

# --- Diagram canvas defaults -----------------------------------------------
PAD = 16
"""Padding around diagram content."""
