"""Explainer #2 — interleaving and the level-stacking problem.

Renders three side-view cross-sections that walk through the design
journey: (A) the naive 2-level layout that collides, (B) the descending
staircase that works but balloons card thickness, and (C) the actual
solution — a 3-level cycle of two standard parts and one tall-hub variant.
"""

from __future__ import annotations

from pathlib import Path

import drawsvg as dw

from explainers import card, diagrams, style as S


SLUG = "stacking"


def _section_2level_fail(out: Path) -> Path:
    """Side view: every gear at 2 levels, big discs collide."""
    layout = diagrams.CrossSectionLayout(
        n_levels=2, level_height=14, gear_thickness=5,
        center_distance=44, margin=28,
        level_labels=("L0", "L1"),
    )
    # Five gears, all in the same orientation: big at L0, pinion at L1.
    # Adjacent big discs share L0 → collision (rendered with FAIL accent).
    gears = []
    for i in range(card.N_STAGES):
        gears.append(diagrams.GearSection(
            label=f"G{i + 1}",
            big_level=0,
            pinion_level=1,
            big_radius=18, pinion_radius=5, hub_radius=2,
            collide=True,
        ))
    width = 2 * layout.margin + (len(gears) - 1) * layout.center_distance + 2 * 18
    height = 2 * layout.margin + (layout.n_levels + 1) * layout.level_height + layout.gear_thickness * 2 + 30

    d = diagrams.new_drawing(width, height)
    diagrams.title(d, layout.margin, layout.margin - 4,
                   "(A) two levels — adjacent big discs collide on L0",
                   color=S.ACCENT_FAIL)
    diagrams.cross_section(d, 0, 12, gears, layout=layout)
    diagrams.caption(d, layout.margin, height - 8,
                     "Every gear shares the same orientation, so every big disc lives on L0. "
                     "Two big discs at the same height physically intersect at the mesh point.")
    d.save_svg(str(out))
    return out


def _section_staircase(out: Path) -> Path:
    """Side view: each gear one level lower than the previous. Works, but tall."""
    n = card.N_STAGES
    layout = diagrams.CrossSectionLayout(
        n_levels=n + 1, level_height=10, gear_thickness=4,
        center_distance=44, margin=28,
        level_labels=tuple(f"L{i}" for i in range(n + 1)),
        levels_at_top=True,
    )
    gears = []
    for i in range(n):
        gears.append(diagrams.GearSection(
            label=f"G{i + 1}",
            big_level=i,
            pinion_level=i + 1,
            big_radius=18, pinion_radius=5, hub_radius=2,
        ))
    width = 2 * layout.margin + (n - 1) * layout.center_distance + 2 * 18
    height = 2 * layout.margin + (layout.n_levels + 1) * layout.level_height + layout.gear_thickness * 2 + 30

    d = diagrams.new_drawing(width, height)
    diagrams.title(d, layout.margin, layout.margin - 4,
                   "(B) descending staircase — works, but card thickness scales with gear count")
    diagrams.cross_section(d, 0, 12, gears, layout=layout)
    diagrams.caption(d, layout.margin, height - 8,
                     f"Each gear sits one level below the previous. {n} gears need {n + 1} levels — "
                     f"every additional gear thickens the card by one more gear-plate plus clearance.")
    d.save_svg(str(out))
    return out


