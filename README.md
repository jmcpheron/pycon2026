# pycon2026 — a parametric PyCon 2026 badge

> A 3D-printable conference badge with a print-in-place spinning gear. Forked, personalized, and built end-to-end with **Python driving OpenSCAD** in CI.

[![CI](https://github.com/jmcpheron/pycon2026/actions/workflows/ci.yml/badge.svg)](https://github.com/jmcpheron/pycon2026/actions/workflows/ci.yml)
[![Build STL](https://github.com/jmcpheron/pycon2026/actions/workflows/build-stl.yml/badge.svg)](https://github.com/jmcpheron/pycon2026/actions/workflows/build-stl.yml)
[![Pages](https://github.com/jmcpheron/pycon2026/actions/workflows/pages.yml/badge.svg)](https://jmcpheron.github.io/pycon2026/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/)

<table>
<tr>
<td align="center" valign="top" width="33%">
<img src="docs/assets/badge-hero.png" alt="The pycon2026 badge rendered in OpenSCAD's Cornfield colorscheme — an 88.9 × 50.8 × 1.6 mm card with embossed jmcpheron / pycon2026 text and a 14-tooth print-in-place gear in the pocket." />
<br/>
<sub><strong>1 · Source → OpenSCAD render</strong><br/>Python templates the SCAD, OpenSCAD renders the PNG. <a href=".github/workflows/build-stl.yml">Re-rendered in CI</a> on every push.</sub>
</td>
<td align="center" valign="top" width="33%">
<a href="https://github.com/jmcpheron/pycon2026/blob/main/models/card.stl"><img src="docs/assets/badge-stl-github.png" alt="A screenshot of GitHub's built-in STL viewer showing the badge as a blue solid resting on a triangulated ground plane, with toolbar controls for zoom / pan / rotate / view mode." /></a>
<br/>
<sub><strong>2 · Same source → STL on GitHub</strong><br/>The same Python pipeline produces <a href="https://github.com/jmcpheron/pycon2026/blob/main/models/card.stl"><code>models/card.stl</code></a> — <a href="https://github.com/jmcpheron/pycon2026/blob/main/models/card.stl">click to spin it in GitHub's viewer →</a></sub>
</td>
<td align="center" valign="top" width="33%">
<img src="docs/assets/badge-printed-placeholder.svg" alt="Placeholder graphic indicating that a photo of the actual printed badge will be added here once the print succeeds." />
<br/>
<sub><strong>3 · Same source → printed object</strong><br/>Coming soon — slice <code>card.stl</code>, print at 0.2 mm layers, pop the gear free with a fingernail.</sub>
</td>
</tr>
</table>

---

> **PyCon US 2026 — Long Beach, May 14–17.** Built to hand out and to fork. [Live demo page →](https://jmcpheron.github.io/pycon2026/)

## Quickstart

```bash
git clone https://github.com/jmcpheron/pycon2026
cd pycon2026
uv sync
uv run badgeforge build --name "Your Name" --github "yourhandle"
```

Out lands at `models/card.stl`. Slice it, print it (PLA, 0.2 mm layers, no supports), pop the gear free with a fingernail, wear it.

## How the pipeline works

```
  user values ──►  badgeforge CLI  ──►  openscad -D name=…  ──►  card.stl
  (--name,         (Python)             -D github=…             (binary STL)
   --github)                            card.scad
```

Python is the parametric and orchestration layer. OpenSCAD is the deterministic geometry backend. The same `badgeforge build` runs locally and in CI — every push to `main` rebuilds `models/card.stl` and commits it back, so the printable file in the repo always matches the source.

## What's on the badge

- **Body:** 88.9 × 50.8 × 1.6 mm — the standard business-card footprint, sized to fit a wallet sleeve.
- **Print-in-place gear:** a 30 mm spur gear sitting in a recessed pocket on a 2.4 mm post. The 0.2 mm sacrificial layer separates the gear from the post during printing; pop it free after.
- **Embossed text:** two-line `<name>` / `<github>` layout, 0.4 mm relief, Liberation Mono Bold. Defaults are `jmcpheron` and `pycon2026`. Both lines fit comfortably at ~9 characters each — longer strings will overflow into the gear pocket. (See [`docs/devlog/2026-05-06-card-text-mockups.md`](docs/devlog/2026-05-06-card-text-mockups.md) for the layout exploration.)

## Print settings (starting point)

| Setting | Value |
| --- | --- |
| Material | PLA |
| Layer height | 0.2 mm |
| Walls | 3 |
| Top/bottom layers | 4 |
| Infill | 20 % gyroid |
| Supports | none |
| Adhesion | brim 5 mm if your bed is uneven |

If the gear fuses to the post on first print, bump `gear_z_lift` from 0.2 to 0.3 mm in `models/card.scad`.

## Devlog

This is a working-out-loud project. Build progress, prints that worked, prints that didn't, and the design choices behind them live at [`docs/devlog/`](docs/devlog/).

## Requirements (local)

- Python 3.11+
- [OpenSCAD](https://openscad.org/) on your `$PATH`
- [`uv`](https://docs.astral.sh/uv/) (recommended)

## License

MIT

---

<details>
<summary><strong>Earlier: the AI design loop (scadia)</strong></summary>

Before the pivot to the badge, this repo was `scadia` — a Python tool that drove OpenSCAD code generation through Claude with a vision-feedback iteration loop. The loop and its experiments are still in this repo (`src/scadia/`, `scripts/multi_*.py`) and the showcase models in `models/` (m10-nut, scadvil, pi5-wall-mount, pi5-retro-case) are all outputs from it.

Why we stepped away from it for PyCon: the AI-loop arc had a Phase 3 plan (the Raspberry Pi case progression) that wasn't going to finish in time for the conference, and the badge was already half-built from Phase 2. The pivot is described in [`docs/devlog/2026-05-08-pivot-to-badge.md`](docs/devlog/).

```
                    ┌─────────────────┐
   user prompt ────►│  generate SCAD  │
                    └────────┬────────┘
                             ▼
                    ┌─────────────────┐
                    │     OpenSCAD    │
                    └────────┬────────┘
                       PNG    │   stderr
                  ┌───────────┴────────────┐
                  ▼                        ▼
          ┌──────────────┐         ┌────────────────┐
          │ vision critic │         │  validator     │
          └──────┬───────┘         └────────┬───────┘
                 │                          │
                 └──────────┬───────────────┘
                            ▼
                    ┌──────────────┐
                    │  controller  │  should_continue?
                    └──────────────┘
```

To run the loop:

```bash
cp .env.example .env  # add ANTHROPIC_API_KEY
uv run scadia "a hexagonal nut, M10" --iterations 3
```

Output lands in `output/run-<timestamp>/`. The loop is still functional; it's just not the headline anymore.

</details>
