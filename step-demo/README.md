# step-demo — STEP files, the Python way

This directory exercises [`stepforge`](../src/stepforge), the sibling tool to `badgeforge` that handles STEP files (ISO 10303 — the heavyweight CAD interchange format that GitHub's web UI can't natively render).

The story is in three parts.

## 1 · Inspect a real STEP file

`pounce-a-pult.step` is an Onshape AP242 export (a small toy trebuchet model). Even before we tessellate anything, Python can read its product structure:

```bash
uv run stepforge inspect step-demo/pounce-a-pult.step
```

You get the schema, originating system, units, bounding box, triangle count at the default tessellation, and the assembly tree with each part's position. CI captures this as [`docs/pounce-a-pult-tree.txt`](../docs/pounce-a-pult-tree.txt) on every push.

## 2 · Convert it to formats GitHub *can* render

```bash
uv run stepforge build --in step-demo/pounce-a-pult.step --out step-demo/pounce-a-pult.stl
uv run stepforge build --in step-demo/pounce-a-pult.step --out step-demo/pounce-a-pult.glb
```

GitHub renders `.stl` natively — click [`pounce-a-pult.stl`](pounce-a-pult.stl) in the file tree and you get a 3D viewer with pan/zoom/rotate. The `.glb` is a glTF binary suitable for embedding in three.js viewers, model-viewer, etc.

For the README hero images:

```bash
xvfb-run -a uv run stepforge render \
  --in step-demo/pounce-a-pult.step \
  --angle iso \
  --out docs/assets/pounce-a-pult-iso.png
```

`stepforge render` is small and a little clever: it tessellates to STL, writes a one-line `.scad` shim that `import()`s the STL, then hands the whole thing to OpenSCAD — reusing the exact xvfb + Cornfield pipeline `badgeforge` already proved out. So the STEP renders share the badge's visual style for free.

## 3 · Compose multiple STEP parts into one assembly

Sometimes the assembly is one file; sometimes it's a bill of materials. `stepforge assemble` reads a TOML manifest and stitches parts together:

```bash
uv run python step-demo/parts/generate.py        # one-shot — writes base/arm/cup/pin .step
uv run stepforge assemble \
  --manifest step-demo/parts/assembly.toml \
  --out step-demo/parts/assembled.step \
  --also-stl --also-png
```

[`parts/assembly.toml`](parts/assembly.toml) is a flat list of `[[part]]` blocks with relative `path`, optional `name`, and optional `xyz` / `rpy` locations. Edit the numbers, re-run, see the result.

## Pipeline diagram

```
  *.step  ──►  stepforge inspect ──►  tree.txt
          ──►  stepforge build   ──►  *.stl  (GitHub viewer)
          ──►  stepforge build   ──►  *.glb  (web viewers)
          ──►  stepforge render  ──►  *.png  (hero images)
  *.toml  ──►  stepforge assemble ──► assembled.step (+ .stl, +.png)
```

CI runs all of the above on every push that touches `step-demo/**` or `src/stepforge/**`, then auto-commits the results. Configured in [`.github/workflows/build-step.yml`](../.github/workflows/build-step.yml).

## Why these tool choices

- **`build123d`** for STEP I/O — actively maintained, clean `Compound` / `Location` API, sits on the same OpenCascade engine Onshape uses on export so the round-trip is BREP-lossless rather than mesh-lossy.
- **OpenSCAD** for PNG renders — already proven on this repo's CI; sidesteps the EGL / pyrender headless rabbit hole.
- **`trimesh`** is in the dep list as an optional bridge to other mesh formats; `stepforge build` itself uses build123d's native `export_gltf`.

The OpenCascade Python wheel (`cadquery-ocp`) is ~180 MB, so it's gated behind `uv sync --extra step` rather than being a default dependency — most contributors only working on the badge don't need it.