def _section_3level_cycle(out: Path) -> Path:
    """The actual solution: 3-level cycle, two standard parts + one tall."""
    n = card.N_STAGES
    layout = diagrams.CrossSectionLayout(
        n_levels=3, level_height=14, gear_thickness=5,
        center_distance=44, margin=28,
        level_labels=("L0", "L1", "L2"),
    )

    # Cycle of 3 gears: gear 1 = big L0/pinion L1, gear 2 = big L1/pinion L2,
    # gear 3 = big L2/pinion L0 (tall hub jumps L1 entirely). Then the cycle
    # restarts: gear 4 = like gear 1, gear 5 = like gear 2, etc.
    cycle = [
        (0, 1, S.GEAR_BIG, S.GEAR_PINION, S.HUB),       # standard
        (1, 2, S.GEAR_BIG, S.GEAR_PINION, S.HUB),       # standard, mounted up
        (2, 0, S.GEAR_TALL, S.GEAR_TALL, S.GEAR_TALL),  # tall — pinion vaults to L0
    ]
    gears = []
    for i in range(n):
        big_lvl, pin_lvl, fb, fp, fh = cycle[i % 3]
        label = f"G{i + 1}" + (" (tall)" if i % 3 == 2 else "")
        gears.append(diagrams.GearSection(
            label=label,
            big_level=big_lvl,
            pinion_level=pin_lvl,
            big_radius=18, pinion_radius=5, hub_radius=2,
            fill_big=fb, fill_pinion=fp, fill_hub=fh,
        ))
    width = 2 * layout.margin + (n - 1) * layout.center_distance + 2 * 18
    height = 2 * layout.margin + (layout.n_levels + 1) * layout.level_height + layout.gear_thickness * 2 + 30

    d = diagrams.new_drawing(width, height)
    diagrams.title(d, layout.margin, layout.margin - 4,
                   "(C) three-level cycle — two standard parts, then one tall — repeat",
                   color=S.ACCENT_OK)
    diagrams.cross_section(d, 0, 12, gears, layout=layout)
    diagrams.caption(d, layout.margin, height - 8,
                     "Tall variants (darker) carry their pinion two levels down so it lands at L0 "
                     "again, returning the chain to its starting configuration. "
                     "Card thickness stays at 3 levels regardless of gear count.")
    d.save_svg(str(out))
    return out


def _plan_view(out: Path) -> Path:
    """Top-down: 5 posts at center distance, with the card outline."""
    pad = 24
    scale = 4.0   # px per mm
    chain_len = (card.N_STAGES - 1) * card.CENTER_DISTANCE_MM * scale
    width = 2 * pad + chain_len + 2 * (card.OUTER_DIA_BIG / 2) * scale + 40
    height = 2 * pad + card.CARD_HEIGHT_MM * scale * 0.6

    d = diagrams.new_drawing(width, height)

    # Card outline (scaled visually small for the diagram).
    card_w = card.CARD_WIDTH_MM * scale
    card_h = card.CARD_HEIGHT_MM * scale * 0.6
    diagrams.card_outline(d, pad, pad, card_w, card_h)

    cy = pad + card_h / 2
    cx0 = pad + 20

    # Show actual physical overlap of big gears at the mesh.
    big_r = (card.OUTER_DIA_BIG / 2) * scale
    pin_r = (card.OUTER_DIA_PINION / 2) * scale
    cd_px = card.CENTER_DISTANCE_MM * scale

    for i in range(card.N_STAGES):
        cx = cx0 + i * cd_px
        diagrams.compound_gear(
            d, cx, cy,
            big_r=big_r, pinion_r=pin_r, hub_r=4.5,
            label=f"G{i + 1}",
            teeth_count=card.BIG_TEETH,
        )

    # Dimension line for one center distance
    if card.N_STAGES >= 2:
        x1 = cx0
        x2 = cx0 + cd_px
        y_dim = cy + big_r + 22
        diagrams.dimension_line(
            d, x1, y_dim, x2, y_dim,
            label=f"{card.CENTER_DISTANCE_MM:g} mm "
                  f"= ({card.PITCH_DIA_BIG:g} + {card.PITCH_DIA_PINION:g}) / 2",
        )

    diagrams.caption(d, pad, height - 6,
                     f"Plan view at scale {scale:g}× — card is "
                     f"{card.CARD_WIDTH_MM:g} × {card.CARD_HEIGHT_MM:g} mm")
    d.save_svg(str(out))
    return out


