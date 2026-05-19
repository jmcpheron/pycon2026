# Onshape vs OpenSCAD — for code-tracked CAD

Both Onshape and OpenSCAD are *parametric* CAD. You set knobs, the
model rebuilds. But they sit at opposite ends of a spectrum that
matters if you live in `git`: **where the source of truth lives, and
how a future you re-derives the model from it**.

This page exists because the same ring gear in this build can be made
with either tool. Both paths work. The point isn't to declare a winner
— it's to be clear about what you trade for what.

## TL;DR

| Question | Onshape | OpenSCAD |
| --- | --- | --- |
| Where does the source of truth live? | Cloud document with versioned revisions | Plain `.scad` text file in `git` |
| What does a "diff" look like? | Visual A↔B revision compare in the browser | `git diff` — line-level, attribution-able |
| Can I rebuild this from a 2-year-old commit? | Only if the Onshape doc still exists *and* its FeatureScripts haven't been version-bumped | Yes, deterministically — same `openscad` + same `.scad` = same STL |
| Does it work offline? | No | Yes |
| Best at? | Assemblies with motion (mates, joints, gear relations) | Math-driven parts, parameter sweeps, programmatic generation |
| Worst at? | Things that need to be checked into `git` | Organic / sculpted shapes |
| Cost (this project) | Free (public docs) | Free, MIT |
| Export to STEP? | Yes (native CAD kernel) | No (mesh-based, STL/3MF/AMF only) |
| Library ecosystem | FeatureScripts (cloud, embedded in CAD) | BOSL2, MCAD, NopSCADlib (installed locally) |

## What they have in common

If you squint, the **mental model is the same**:

1. Define parameters.
2. Express the geometry as expressions of those parameters.
3. Tweak a parameter, the whole model re-derives.

