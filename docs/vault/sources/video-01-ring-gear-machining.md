# Video 01 — Ring gear machining

- **URL:** https://www.youtube.com/watch?v=SiL8IzJSnyU
- **What it covers:** Adam machines the 120-tooth ring gear from a solid
  cylinder of 416 stainless steel. Discusses the gear math for the full vault,
  the 1/12-scale simplification he chose, and shows a black test plate where
  the spur gears mount around the ring gear to verify meshing. Locking pins
  are described from his technical drawing but not yet machined.
- **Watched:** 2026-05-06
- **Distilled into:** `../specs.md`, `../onshape-notes.md`

This file preserves the unfiltered initial research so the canonical specs are
always traceable back to a source.

---

## Core gear math

For gears to mesh — in CAD or in real life — they must share the same
**Module** (often just "Mod").

- **Gear Module:** 0.5 mm. Critical number for generating gears in Onshape.
- **Real-world vault door (base 12):** 24 spur gears (24 teeth each) around a
  288-tooth ring gear.
- **Adam's 1/12-scale version:** halves the math.
  - Spur gears (and locking pins): 12
  - Spur gear teeth: 24 each
  - Ring gear teeth: 120

## Ring gear specs

- Material: 416 stainless steel (FYI; not needed for CAD).
- Outer diameter: 2.401 in (basically exactly 2.4 in).
- Number of teeth: 120.
- Depth of gear cut: 0.044 in (44 thousandths) from outer diameter to root of
  the tooth.

## Layout and spacing (the base plate)

Adam shows a black rectangular test plate where the spur gears mount to test
meshing with the ring gear.

- Dividing plate on the mill: 15° increments. 360 / 15 = 24, so the test plate
  has 24 holes drilled in a circle.
- Adam fills only every other hole — 12 spur gears at 30° spacing.
- For CAD: sketch the bolt-circle with 12 points, 30° apart.

## Locking pins

Not yet built in this video, but Adam shows the technical drawing.

- Pin diameter: 12 mm.
- Each pin's bottom has a straight gear "rack" machined into it.
- Turning the 120-tooth ring gear turns all twelve 24-tooth spur gears, which
  drive the racks, which push all 12 pins outward into the vault wall in unison.

## Onshape modeling tips (from the same source)

1. **Use the Spur Gear FeatureScript** — don't hand-draw involute teeth. Add
   custom features → search "Spur Gear".
2. **Spur gear:** Module 0.5 mm, 24 teeth.
3. **Ring gear:** same generator, set to Internal Gear, Module 0.5 mm, 120
   teeth. Outer diameter should land on Adam's 2.4 in.
4. **Mate connectors:** in Assembly, Revolute Mate to fix gears to the base
   plate, then Gear Relation to make them spin together. Onshape computes the
   ratio from tooth counts (120:24 = 5:1).