def build(out_dir: Path) -> Path:
    assets = out_dir / "assets"
    assets.mkdir(parents=True, exist_ok=True)

    fail_path = _section_2level_fail(assets / f"{SLUG}-2level-fail.svg")
    stair_path = _section_staircase(assets / f"{SLUG}-staircase.svg")
    cycle_path = _section_3level_cycle(assets / f"{SLUG}-3level-cycle.svg")
    plan_path = _plan_view(assets / f"{SLUG}-plan-view.svg")

    md_path = out_dir / f"{SLUG}.md"
    md_path.write_text(f"""# Stacking — fitting {card.N_STAGES} compound gears in a {card.CARD_THICKNESS_MM:g} mm card

> *[your voice here] this section is the one where the chat conversation actually went somewhere. Spoiler: 2D layout fails, brute-force stair-stepping works but bloats the card, and the right answer is a 3-level cycle.*

## The constraint

Two compound gears mesh when one's pinion lines up with the other's big disc — same height, different post. That part's straightforward. The trouble starts when you ask: where does each gear's *other* part go? And, more painfully: where do the *non-meshing* parts of every other gear in the chain end up?

You only have a few millimetres of card thickness to work with ({card.CARD_THICKNESS_MM:g} mm here, with {card.GEAR_THICKNESS_MM:g} mm gear plates and {card.LAYER_GAP_MM:g} mm clearance between layers). Every level you add is a budget line item.

## (A) Two levels, naive — doesn't work

The first instinct is: put every gear in the same orientation. Big disc on the bottom, pinion on top. Two levels total. Stack them in a row.

![two-level layout fails because adjacent big discs share L0 and collide](assets/{fail_path.name})

The pinions all live at L1 and the big discs all live at L0, which is *fine* for meshing (each gear's pinion at L1 has the next gear's big disc to mesh with) — except adjacent big discs are now occupying the same horizontal level *and* are close enough to physically intersect at the mesh point. Nothing turns.

## (B) Descending staircase — works, but expensive

The brute-force fix: put every gear one level lower than the previous one. No two big discs ever share a level, no collisions anywhere.

![descending staircase: each gear one level lower](assets/{stair_path.name})

This works, but **{card.N_STAGES} gears now need {card.N_STAGES + 1} levels of vertical space** — every additional gear thickens the card. At {card.GEAR_THICKNESS_MM:g} mm per gear plate plus {card.LAYER_GAP_MM:g} mm of clearance, that's {(card.GEAR_THICKNESS_MM + card.LAYER_GAP_MM) * (card.N_STAGES + 1):.1f} mm just for the stack. The card has to be thicker than the chain plus floor and cap. Six gears overshoots a {card.CARD_THICKNESS_MM:g} mm card.

## (C) Three-level cycle — two standard parts, one tall — works *and* doesn't grow

Here's the trick that came out of the chat conversation, eventually: introduce a special **tall-hub** variant of the gear. Its hub is long enough to span two levels of vertical clearance. Use it once every three gears, and the chain returns to its starting configuration after each cycle.

![three-level cycle with a tall-hub gear every third position](assets/{cycle_path.name})

The cycle in pictures:

| Gear in cycle | Big disc level | Pinion level | Part type |
|---------------|----------------|--------------|-----------|
| 1 (G1, G4, G7…) | L0 | L1 | standard |
| 2 (G2, G5, G8…) | L1 | L2 | standard, mounted up one level |
| 3 (G3, G6, G9…) | L2 | L0 | **tall-hub** (pinion vaults two levels down) |

After three gears you're back at L0, ready to start the next cycle. The card stays at three levels of vertical stack regardless of gear count: {card.N_STAGES} gears, ten gears, twenty gears — same {card.LEVELS}-level card.

You only need **two unique printed parts**: the standard one (hub spans 1 clearance) and the tall one (hub spans 2 clearances). For a {card.N_STAGES}-gear chain you print {card.N_STAGES - card.N_STAGES // 3} standard and {card.N_STAGES // 3} tall.

## Plan view

Spacing — the part where the meshing actually has to be physically possible — is set by the standard gear-mesh formula:

```text
center_distance = module × (big_teeth + pinion_teeth) / 2
                = {card.MODULE_MM} × ({card.BIG_TEETH} + {card.PINION_TEETH}) / 2
                = {card.CENTER_DISTANCE_MM:g} mm
```

That's the post-to-post distance for every adjacent pair. Five gears = four meshes = {(card.N_STAGES - 1) * card.CENTER_DISTANCE_MM:g} mm of horizontal post span.

![plan view of 5 compound gears at center distance](assets/{plan_path.name})

The big discs visually overlap in plan view at the mesh point — that's *intended*. The teeth interlock at the pitch circle. Cross-section (C) above proves the discs are at different *heights*, so there's no physical collision; the overlap is just the shadow when you look down at it.

## Why this matters in practice

You can solve the same problem by laying the chain out in 2D — bend it into an L-shape, route around an obstacle, etc. — but a straight run is cleaner to print, cleaner to assemble, and reads better on a {card.CARD_WIDTH_MM:g} × {card.CARD_HEIGHT_MM:g} mm rectangle. The 3-level cycle is the smallest design that lets a straight chain stay straight.

[Next: terminology — naming all the parts you've been pointing at →](terminology.md)

---

*Generated by [`src/explainers/stacking.py`](../../src/explainers/stacking.py). Edit the source, not this file.*
""")
    return md_path
