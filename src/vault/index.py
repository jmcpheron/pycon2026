"""Builds docs/vault/README.md — the maker-story landing page.

Also emits the animated hero SVG at docs/vault/assets/vault-hero-animated.svg.
The README leads with the animation, opens with a first-person account of
the rack-thinning observation, then CTAs the interactive pin explorer
before the topic-page index.
"""

from __future__ import annotations

from pathlib import Path

from vault import vault as V
from vault.svg_draw import draw_animated_hero

# The interactive explorer ships as a hand-written HTML file at
# docs/vault/pin-explorer.html — relative link works on Pages, the
# absolute Pages URL is the reliable click-through from github.com.
PAGES_BASE = "https://jmcpheron.github.io/pycon2026"
EXPLORER_URL = f"{PAGES_BASE}/vault/pin-explorer.html"


def build_index(out_dir: Path) -> Path:
    assets = out_dir / "assets"
    assets.mkdir(parents=True, exist_ok=True)

    hero = draw_animated_hero(assets / "vault-hero-animated.svg")

    md_path = out_dir / "README.md"
    md_path.write_text(f"""# Vault Door Mechanism Study

![{V.PIN_COUNT}-pin vault door — pins extending and retracting from one cam rotation](assets/{hero.name})

> *A small Python toy for the geometry of rotary vault-door pin mechanisms.
> Symmetry, gearing, packaging, and why {V.PIN_COUNT} friends are kinder
> than {V.PRIME_PIN_COUNT}.*

## I made this because I got curious

Watching Adam Savage's mini vault-door build, I kept staring at one
detail I didn't understand at first: each pin had a section of straight
gear teeth cut into it, and the back of that section — the spine,
opposite the teeth — was machined surprisingly thin. More material
removed than weight savings would justify. When the parts went together
inside the door it clicked. **The pin count was forcing the geometry.**

A single central pinion has to drive all N racks at once, the racks
share the perimeter of that one pinion, and each rack's spine gets
machined down to whatever slice it gets. Bigger N → thinner slice.
Adam wasn't choosing the shape; the pin count was choosing it for him.

That observation kept me up an evening. This repo is what came out — a
Python parametric study of how pin count, symmetry, gearing, and
packaging interact on a circular vault door. Every diagram below is
generated from one parameter file
([`vault.py`](../../src/vault/vault.py)); change a number, every page
re-derives.

## Play with it

**[→ Open the live pin-count explorer]({EXPLORER_URL})**

Drag the slider from 3 to 30 pins. The layout snaps. The readout panel
shows the angle step (`360/N`), the divisors of N, whether the count
has exact opposing pairs, and how thin the rack body has to be at that
pin count given the canonical {V.CENTRAL_PINION_RADIUS_MM:g} mm pinion.

> {V.PIN_COUNT} reads clean.  {V.PRIME_PIN_COUNT} leaves an orphan.  {V.FRIENDLY_PIN_COUNT} pinches the racks to slivers.

*(Clicking that link from GitHub.com opens the page source. Open it
through GitHub Pages for the live version — the URL above lands you
there directly.)*

## Five short sections

1. [**Symmetry**](symmetry.md) — why {V.PIN_COUNT} and {V.FRIENDLY_PIN_COUNT} read as obvious and {V.PRIME_PIN_COUNT} doesn't.
2. [**The {V.PRIME_PIN_COUNT}-pin problem**](thirteen-pin-problem.md) — possible but mechanically awkward, and exactly *why* — no exact opposing pairs, no subgroup structure, no shared linkages.
3. [**Pin counts**](pin-counts.md) — small-multiples comparison plus the rack-thinning note from watching Adam's video, with the inequality `t ≤ 2π·r_pinion/N − clearance` and a per-N budget table.
4. [**Motion and travel**](motion-and-travel.md) — what a {V.CAM_ROTATION_DEG:g}° cam rotation actually gets you. `arc = r·θ`, the cam-radius table, and the careful distinction between *arc travel* and *radial pin travel*.
5. [**Onshape workflow**](onshape-workflow.md) — how the Python parameters in [`vault.py`](../../src/vault/vault.py) map to a parametric CAD model.

## For the Tested community

If you got here via the Tested Maker Share: hi. Adam's mini vault-door
build sparked this study; it is a love-letter to the geometry, not a
clone of his mechanism. Fork it, remix it, riff on it — change the pin
count in [`vault.py`](../../src/vault/vault.py), run `uv run vault build`,
and every page above re-derives with your numbers. The interactive
explorer takes the same input live in your browser. Send me what you
find.

## Default door parameters

* Door diameter: **{V.DOOR_DIAMETER_MM:g} mm**, thickness **{V.DOOR_THICKNESS_MM:g} mm**
* Pin count: **{V.PIN_COUNT}** on a pitch circle of radius **{V.PIN_RADIUS_MM:g} mm**
* Pin travel: **{V.PIN_TRAVEL_MM:g} mm** radial
* Central cam rotation: **{V.CAM_ROTATION_DEG:g}°** (sweeps **{V.ARC_AT_10DEG_MM:.2f} mm** of arc at the pin radius)
* Central pinion radius: **{V.CENTRAL_PINION_RADIUS_MM:g} mm** (bounds rack-body thickness to **{V.MAX_RACK_TANGENTIAL_THICKNESS_MM:.2f} mm** at N = {V.PIN_COUNT})

Change any of these in [`vault.py`](../../src/vault/vault.py) and the
explainer pages, hero animation, and budget tables all re-derive on the
next `uv run vault build`.

## How it gets built

```
src/vault/<topic>.py  ─►  uv run vault build <topic>  ─►  docs/vault/<topic>.md (+ assets/*.svg)
```

The pages are regenerated by [`.github/workflows/build-vault.yml`](../../.github/workflows/build-vault.yml)
on every push that touches `src/vault/` and auto-committed back to
`main`, alongside the parallel auto-commit workflows for the gear card
and the engineering explainers.

The interactive [`pin-explorer.html`](pin-explorer.html) is *not*
regenerated — it's hand-written, self-contained, deployed by
[`.github/workflows/pages.yml`](../../.github/workflows/pages.yml).

## Disclaimer · licenses

This is a fan-made educational mechanism study inspired by public maker
videos and general vault-door mechanisms. It is **not** an official
Tested project, does not reproduce any private plans, and is not
affiliated with Adam Savage's Tested.com.

Code: MIT.
Diagrams + 3D files under this directory: CC BY-SA 4.0.
See [`LICENSE`](../../LICENSE) and [`LICENSE-3D-FILES`](../../LICENSE-3D-FILES).

---

*Generated by `src/vault/index.py`. Source-of-truth parameters live in
[`src/vault/vault.py`](../../src/vault/vault.py).*
""")
    return md_path
