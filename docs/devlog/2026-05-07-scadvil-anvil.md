# Building the SCADvil — first attempt

*2026-05-07 · jmcpheron*

<!-- TODO(jmcpheron): one or two sentences in your voice on what the SCADvil is and why it
     leads off Phase 3. Suggested beats: project mascot / calibration object / not the
     Benchy boat / the fun half of the demo arc that pairs with the more serious Pi mounts. -->

## 00:20 — first generation

After a first attempt that got stuck rendering a `minkowski()`-wrapped model for over six minutes, I tightened the prompt with explicit OpenSCAD guardrails (no `minkowski()` / `hull()`, `$fn = 24`, sharp edges OK). Second run converged on iter-0 — the controller stopped because the vision critic gave it 8/10 with no blocking issues.

**Prompt:**

```text
Create a 3D-printable OpenSCAD calibration anvil.

Design constraints to keep render time low:
- Use only cube(), cylinder(), and sphere() primitives.
- Do NOT use minkowski() or hull() — they are too slow on this OpenSCAD version.
- Use $fn = 24 globally.
- Avoid global edge rounding. Sharp edges are fine.

The anvil should include:
- A flat base (a wide cube), designed to print flat-side down.
- A block body sitting on the base.
- A tapered horn extending from one side (a cube or wedge, no hull).
- A short heel block on the other side.
- One 4 mm circular tolerance hole, drilled vertically through the body.
- Embossed text "PYCON" recessed into one side face.

Target ~50 mm wide. Keep it simple and printable on FDM at 0.2 mm layers.
```

**What scadia produced (iter-0):**

![iter-0 render of the SCADvil](assets/2026-05-07-scadvil-anvil/render.png)

| | |
|---|---|
| Stop reason | `critic marked design done` |
| Score | 8 / 10 |
| Blocking issues | 0 |
| Iterations | 1 of 3 (controller stopped early) |
| Source | [`models/scadvil.scad`](../../models/scadvil.scad) — checked in verbatim from the run |

The critic's only nonblocking notes were that the embossed text was too subtle and the tolerance hole wasn't visible from the rendered angle. It graded the shape favorably and stopped.

## What the loop missed

Reading the actual `.scad` source surfaced three CSG bugs the vision critic couldn't see:

**1. The "tolerance hole" is a peg, not a hole.** The agent defined `tolerance_hole()` as a `cylinder()` and called it from inside `module anvil()` — which composes its children by implicit union. Only the text emboss gets subtracted at the bottom. So the hole is positive geometry. That cylinder you can see protruding from the top of the body is what was supposed to be a 22 mm vertical drill.

```scad
module anvil() {
    cube([55, 35, 4], center = true);          // base
    translate([0, 0, 9]) cube([45, 30, 14], center = true);  // body
    // ...
    tolerance_hole();   // ← this is a union, not a difference
}
```

**2. The embossed PYCON text is floating in space.** The body's top face sits at z ≈ 16, but the text emboss `cube([..., 0.8])`s are translated to z = 19.5 — 3.5 mm above the body. The top-level `difference(anvil(), text_emboss())` only carves where geometry overlaps, so most of the letters subtract from nothing.

**3. The horn isn't really tapered.** The agent approximated a wedge by differencing one cube from another — slicing a corner off rather than producing a smooth taper. Dimensionally fine, visually unconvincing.

<!-- TODO(jmcpheron): your take on what these bugs mean for the demo / the talk.
     Some angles to consider, pick whichever you want:

     - The vision sensor looks at a render. It can't tell whether a cylinder is positive
       or negative geometry — that information lives in the SCAD AST, not the pixels.
     - A second sensor that reasoned about primitive *roles* (or even just a volume-
       conservation check on the STL) would have caught Bug 1.
     - "AI critique passed" is not the same as "the artifact is correct." A reminder
       that the loop has blind spots — and showing those is more honest demo material
       than a clean success.
     - Or maybe: this is iter-0 of three. Letting the loop run further (or sharpening
       the prompt to specify difference()) would likely fix it. Worth a follow-up post.
   -->

## What's next

1. Print this anvil as-is and see how the bugs show up in plastic. The peg-where-a-hole-should-be will be visible at a glance; the floating text will simply not exist on the print.
2. Decide whether the next post is *"refining the SCADvil prompt"* (sharpen the brief, add `difference()` and side-face placement language) or *"adding a third sensor"* (a code-aware AST/STL check that would have caught these bugs).
3. Stay on the `raspberry-pi-demos` branch — the Pi 5 wall mount and retro case follow this same workflow and will land in their own posts.

## 00:25 — printed object

<!-- TODO(jmcpheron): photo of the printed SCADvil (or the print attempt, including
     however the peg-vs-hole bug looks in plastic) + 1–2 lines on how it came off
     the printer. Append as a new ## HH:MM section here when the print is done. -->
