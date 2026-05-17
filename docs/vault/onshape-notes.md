# Onshape working notes

CAD-tool-specific guidance, distilled from initial research and updated as I
go. `specs.md` is for *what* to model; this file is for *how* to model it in
Onshape specifically.

## FeatureScripts to use

Don't hand-draw involute gear teeth — Onshape's standard custom-feature
library has a **Spur Gear** generator. Add it via "Add custom features" in any
Part Studio.

| Gear | Settings |
| --- | --- |
| Spur gear (qty 12) | Module 0.5, 24 teeth, **External** |
| Ring gear | Module 0.5, 120 teeth, **External** (it's a sun gear — see below) |

The 2.4-in outer-diameter target on the ring gear should fall out of the math
once module and tooth count are right; verify against `specs.md` after generating.

> **Naming note.** "Ring gear" is what Adam calls it in the video, but
> topologically it's a *sun gear* — the 12 spurs orbit it on the outside,
> meeting its outward-facing teeth. An *internal* ring/annulus gear has
> teeth on the inside of an annulus with planets sitting inside. Set
> `Internal = OFF` in the FeatureScript or the spurs won't mesh.

## Assembly: getting them to mesh

1. **Revolute Mate** each gear and pin to the base plate so it can rotate
   about its axis.
2. **Gear Relation** between the ring gear and each spur gear. Onshape derives
   the 5:1 ratio from the tooth counts automatically (no need to type it).
3. For the locking pins, a **Rack and Pinion Relation** (rather than Gear
   Relation) ties each pin's linear motion to its spur gear's rotation.

Driving the ring gear should then animate all 12 pins extending in unison.

## Ring gear in Onshape — module math, then two ways to cut teeth

### What "module" actually is

Gear *module* (`m`) is the millimetres of **pitch diameter per tooth**.

```
pitch_diameter = m × N           (N = tooth count)
pitch_radius   = m × N / 2
```

The *pitch circle* is the imaginary circle where two meshing gears
touch tangentially — not the outer (tooth-tip) or root (tooth-bottom)
circle. The tooth-tip circle is one module *bigger* than the pitch
circle on each side:

```
tip_diameter  = pitch_diameter + 2·m   (external gear)
root_diameter = pitch_diameter − 2.5·m (external gear, with clearance)
```

**Two gears can only mesh if they share the same module.** Module is
to gears what thread pitch is to screws — it's the "compatibility
key". For this build, every gear is module `0.5 mm`.

Plugging in Adam's numbers:

| Gear | `m × N` | Pitch dia | Tip dia (outer) |
| --- | --- | --- | --- |
| Spur (×12) | 0.5 × 24 | 12.0 mm | 13.0 mm |
| Ring (sun)  | 0.5 × 120 | 60.0 mm | 61.0 mm |

The 61.0 mm tip diameter is **2.401 in** — exactly the OD Adam
measures in the video. That's the consistency check after generating
the gear: if Onshape's "outer diameter" readout is anything but
61 mm, the module or tooth count is wrong.

### Spur-gear centre distance falls out of the same math

For two external gears in mesh the centres are spaced by the *sum* of
their pitch radii:

```
centre_distance = (pitch_radius_ring + pitch_radius_spur)
                = (60/2) + (12/2)
                = 30 + 6
                = 36 mm
```

Twice that = 72 mm BCD — which matches Adam's 72 mm bolt-circle
exactly. So once `m`, ring teeth, and spur teeth are set, the 72 mm
BCD isn't a free parameter; it's a derived consequence.

### Approach A — Spur Gear FeatureScript (recommended)

This is the path the table above is pointing at. Two clicks per gear,
no manual involute drawing.

1. In a Part Studio: **Add custom features → search "Spur Gear" →
   install** the Onshape Inc. one. (You only do this once per
   document.)
2. Toolbar → **Spur Gear** icon.
3. Inputs:
   * `Module` = `#gear_module` (= 0.5 mm)
   * `Number of teeth` = 120 for the ring, 24 for the spur
   * `Pressure angle` = 20° (modern; 14.5° only matters for our
     OpenSCAD-rendered preview where build123d hits numerical limits)
   * `Face width` (i.e. thickness) = whatever the door cavity allows.
     For Adam's stack a few mm is fine.
   * **`Internal` = OFF** — both the ring/sun and the spurs are
     external. Flipping Internal ON makes the FeatureScript carve
     teeth into the *inside* of an annulus, which is the wrong
     topology for this build.
   * `Centre hole` — optional. The spurs need one for their
     shoulder-bolt axle; the ring needs one for the 2.003 in mounting
     boss (= 50.876 mm).
4. Pick the sketch plane (Top is fine) and confirm.

The result is a full involute-toothed gear, mathematically perfect.

### Approach B — Sketch + Pattern Remove (manual)

Worth doing **once**, on a low-tooth-count gear, to actually feel how
the involute shape comes out. Don't do this for the 120-tooth ring —
it'll be 120 hand-tuned cuts.

1. **Blank**: a cylinder, diameter = `tip_diameter = m·N + 2·m`.
2. **One tooth gap**: sketch a single tooth-shaped void at the top of
   the blank. The "right" curve is an involute of a base circle
   (`base_diameter = pitch_diameter · cos(pressure_angle)`), but for
   visualisation a symmetric V-shape with the included angle set to
   `360° / N − 2·pressure_angle` reads correctly at low tooth counts.
3. **Extrude → Remove** that sketch through the blank.
4. **Linear/Circular Pattern**: pattern the Remove feature `N` times
   around the axis. The pattern angle is `360° / N`.

For a 24-tooth spur this gets you a passable gear in 5–10 minutes.
For the 120-tooth ring it would take an hour and look worse than the
FeatureScript output. The reason to do it once is so the module /
pitch-circle relationship stops being abstract — you literally
*drew* the pitch circle to position the tooth gap, and you watched
the tooth count drive the pattern step.

### Verifying the mesh in the Assembly tab

Whichever approach you used:

1. Insert the ring and one spur into an Assembly.
2. **Fix** the ring at the origin.
3. **Revolute mate** the spur to a sketch point on the ring's 72 mm
   BCD. The spur should spin freely around its own axis.
4. **Gear Relation**: select the ring's revolute and the spur's
   revolute. Onshape derives the 5:1 ratio from the tooth counts
   (120 / 24); you should not have to type it.
5. Drag the ring with your mouse. The spur spins. If the *teeth visibly
   collide* rather than glide, the centre distance is off by a fraction
   of a mm — usually because the BCD was typed in by hand instead of
   computed from `(m·N_ring + m·N_spur) / 2`.

## Gotchas & lessons learned

_(Add entries here as I run into them.)_
