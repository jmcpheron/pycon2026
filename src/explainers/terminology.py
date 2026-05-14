"""Explainer #3 — terminology: pinion, hub, post, pitch circle, and friends.

Renders a single annotated cross-section of one compound gear with
callouts for every named feature, plus a side-by-side comparison of the
standard and tall-hub variants. The point of this section is to lock down
vocabulary the other explainers depend on.
"""

from __future__ import annotations

from pathlib import Path

import drawsvg as dw

from explainers import card, diagrams, style as S


SLUG = "terminology"


def _annotated_top_view(out: Path) -> Path:
    """Plan view of one compound gear with annotated callouts."""
    pad = 28
    scale = 8.0   # px per mm — large for readability
    big_r = (card.OUTER_DIA_BIG / 2) * scale     # 100 px
    pin_r = (card.OUTER_DIA_PINION / 2) * scale  # ~29 px
    pitch_r = (card.PITCH_DIA_BIG / 2) * scale
    hub_r = (card.HUB_DIAMETER_MM / 2) * scale
    post_r = (card.POST_HOLE_MM / 2) * scale

    # Plenty of headroom for callout labels around the gear.
    width = pad * 2 + big_r * 2 + 280
    height = pad * 2 + big_r * 2 + 60

    d = diagrams.new_drawing(width, height)
    cx = pad + big_r + 80
    cy = pad + big_r + 20

    # Outer disc (no teeth fill — we'll outline with pitch + outer + root).
    d.append(dw.Circle(cx, cy, big_r, fill=S.GEAR_BIG,
                       stroke=S.INK, stroke_width=S.STROKE_THIN))
    # Outer (addendum) circle highlighted as a dashed boundary.
    d.append(dw.Circle(cx, cy, big_r, fill="none",
                       stroke=S.INK_MUTED, stroke_width=S.STROKE_DIM,
                       stroke_dasharray="3,2"))
    # Pitch circle — the imaginary circle where gears actually mesh.
    d.append(dw.Circle(cx, cy, pitch_r, fill="none",
                       stroke=S.ACCENT_HILITE, stroke_width=S.STROKE_NORMAL,
                       stroke_dasharray="4,3"))
    # Root circle — the bottoms of the tooth valleys.
    root_r = (card.ROOT_DIA_BIG / 2) * scale
    d.append(dw.Circle(cx, cy, root_r, fill="none",
                       stroke=S.INK_MUTED, stroke_width=S.STROKE_DIM,
                       stroke_dasharray="2,2"))
    diagrams._tooth_ring(d, cx, cy, big_r - 4, card.BIG_TEETH, S.INK)

    # Pinion concentric (hidden behind big in plan view but shown smaller).
    d.append(dw.Circle(cx, cy, pin_r, fill=S.GEAR_PINION,
                       stroke=S.INK, stroke_width=S.STROKE_THIN))
    # Hub
    d.append(dw.Circle(cx, cy, hub_r, fill=S.HUB,
                       stroke=S.INK, stroke_width=S.STROKE_THIN))
    # Post hole
    d.append(dw.Circle(cx, cy, post_r, fill=S.PAPER,
                       stroke=S.INK, stroke_width=S.STROKE_THIN))

    # Callouts — leader lines from feature to label
    def callout(lx: float, ly: float, fx: float, fy: float, text: str,
                anchor: str = "start") -> None:
        d.append(dw.Line(fx, fy, lx, ly,
                         stroke=S.INK_MUTED, stroke_width=S.STROKE_DIM))
        d.append(dw.Circle(fx, fy, 1.4, fill=S.INK))
        d.append(dw.Text(text, S.FONT_SIZE_LABEL,
                         x=lx, y=ly + 4,
                         font_family=S.FONT_FAMILY, fill=S.INK,
                         text_anchor=anchor))

    # left-side labels
    callout(20, cy - big_r + 8, cx - big_r + 4, cy - 4,
            "outer (addendum) circle", anchor="start")
    callout(20, cy - big_r + 38, cx - pitch_r * 0.85, cy - pitch_r * 0.5,
            "pitch circle — meshing radius", anchor="start")
    callout(20, cy + 2, cx - hub_r - 1, cy,
            "hub (boss)", anchor="start")
    callout(20, cy + 36, cx - post_r - 1, cy + 4,
            "post hole — through to axle", anchor="start")
    callout(20, cy + 70, cx - pin_r - 1, cy + 6,
            "pinion (small gear)", anchor="start")
    callout(20, cy + 100, cx - root_r * 0.7, cy + root_r * 0.7,
            "root circle — tooth valley", anchor="start")

    # right-side labels
    callout(width - 20, cy - big_r + 8, cx + big_r - 4, cy - 4,
            "big gear (driven by pinion of previous stage)", anchor="end")
    callout(width - 20, cy + 2,
            cx + big_r * 0.7, cy + big_r * 0.4,
            f"{card.BIG_TEETH} teeth, module {card.MODULE_MM} mm", anchor="end")
    callout(width - 20, cy + 36,
            cx + pitch_r * 0.4, cy + pitch_r * 0.7,
            f"pitch ⌀ = teeth × module = {card.PITCH_DIA_BIG:g} mm", anchor="end")

    diagrams.title(d, pad, pad - 10,
                   "One compound gear, annotated (plan view)")
    diagrams.caption(d, pad, height - 10,
                     f"All radii at {scale:g}× scale. Real big OD = {card.OUTER_DIA_BIG:g} mm.")
    d.save_svg(str(out))
    return out


