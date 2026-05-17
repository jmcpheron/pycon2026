# Vault build — specifications

Single source of truth for every dimension, count, and material call-out.
Each entry tagged with the source it came from (e.g. `[video-01]`), so when
Adam revises a number in a later video the trail stays clear.

Sources legend:
- `[video-01]` — Adam machining the ring gear from a stainless cylinder
  (https://www.youtube.com/watch?v=SiL8IzJSnyU)
- `[Part 2]` — pins, racks, acrylic hub body — `part-2.md`
- `[Part 3]` — vault-door puck, frame plate, hinge — `part-3.md`
- `[Part 4]` — rack concentricity rework, revised pin diameter — `part-4.md`
- `[Part 5]` — miniature combination lock cage — `part-5.md`

---

## Global gear math

| Parameter | Value | Source |
| --- | --- | --- |
| Gear module | 0.5 mm | [video-01] |
| Scale (relative to a real vault door) | 1/12 | [video-01] |

The module is the parameter that has to match across every gear that meshes,
so it is the single most important number in the file.

## Real-world reference (for context, not for modeling)

Real vault doors: 24 spur gears (24 teeth each) around a 288-tooth ring gear.
Adam's miniature halves this — see below. `[video-01]`

## Ring gear

| Parameter | Value | Source |
| --- | --- | --- |
| Teeth | 120 | [video-01] |
| Outer diameter | 2.401 in (≈ 2.4 in) | [video-01] |
| Depth of gear cut (OD to root of tooth) | 0.044 in | [video-01] |
| Material (Adam's build, FYI only) | 416 stainless | [video-01] |

## Spur gears

| Parameter | Value | Source |
| --- | --- | --- |
| Count | 12 | [video-01] |
| Teeth (each) | 24 | [video-01] |
| Bolt-circle hole spacing | 30° (12 holes evenly around) | [video-01] |

Adam's mill dividing plate has 24 holes (15° spacing), but he only fills every
other one for the 12-pin door.

## Locking pins

| Parameter | Value | Source |
| --- | --- | --- |
| Count | 12 (one per spur gear) | [video-01] |
| Diameter | 12 mm | [video-01] |
| Drive mechanism | Straight rack on bottom face, driven by spur gear | [video-01] |

## Door body (the acrylic / cast-iron puck)

| Parameter | Value | Source |
| --- | --- | --- |
| Outer diameter (at the front face) | 6 in (152.4 mm) | [Part 2] |
| Stock thickness (Adam's as-built) | 1.25 in (31.75 mm) | [Part 2] |
| Sandbox thickness (see "Three-stage edge profile" below) | 48 mm | derived |
| Material (Part 2) | Cast acrylic (for the visualisation hub) | [Part 2] |
| Material (Part 3) | Cast iron (the real heavy puck) | [Part 3] |
| Front-face solid thickness (before cavity) | 0.5 in (12.7 mm) | [Part 3] |
| Internal cavity depth (Adam's stock) | 0.75 in (19.05 mm) | [Part 3] |
| Door-thinning required for swing clearance | 0.75 in (19.05 mm) of push-back | [Part 3] |
| Ring-gear boss inner diameter ("slip cut") | 2.003 in (50.876 mm) | [Part 2] |

### Three-stage edge profile

The Part 3 video shows the door edge is NOT a single conical taper —
it's three roughly-even axial stages stacked back-to-front, each
~1/3 of the total thickness:

| Stage | z range | Wall character | Role |
| --- | --- | --- | --- |
| **Back** | [0, t/3] | Near-cylindrical (≈ 0°) | Houses the 12 radial pin bores. The wall has to be straight so the bores are perpendicular to a parallel surface. |
| **Middle** | [t/3, 2t/3] | Gradual taper (≈ 6°) | Intermediate transition. |
| **Front** | [2t/3, t] | Bigger taper (≈ 12°) | Lands on the display face. This is the angle that does most of the "thunk into the frame seat" work. |

Where `t` is the total door thickness.

**Why the sandbox uses 48 mm instead of Adam's 31.75 mm**: at the
canonical 12 mm pin diameter, the back stage needs to contain the pin
bore cleanly — diameter 12 + 0.2 mm clearance + ~2 mm of wall above and
below = ~16 mm of z-height per stage. Three even stages of 16 mm = 48
mm total. Adam's 31.75 mm stock gives each stage only ~10.6 mm, which
forces the pin to straddle the boundary between the back stage and the
middle stage rather than living entirely inside the back stage. The
sandbox model favours a clean back-stage placement; the as-built
column is preserved as a separate row above.

## Pin layout & spur-axle bolt circle

| Parameter | Value | Source |
| --- | --- | --- |
| Spur-axle bolt-circle diameter (BCD) | 72 mm | [Part 2] |
| Spur-axle hole count | 12 (every other hole of the 24-hole dividing-plate pattern) | [video-01] |
| Angular spacing | 30° | 360 / 12 |
| Pin bores | 12 radial, through the rim, into the cavity | [Part 2] |
| Shoulder-bolt smooth-shoulder slip-fit clearance to spur-gear bore | 0.1 mm | [Part 2] |

## Pin & rack mechanism (revisions and details)

| Parameter | Value | Source |
| --- | --- | --- |
| Pin diameter (Part 2 drawing) | 12 mm ("M12 × 30") | [Part 2] |
| Pin diameter (Part 4 revision, measured from physical part) | 10 mm | [Part 4] |
| Pin length | 30 mm | [Part 2] |
| Pin base thread | M6 (rack screws into the pin base) | [Part 2] |
| Rack stock | 8 × 8 mm square | [Part 2] |
| Rack module | Mod 0.5 (matches ring + spur) | [Part 2] |
| Rack threaded stud | 6 mm Ø, M6 (turned from the 8 mm square) | [Part 2] |
| Rack back-face relief | Curved (ball-end-mill) to clear ring gear | [Part 2] |
| Rack quantity made | 14 (12 needed; "always make more than you need") | [Part 4] |
| Rack tooth-zero-point alignment tolerance | within 0.1 mm of all 12 racks | [Part 2] |
| Concentricity error from hand-cut thread (the trap to avoid in CAD) | 0.0125 in (≈ 0.32 mm) | [Part 4] |

## Frame plate & door swing (Part 3, FYI for the full build)

| Parameter | Value | Source |
| --- | --- | --- |
| Frame plate material | 1/2 in 6061 aluminium | [Part 3] |
| Frame plate footprint | ≈ 10–12 in square | [Part 3] |
| Frame opening | 6 in bore | [Part 3] |
| Door-to-frame radial clearance | 0.020 in (0.508 mm) | [Part 3] |
| Hinge thrust bearings | 3/8 in OD on a 1/8 in centre pin | [Part 3] |
| Hinge fasteners | 28 × M2 screws (M6 is Adam's plan B) | [Part 3] |

## Combination lock cage (Part 5, future scope)

| Parameter | Value | Source |
| --- | --- | --- |
| Cage envelope | 0.75 in long × 0.5 in wide | [Part 5] |
| Cage wall material | 0.025 in (≈ 0.64 mm) brass sheet | [Part 5] |
| Combination wheels | 3 wheels | [Part 5] |
| Wheel diameter | 0.450 in | [Part 5] |
| Spindle | 1/8 in brass rod through the door | [Part 5] |
| Dial tick divisions | 36 (one per 10°) | [Part 5] |

## Derived values

| Parameter | Value | Notes |
| --- | --- | --- |
| Drive ratio (ring : spur) | 5 : 1 | 120 / 24. Onshape's Gear Relation tool will compute this automatically from tooth counts. |
| Spur centres relative to ring centre | 36 mm | BCD / 2 |
| Pins per 30° wedge | 1 | 12 pins, 360 / 12 |

## Discrepancies (numbers that disagree between sources)

These are the open decisions. When you pick a winner, update both
`src/vault/vault.py` and the row above to match.

| Param | `src/vault/vault.py` | Video transcript | Decision |
| --- | --- | --- | --- |
| Locking pin diameter | `MECH_LOCKING_PIN_DIA_MM = 12.0` | 12 mm `[Part 2 drawing]` → revised 10 mm `[Part 4 physical part]` | (TBD) |
