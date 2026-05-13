# pycon2026 — a 256:1 reduction-gear card

> A credit-card-sized object with a five-stage compound reduction-gear chain. Designed in Onshape, deconstructed by Python.

[![CI](https://github.com/jmcpheron/pycon2026/actions/workflows/ci.yml/badge.svg)](https://github.com/jmcpheron/pycon2026/actions/workflows/ci.yml)
[![Build Card](https://github.com/jmcpheron/pycon2026/actions/workflows/build-card.yml/badge.svg)](https://github.com/jmcpheron/pycon2026/actions/workflows/build-card.yml)
[![Build Explainers](https://github.com/jmcpheron/pycon2026/actions/workflows/build-explainers.yml/badge.svg)](https://github.com/jmcpheron/pycon2026/actions/workflows/build-explainers.yml)
[![Pages](https://github.com/jmcpheron/pycon2026/actions/workflows/pages.yml/badge.svg)](https://jmcpheron.github.io/pycon2026/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

<p align="center">
  <img src="docs/assets/card/exploded.gif" alt="Animated exploded view of the reduction-gear card: top card half lifts up, five blue 40-tooth spur gears fan out in the middle, bottom card half lowers to reveal five shaft holes spaced 15 mm apart." width="900" />
</p>

<p align="center">
  <sub>Onshape AP242 STEP → <a href="src/stepforge"><code>stepforge explode</code></a> → seven parts → animated GIF. Every frame is regenerated in CI when the STEP changes.</sub>
</p>

<table>
<tr>
<td align="center" valign="top" width="33%">
<img src="docs/assets/card/parts/Part_1.png" alt="Render of one of the two card halves — a 78 × 44 mm flat body with four square gear pockets, an axle hole, and a curved bottle-opener-style notch on the right." />
<br/>
<sub><strong>Card half</strong><br/>78 × 44 mm body, four pockets, axle hole, bottle-opener notch.</sub>
</td>
<td align="center" valign="top" width="33%">
<img src="docs/assets/card/parts/Spur_gear_40_teeth.png" alt="Render of a 40-tooth spur gear with a short 10-tooth pinion hub fused on top — the standard compound gear." />
<br/>
<sub><strong>Standard compound gear</strong><br/>40-tooth driven disc + 10-tooth pinion on a short hub.</sub>
</td>
<td align="center" valign="top" width="33%">
<img src="docs/assets/card/parts/Spur_gear_40_teeth_4.png" alt="Render of a 40-tooth spur gear with a tall 10-tooth pinion hub — the tall-hub variant used in alternating stages of the compound chain." />
<br/>
<sub><strong>Tall-hub variant</strong><br/>Same 40 / 10 teeth, taller hub. Interleaved with short-hub gears so the discs don't collide.</sub>
</td>
</tr>
</table>

## Hand me one at PyCon US 2026

Long Beach, May 14–17. If you found this repo from a 3D-printed card I gave you — hi. The source for that card is [`jmcpheron-card.step`](jmcpheron-card.step) at the root of this repo. Fork it, slice it, print your own.

## How it works

Five gear stages, 4:1 each, multiplied together: **256:1**. Spin the input gear with your thumb; the output gear moves a quarter-degree.

The story is told across six short Python-generated explainers:

- [**The card in 3D**](docs/explainers/card-3d.md) — canonical STEP source and the `stepforge` pipeline. Start here.
- [**Gear ratios**](docs/explainers/gear-ratios.md) — compound multiplication, with a thumb-travel intuition: ~20.3 m of finger motion per output rotation.
- [**Decoding the gears from STEP**](docs/explainers/decoding-gears.md) — slice the committed STL, FFT the radial profile, recover the tooth count and module from geometry alone.
- [**Stacking**](docs/explainers/stacking.md) — why a 3-level cycle of hub heights keeps the card thin without the discs colliding.
- [**Terminology**](docs/explainers/terminology.md) — pinion, module, pitch circle, addendum. The 90 seconds of vocabulary the other pages assume.
- [**Printing considerations**](docs/explainers/printing.md) — orientation, chamfers, why each post is its own part.

## The Python tools

### `stepforge` — Python-driven STEP files

Click CLI on top of [`build123d`](https://github.com/gumyr/build123d) (OpenCascade) and [`cascadio`](https://github.com/trimesh/cascadio). Five subcommands:

| Command | Does |
|---|---|
| `stepforge inspect` | AP242 schema, assembly tree, bounding box, tessellation stats; merges sidecar `.meta.toml` if present |
| `stepforge build` | Tessellates STEP → STL or **colored GLB** (cascadio path preserves Onshape's per-part colors) |
| `stepforge render` | Orthographic PNG via the OpenSCAD pipeline (iso/top/edge/front/right presets) |
| `stepforge explode` | Decomposes an assembly into per-part STL/GLB/PNG + an exploded GLB + an animated GIF + a manifest |
| `stepforge assemble` | Composes multiple STEP parts into one assembly from a TOML manifest |

```
jmcpheron-card.step  ──►  stepforge inspect  ──►  docs/assets/card/inspect.txt
                     ──►  stepforge build    ──►  jmcpheron-card.{stl,glb}
                     ──►  stepforge explode  ──►  parts/*.{stl,glb,png}
                                                  exploded.{glb,gif}
                                                  manifest.toml
```

Every file in [`docs/assets/card/`](docs/assets/card/) is regenerated by [`.github/workflows/build-card.yml`](.github/workflows/build-card.yml) on any push that touches the STEP or the `stepforge` source, then auto-committed back. Push a new Onshape export and the hero GIF above updates itself within a minute.

### `explainers` — illustrated engineering writeups

Short, deterministic Python programs that produce the writeups under [`docs/explainers/`](docs/explainers/). The math, diagrams, and tables come from one canonical [`card.py`](src/explainers/card.py) — change a number there, every page reflects it on the next build.

```
src/explainers/<topic>.py  ──►  uv run explainers build  ──►  docs/explainers/<topic>.md
```

## Quickstart

```bash
git clone https://github.com/jmcpheron/pycon2026
cd pycon2026
uv sync --extra step
uv run stepforge inspect jmcpheron-card.step
uv run stepforge explode --in jmcpheron-card.step --out /tmp/card/
# → /tmp/card/{exploded.gif, jmcpheron-card.glb, parts/*.{stl,glb,png}, manifest.toml}
```

The `step` extra is opt-in — the OpenCascade wheel is ~180 MB.

Requirements: Python 3.11+, [OpenSCAD](https://openscad.org/) on your `$PATH`, [`uv`](https://docs.astral.sh/uv/).

## Things I'd love to chat about at PyCon

If you scanned this from the card I handed you, here's what I'm hoping to talk about. Find me on the floor — or open an issue.

- **3D printing**, especially print-in-place mechanisms and the geometry tricks that make them survive a bed-slinger.
- **Python ↔ CAD pipelines.** Onshape STEP exports → `cascadio` → `trimesh` → OpenSCAD → animated GIF, all in CI. I'd like to hear what other people are gluing together.
- **Open-source licensing for physical 3D files.** STEP and STL aren't software; MIT covers the code in this repo, but the geometry sits in a fuzzier zone.
- **Less-permissive licensing for STEP/STL** as a hedge against patent trolls and copyright-shaped opportunism. Whether stricter terms actually protect physical-design authors, or just create friction for the people who'd remix in good faith.
- **Devlog-as-build-journal** as a way to ship hardware in public. I'd like to hear from others doing the same.

## License

MIT — code and 3D assets, for now. See "Things I'd love to chat about at PyCon" above; the right license for the STEP/STL files is a live question, not a settled answer.