def _variant_comparison(out: Path) -> Path:
    """Side-by-side cross-section: standard part vs tall-hub variant."""
    layout = diagrams.CrossSectionLayout(
        n_levels=3, level_height=22, gear_thickness=8,
        center_distance=120, margin=40,
        level_labels=("L0", "L1", "L2"),
    )
    gears = [
        diagrams.GearSection(
            label="standard part",
            big_level=0, pinion_level=1,
            big_radius=30, pinion_radius=8, hub_radius=4,
        ),
        diagrams.GearSection(
            label="tall-hub variant",
            big_level=2, pinion_level=0,
            big_radius=30, pinion_radius=8, hub_radius=4,
            fill_big=S.GEAR_TALL, fill_pinion=S.GEAR_TALL, fill_hub=S.GEAR_TALL,
        ),
    ]
    width = 2 * layout.margin + (len(gears) - 1) * layout.center_distance + 2 * 30
    height = 2 * layout.margin + (layout.n_levels + 1) * layout.level_height + layout.gear_thickness * 2 + 36

    d = diagrams.new_drawing(width, height)
    diagrams.title(d, layout.margin, layout.margin - 8,
                   "Two unique parts make a chain of any length")
    diagrams.cross_section(d, 0, 16, gears, layout=layout)
    diagrams.caption(d, layout.margin, height - 12,
                     f"Standard hub spans {card.HUB_LEN_STANDARD_MM:g} mm "
                     f"(one gear + one gap). Tall-hub spans "
                     f"{card.HUB_LEN_TALL_MM:g} mm (vaults a level).")
    d.save_svg(str(out))
    return out


GLOSSARY = [
    ("big gear",
     "The larger of the two toothed wheels on a compound gear part. "
     "Driven by the pinion of the previous stage."),
    ("pinion",
     "The smaller toothed wheel on the same shaft as the big gear, "
     "sharing rotation. Drives the next stage's big gear."),
    ("hub (boss)",
     "The cylindrical spacer between big gear and pinion that sets their "
     "vertical separation. Length determines whether a part is the "
     "'standard' or 'tall-hub' variant."),
    ("post (axle, arbor)",
     "The vertical pin pressed into the card body that the gear rotates "
     "around. 'Post' in this writeup; 'axle' in mechanical engineering; "
     "'arbor' in clockmaking."),
    ("post hole",
     "The through-bore in the gear hub that fits over the post with "
     "enough clearance for free rotation."),
    ("pitch circle",
     "The imaginary circle where two meshing gears would touch if they "
     "were friction wheels. Tooth count × module / 2 = pitch radius."),
    ("module",
     "The size of one tooth, expressed as pitch diameter per tooth in mm. "
     "Two gears mesh only if their modules match."),
    ("addendum",
     "The radial distance from the pitch circle to the top of a tooth. "
     "Equals the module."),
    ("dedendum",
     "The radial distance from the pitch circle down to the root circle. "
     "Slightly larger than the addendum (×1.25) for clearance."),
    ("outer (addendum) circle",
     "The actual outer boundary of the gear — pitch circle plus addendum. "
     "What you'd measure with calipers."),
    ("root circle",
     "The bottom of the tooth valleys — pitch circle minus dedendum."),
    ("center distance",
     "Post-to-post spacing for a meshing pair. "
     "(big_pitch_⌀ + pinion_pitch_⌀) / 2."),
    ("compound gear",
     "A single rigid part holding both a big gear and a pinion on a "
     "shared hub. The two halves rotate together."),
    ("level",
     "A horizontal band of card thickness where a gear plate sits. "
     "Three levels cover any chain length when paired with a tall-hub "
     "variant every third gear."),
]


