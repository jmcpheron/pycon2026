# Vault door — local OpenSCAD sandbox

This directory is the **local iteration playground** for the vault door's
structural body. It is intentionally a "side quest" from the main repo
toolchain:

* No build123d, no `bd_warehouse`, no Python in the loop — just one
  hand-written `.scad` file with an OpenSCAD Customizer block.
* Not watched by `build-vault.yml` or `build-vault-mechanism.yml`. The
  only CI that touches it is `pages.yml`, which publishes the file to
  GitHub Pages as a static asset.
* No auto-commits race your edits.

The canonical Python parameters in [`src/vault/vault.py`](../../../src/vault/vault.py)
remain the source of truth for the CI-rendered GIF and the engineering
explainer pages. `door.scad` is a *parallel* representation — same
numbers, different language — meant for fast geometric play.

## How to use

Open the file in the OpenSCAD GUI:

```
openscad docs/vault/sandbox/door.scad
```

Then **View → Customizer**. Drag the sliders. Hit **F5** for fast
preview, **F6** for the full CSG render.

To export a still PNG for sharing:

```
openscad -o /tmp/door.png \
    --imgsize 1600,900 \
    --camera 0,0,15,58,0,28,500 \
    --projection ortho \
    --colorscheme Cornfield \
    docs/vault/sandbox/door.scad
```

To override a parameter from the command line (one-off, without editing
the file):

```
openscad -o /tmp/door_thin.png -D 'door_thickness_mm=24' docs/vault/sandbox/door.scad
```

## What is and isn't in the model

In: door body, tapered edge, internal cavity, 12 radial pin bores, the
spur-axle bolt circle on the 72 mm BCD, the ring-gear boss recess, an
optional 120° cutaway wedge.

Not in: the ring gear, the 12 spur gears, the racks, the locking pins
themselves, the combination lock cage, the hinge, the frame plate. The
gears already exist as STLs in
[`docs/vault/assets/parts/`](../assets/parts/) — those are produced from
`src/vault/mechanism.py` via build123d + bd_warehouse, because involute
gear teeth are painful in raw OpenSCAD primitives. If you want them
visible alongside the door, `import("../assets/parts/ring-gear.stl")`
from a sibling `.scad` file is the cleanest path.

## When to graduate a number out of the sandbox

If a dimension you've been dialling in here turns out to be the "right"
one, update [`docs/vault/specs.md`](../specs.md) (with a source tag) and
then `src/vault/vault.py`. The sandbox is for play; the Python module is
where decisions land.