Both produce STL. Both can drive a 3D printer or downstream
simulation. Both can be parametrically *configured* (Onshape's
"configurations" / OpenSCAD's `// [Customizer]` blocks).

The whole gear-math derivation in
[`onshape-notes.md`](onshape-notes.md) — module, pitch circle, tip
circle, root circle, centre distance from sum of pitch radii — is
*identical* in both tools. It has to be: it's just the underlying
gear geometry. The tools differ in how you *type* it.

## Where they diverge: the ring gear, two ways

### Onshape

Four clicks, no math typed out by you:

1. Add custom feature → install "Spur Gear" once.
2. Open the Spur Gear feature.
3. Fill in: `Module = 0.5`, `Teeth = 120`, `Pressure angle = 20°`,
   `Face width = 4 mm`, `Bore dia = 50.876 mm`, **`Internal = OFF`**.
4. Confirm.

You don't see `pitch_radius = m·N / 2` anywhere. The FeatureScript
computed it; the GUI just rendered the result. This is fast, ergonomic,
and the resulting involute is metrology-grade. If you change a
parameter, the gear updates in real time.

Where this leaves you for "code tracking":

* The parameter values live inside a cloud document.
* If you delete the document, the gear is gone. If Onshape rolls a new
  FeatureScript version, the same numbers might generate a *slightly
  different* gear.
* Diffs are visual ("compare this revision to that revision"). They
  read well for shape changes ("the bore moved 2 mm") but poorly for
  parameter changes ("which of the 17 numbers changed from r12 to
  r13?").
* You can export a STEP or STL and check those into git, but those are
  *artifacts*, not sources. Re-editing them downstream defeats the
  parametric workflow.

### OpenSCAD

The same gear, expressed as text you can `git diff`:

```scad
// docs/vault/sandbox/ring_gear.scad — excerpt
function pitch_radius(n, m) = n * m / 2;
function tip_radius(n, m)   = pitch_radius(n, m) + m;
function root_radius(n, m)  = pitch_radius(n, m) - 1.25 * m;

module gear_2d(n, m, pa) {
    pitch_r = pitch_radius(n, m);
    tip_r   = tip_radius(n, m);
    root_r  = root_radius(n, m);
    half_arc_at_pitch = m * PI / 4;
    half_root_y = half_arc_at_pitch + (pitch_r - root_r) * tan(pa);
    half_tip_y  = max(half_arc_at_pitch - (tip_r - pitch_r) * tan(pa),
                      0.02);
    union() {
        circle(r = root_r);
        for (k = [0 : n - 1])
            rotate([0, 0, k * 360 / n])
                polygon(points = [
                    [root_r, -half_root_y],
                    [root_r,  half_root_y],
                    [tip_r,   half_tip_y],
                    [tip_r,  -half_tip_y],
                ]);
    }
}
```

The full file is ~80 lines including comments and the satellite-spur
demo. Run `openscad -o ring_gear.stl -D 'show_spurs=false'
ring_gear.scad` and you get a 2708-facet STL you can print.

* **`git log` is your design history.** Every change to a parameter is
  attributed, dated, and revertible. PRs review parameter changes
  exactly the way they review code.
* **Reproducibility is automatic.** Check out a 2-year-old commit, run
  OpenSCAD, get the *exact* same STL bytes (up to FP determinism).
* **The math is visible.** Anyone reading the file can see that
  `pitch_radius` is `n × m / 2`. The Onshape FeatureScript hides this.
* **You pay for it in tooth fidelity** — the `polygon()` above uses
  straight flanks slanted by the pressure angle, not a true involute
  curve. For visualisation and most prints, it's fine; for tight-mesh
  metrology, you'd want BOSL2's `spur_gear()` or a true-involute
  library.

### Visually side-by-side

The OpenSCAD render at default Customizer values:

![Ring + 12 spurs meshing, generated from ring_gear.scad](sandbox/ring_gear.stl)

(That's a link to the generated STL. The render PNG is regenerated
ad-hoc; see [`sandbox/README.md`](sandbox/README.md) for the export
command.)

The Onshape render would look identical *to the eye* — the same module
and tooth counts produce the same external shape, regardless of who
draws the teeth. The differences live in the **process**, not the
geometry.

## Where each tool dominates

### Reach for Onshape when

* You're building **assemblies with motion**. Mates, joints, gear
  relations, drag-to-test interference — these are first-class in
  Onshape and a pain to express in code.
* You need **STEP export** for downstream CAM, CFD, FEA, or other
  classical CAD pipelines. OpenSCAD's mesh outputs can't round-trip
  through STEP.
* The shape is **organic or sculpted** — body work, ergonomic grips,
  swoopy panels. OpenSCAD primitives don't bend that way comfortably.
* Your collaborators **don't code** but do know CAD. Onshape's GUI
  meets them where they are.

### Reach for OpenSCAD when

* The geometry is **math-driven**. Gear teeth, threads, fractals,
  voronoi infill, lattice supports — these are easier as expressions
  than as sketches.
* You want a **parameter sweep**. "Render this part at module 0.4, 0.5,
  0.6, 0.8" is a 1-line shell loop with OpenSCAD; in Onshape it's
  manual configuration management.
* You need **`git`-tracked history of every parameter change**. PRs
  reviewing the move from "12 mm pin" to "10 mm pin" should be a 2-line
  diff, not a screenshot of an Onshape revision tree.
* You're sharing the design **with people who may not have an account**
  on your CAD tool. A `.scad` file works for anyone who runs `apt-get
  install openscad` or downloads the macOS binary.
* The part is **small enough that tooth-perfect involutes don't
  matter** — schematic study models, decorative pieces, prototypes.

## The third option (worth knowing about)

This repo's `src/vault/mechanism.py` does neither — it uses
**build123d + bd_warehouse** (Python on top of the OCCT CAD kernel) to
get *both* a real involute (via OCCT's `Geom_Ellipse` machinery in
`bd_warehouse.gear.SpurGear`) *and* code-trackable parameter source
(via the Python module). The pattern is:

```
src/vault/vault.py          single Python file, every parameter
        ↓
src/vault/mechanism.py      build123d code, imports vault.py
        ↓
docs/vault/assets/parts/*   exported STLs, auto-committed by CI
```

It's the best of both worlds for *this* build — you get true involute
gears that you can `git diff` line-by-line — but the toolchain is
heavy (cadquery-ocp, OpenSCAD for rendering, xvfb in CI). For a
small one-file gear demo, `ring_gear.scad` is faster to read and
faster to iterate on.

The lesson: "Onshape vs OpenSCAD" isn't really binary. If
code-trackability is your hill, the underlying axis is *"is the
source of truth a text file?"* — and OpenSCAD, build123d, and
CadQuery are all on the right side of it.

## See also

* [`onshape-notes.md`](onshape-notes.md) — the canonical Onshape recipe
  for this build, including the ring-gear FeatureScript settings.
* [`sandbox/ring_gear.scad`](sandbox/ring_gear.scad) — the OpenSCAD
  ring-gear demo file.
* [`sandbox/ring_gear.stl`](sandbox/ring_gear.stl) — the printable STL
  generated from it.
* [`sandbox/README.md`](sandbox/README.md) — sandbox usage and
  "graduate a number out of the sandbox" rule.
* `src/vault/mechanism.py` — the build123d production path for the
  same five canonical parts.