def build(out_dir: Path) -> Path:
    assets = out_dir / "assets"
    assets.mkdir(parents=True, exist_ok=True)

    anatomy = _annotated_top_view(assets / f"{SLUG}-anatomy.svg")
    variants = _variant_comparison(assets / f"{SLUG}-variants.svg")

    glossary_md = "\n".join(
        f"| **{term}** | {definition} |"
        for term, definition in GLOSSARY
    )

    md_path = out_dir / f"{SLUG}.md"
    md_path.write_text(f"""# Terminology — naming the parts

> *[your voice here] a paragraph explaining that the chat conversation kept tripping over which thing was called what, and that consolidating vocabulary up front saved a lot of back-and-forth later.*

## One compound gear, named

![annotated plan view of a compound gear](assets/{anatomy.name})

Every gear in the chain is the same shape: a **big gear** stacked above a smaller **pinion**, sharing a **hub** that wraps the **post hole**. When two gears mesh, the meeting actually happens on their **pitch circles** — that imaginary circle where the teeth would slide against each other if they were friction wheels. The visible outer edge — the **outer circle** — is just one tooth-height beyond that.

The math each diagram leans on:

```text
pitch_diameter = teeth × module          # the meshing reference circle
outer_diameter = pitch_diameter + 2 × module
root_diameter  = pitch_diameter − 2.5 × module
center_distance = (pitch_dia_a + pitch_dia_b) / 2
```

For the {card.BIG_TEETH}t / {card.PINION_TEETH}t pair used in this card at module {card.MODULE_MM} mm:

| Feature | Big gear | Pinion |
|---------|---------:|-------:|
| Teeth | {card.BIG_TEETH} | {card.PINION_TEETH} |
| Pitch ⌀ | {card.PITCH_DIA_BIG:g} mm | {card.PITCH_DIA_PINION:g} mm |
| Outer ⌀ | {card.OUTER_DIA_BIG:g} mm | {card.OUTER_DIA_PINION:g} mm |
| Root ⌀ | {card.ROOT_DIA_BIG:g} mm | {card.ROOT_DIA_PINION:g} mm |

## Two parts cover any chain length

![side-by-side standard part and tall-hub variant](assets/{variants.name})

The whole chain comes from two unique printed designs — same big gear, same pinion, same hub diameter, different hub *length*. The tall-hub variant shows up once every third position to drop the next pinion two levels at once and keep the chain from staircasing forever (see [stacking](stacking.md) for the why).

## Glossary

| term | definition |
|------|-----|
{glossary_md}

## A note on which word to use

The same physical thing has different names in different traditions:

- The vertical pin is a **post** in this repo, an **axle** in general mechanical engineering, an **arbor** in clockmaking and watchwork. They mean the same part. This writeup uses *post* throughout because it's the shortest word that's unambiguous in the context of a 3D-printed assembly.
- The cylindrical spacer is a **hub** here; you'll also see it called a **boss** in injection-mould literature, particularly when it's an integral feature of a larger part.
- A *pinion* is just a small gear in a context where there's a bigger gear to compare it to. There's no fixed tooth count that makes something a pinion; it's relational.

[Next: print considerations — how to actually 3D-print these parts →](printing.md)

---

*Generated by [`src/explainers/terminology.py`](../../src/explainers/terminology.py). Edit the source, not this file.*
""")
    return md_path
