# Acknowledgments

This repo is a thin layer of glue on top of a lot of other people's
work. Below is a list of the third-party tools and libraries that
make it possible, with their licenses and links. Where we redistribute
or modify any of their code (we don't — they're all dependencies pulled
from PyPI / apt / etc.), the upstream license text travels with the
package.

If something we use isn't credited here, that's a bug — please open an
issue or a PR.

## Python libraries (pulled in via `pyproject.toml`)

| Project | License | Used for |
|---|---|---|
| [`build123d`](https://github.com/gumyr/build123d) | [Apache-2.0](https://www.apache.org/licenses/LICENSE-2.0) | Parametric CAD modelling — reading the card STEP file in `cardlab`, generating the vault mechanism geometry in `src/vault/mechanism.py`, and the spinning gear chain in `src/cardlab/spin.py`. |
| [`bd_warehouse`](https://github.com/gumyr/bd_warehouse) | [Apache-2.0](https://www.apache.org/licenses/LICENSE-2.0) | Parametric gear primitives (`SpurGear`) on top of `build123d`. Drives the ring gear + spur gears in the vault mechanism animation **and** the 40-tooth driven + 10-tooth pinion compound gears in the card-spinning animation. |
| [`cadquery-ocp`](https://github.com/CadQuery/OCP) | [Apache-2.0](https://github.com/CadQuery/OCP/blob/master/LICENSE) | Python bindings to the [Open CASCADE Technology](https://dev.opencascade.org/) (OCCT) geometry kernel. Underlies `build123d`. |
| [`cascadio`](https://github.com/trimesh/cascadio) | [MIT](https://github.com/trimesh/cascadio/blob/main/LICENSE) | STEP → coloured GLB in one OCCT pass. Preserves Onshape's per-part colours through the `cardlab build` pipeline. |
| [`trimesh`](https://github.com/mikedh/trimesh) | [MIT](https://github.com/mikedh/trimesh/blob/main/LICENSE.md) | Mesh manipulation — used by `cardlab.explode` to enumerate per-part centroids and bboxes, and by the `decoding` explainer to slice the gear STL. |
| [`Pillow`](https://github.com/python-pillow/Pillow) | [MIT-CMU](https://github.com/python-pillow/Pillow/blob/main/LICENSE) | PNG → GIF stitching for the exploded-view animation (`cardlab.explode`) and the vault mechanism animation (`vault.mechanism`). |
| [`drawsvg`](https://github.com/cduck/drawsvg) | [MIT](https://github.com/cduck/drawsvg/blob/master/LICENSE.txt) | SVG generation for every explainer diagram and every vault topic diagram. |
| [`matplotlib`](https://matplotlib.org/) | [PSF-based](https://matplotlib.org/stable/users/project/license.html) | Charts in `src/explainers/` (the `decoding` and `ratios` explainers in particular). |
| [`click`](https://github.com/pallets/click/) | [BSD-3-Clause](https://github.com/pallets/click/blob/main/LICENSE.rst) | Command-line interfaces for all three CLIs (`cardlab`, `explainers`, `vault`). |
| [`pytest`](https://github.com/pytest-dev/pytest/) | [MIT](https://github.com/pytest-dev/pytest/blob/main/LICENSE) | Test runner. |

## External tools (system-level)

| Project | License | Used for |
|---|---|---|
| [OpenSCAD](https://openscad.org/) | [GPL-2.0-or-later](https://github.com/openscad/openscad/blob/master/COPYING) | PNG rendering of every per-part view and every animated frame. Invoked as a subprocess (no linking). |
| [Xvfb](https://x.org/releases/X11R7.7/doc/man/man1/Xvfb.1.xhtml) | [MIT/X11](https://gitlab.freedesktop.org/xorg/xserver/-/blob/master/COPYING) | Headless X display for OpenSCAD in CI runners. |
| [`uv`](https://github.com/astral-sh/uv) | [Apache-2.0 / MIT](https://github.com/astral-sh/uv?tab=readme-ov-file#license) | Python dependency management — the only thing you need to install before `uv sync --extra step`. By [Astral](https://astral.sh/). |
| [Onshape](https://www.onshape.com/) | proprietary platform | Source of the original `jmcpheron-card.step` ([public document](https://cad.onshape.com/documents/786fefdef357fb6860b54650/w/33fb9222a6752311e4f08c8b/e/da99fedbaeebf1422d4cb0d3)). |
| [GitHub Actions](https://github.com/features/actions) | proprietary platform | CI runner that auto-rebuilds the GIFs, SVGs, and markdown on every push. |

## Inspirations (no code reused)

- **Adam Savage's mini vault-door build** on [Tested](https://www.tested.com/). The vault-door study under [`docs/vault/`](docs/vault/) is a love-letter to the *geometry* of his mechanism — a fan study, not a clone, not affiliated with Tested.com or Adam Savage. No private plans or assets from the show are used.

## External 3D assets

- **Pounce-a-Pult spiral cat toy** ([`step-demo/pounce-a-pult.step`](step-demo/pounce-a-pult.step) and every render under [`docs/pounce-a-pult/assets/`](docs/pounce-a-pult/assets/)): design by a MakerWorld designer (profile 2316710), shared under [Creative Commons Attribution 4.0 (CC BY)](https://creativecommons.org/licenses/by/4.0/). Two upstream locations:
  - Parametric CAD source: [public Onshape document](https://cad.onshape.com/documents/01739d2a63dc91eaf28c2c62/w/a7c671d651186a5272cc789f/e/fdb2542c5ccec8040d59912a). This is where the geometry actually *lives* — open it in a browser to inspect, fork it into a free Onshape account to remix.
  - Printable bundle: [MakerWorld model page](https://makerworld.com/en/models/2138778-pounce-a-pult-spiral-cat-toy#profileId-2316710). Slicer profile, photos, assembly tips.

  The STEP file is redistributed here unchanged; our derived renders (PNGs, GIF, GLB, per-part STLs) are derivative works and inherit CC BY 4.0 with the same attribution. This is distinct from the repo's own 3D files (the gear card and vault diagrams), which are CC BY-**SA** 4.0 under [`LICENSE-3D-FILES`](LICENSE-3D-FILES).

## How the licenses interact with this repo

* **Our code** under `src/`, `tests/`, and the GitHub workflows is **MIT** ([`LICENSE`](LICENSE)).
* **Our 3D files** — the committed STEP, and every STL / GLB / PNG / GIF generated under `docs/assets/card/` and `docs/vault/assets/` — are **CC BY-SA 4.0** ([`LICENSE-3D-FILES`](LICENSE-3D-FILES)).
* **Dependencies** retain their own licenses. We do not redistribute their source; we import them from PyPI / install them from apt. Anyone reproducing this project pulls them from the same upstream sources.
* **OCCT** (under `cadquery-ocp`) is LGPL-2.1 with an exception that permits dynamic linking from non-GPL applications. We use it through `build123d`'s Python API only.
* **OpenSCAD** (GPL-2.0-or-later) is invoked as a separate process via `subprocess.run`. No source linking; the GPL doesn't extend across the subprocess boundary.
