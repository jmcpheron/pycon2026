# Pivot: challenge coin → business card

*2026-05-06 · jmcpheron*

## What changed

The Phase-2 conference giveaway has shifted from a challenge coin (round, ~40 mm, with a QR code on the back linking to its own OpenSCAD source) to a **3D-printed business card** (~88.9 × 50.8 mm, with rounded corners, a print-in-place spinning gear, and embossed identifier text).

## Why

<!-- TODO(jmcpheron): write your own reasoning here in your own voice.
     Suggested beats — pick whichever resonate, ignore the rest:

     - what made the coin idea feel cramped (real estate, novelty, etc.)
     - what made the card idea feel right (wallet longevity, FDM-friendliness,
       the gear as a conversation starter, the chance to do PIP)
     - any constraints or context (printer choice, time before the conference,
       what you've already tried with PIP parts)

     Aim for a paragraph or three — this post is the canonical "why" the rest
     of the devlog points back to. -->

## Card parameters (working values)

| Parameter | Value | Notes |
|---|---|---|
| Footprint | 88.9 × 50.8 mm | US-standard size |
| Corner radius | 4.5 mm | Generous round, "fun > strict" |
| Thickness | 1.6 mm | 4 layers @ 0.4 mm |
| Emboss height | +0.4 mm | One layer of relief |
| Gear pocket Ø | 32 mm | Right third of card |
| Pocket depth | 1.2 mm | |
| Gear OD | 30 mm | 14-tooth spur |
| Gear thickness | 1.0 mm | |
| Center post Ø | 2.4 mm | |
| Bore Ø | 3.0 mm | 0.3 mm radial clearance |
| Z-clearance under gear | 0.2 mm | Sacrificial layer |

These live in [`models/card.scad`](../../models/card.scad). The mockups in the next post explore the embossed-text layout — that's the next decision to make.

## What's not decided

- **Embossed text layout** — see [the mockups post](2026-05-06-card-text-mockups.md).
- **Font** — starting point is `Liberation Mono Bold`. Open to swapping after seeing the variants.
- **Whether the GitHub mark stays as a corner accent or gets dropped entirely** — depends on whether it reads cleanly at this size.
- **Gear tooth profile** — first attempt is intentionally simple. The scadia loop will refine via vision feedback if the first print binds.

## What's next

1. Pick a layout from the mockups post.
2. Bake the chosen layout into `card.scad`.
3. First print attempt — slice at 0.2 mm layer height, watch how the gear frees from the sacrificial layer.
4. Log results here, with photos.
