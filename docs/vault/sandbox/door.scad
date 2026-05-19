// docs/vault/sandbox/door.scad
//
// Local OpenSCAD playground for the vault-door BODY only (no gears).
// Open in OpenSCAD GUI, View -> Customizer, drag sliders. See README.md
// in this directory for the why and the export commands.
//
// Parameter names mirror src/vault/vault.py so the two representations
// stay grep-able against each other. Defaults are copied verbatim from
// the canonical Python values; the source tag in each comment points at
// the docs/vault/*.md file the number came from.
//
// Coordinate convention: door axis is +z. z=0 is the BACK face (vault
// side); z=door_thickness_mm is the FRONT face (display side). Pin
// bores run radially inward from the rim, perpendicular to z.

/* [Door body] */
// Part 3 shows the door edge as THREE roughly-even axial stages, each
// ~1/3 of the door thickness:
//   * Back  (z = [0, t/3])   : near-cylindrical. PIN BORES live here.
//   * Middle(z = [t/3, 2t/3]): gradual taper outward.
//   * Front (z = [2t/3, t])  : bigger taper, lands on the display face.
// For a 12 mm pin to fit comfortably inside the back stage (~2 mm of
// wall above & below the bore), each stage needs >= ~16 mm. So a 48 mm
// total thickness is the floor; Adam's actual 1.25 in (31.75 mm) stock
// forces the pin to straddle the back/middle stage boundary.
door_diameter_mm     = 152.4;  // 6 in OD at the front face       [Part 2]
door_thickness_mm    = 48;     // SANDBOX choice; Adam's stock is 31.75 [Part 2/3]
front_face_mm        = 12.7;   // 0.5 in solid face before cavity [Part 3]
back_stage_taper_deg = 0;      // back wall vertical -- pin bores want this [Part 3]
middle_stage_taper_deg = 6;    // gradual taper                   [Part 3]
front_stage_taper_deg  = 12;   // bigger taper, lands on the rim  [Part 3]

/* [Pins] */
pin_count          = 12;       // 12 pins / 30 deg spacing       [video-01]
pin_diameter_mm    = 12;       // 12 (Part 2) vs 10 (Part 4 revision) - try both
pin_bore_clearance = 0.2;      // diametral slip-fit clearance

/* [Spur-axle bolt circle] */
spur_bcd_mm        = 72;       // 12 holes at 30 deg around BCD  [Part 2]
spur_axle_dia_mm   = 4;        // shoulder-bolt smooth shoulder, illustrative
spur_axle_depth_mm = 6;        // how deep the axle holes go from front face

/* [Ring-gear boss (central recess on the inside face)] */
ring_boss_id_mm    = 50.876;   // 2.003 in slip-cut for ring gear[Part 2]
ring_boss_depth_mm = 4;        // recess depth on the back-side face

/* [Rendering] */
fn_resolution      = 96;       // $fn for round bodies. Drop to 32 for fast preview.
show_cutaway       = false;    // 120 deg wedge subtract so you can see inside

// ---------------------------------------------------------------------
//                                Hidden
// ---------------------------------------------------------------------

// Hidden derived values. The leading `_` keeps them out of Customizer.
_eps = 0.01;                              // boolean-subtract overlap fudge
_cavity_id_mm = max(spur_bcd_mm + 12, 84); // wide enough to clear spur ring

$fn = fn_resolution;

// ---------------------------------------------------------------------
//                            Modules
// ---------------------------------------------------------------------

// The three-stage tapered puck. Real vault doors "thunk" into a
// matching tapered seat in the frame -- bigger at the front (display
// side, +z), smaller at the back (vault side, z=0). Part 3 shows the
// edge is built up from THREE stacked frusta, evenly spaced in z, each
// with its own taper angle. Built as a 6-vertex polygon swept around
// the z-axis via rotate_extrude.
module door_body() {
    t          = door_thickness_mm;
    z_back_top   = t / 3;
    z_middle_top = 2 * t / 3;
    z_front_top  = t;

    r_front       = door_diameter_mm / 2;
    front_dr      = (t / 3) * tan(front_stage_taper_deg);
    middle_dr     = (t / 3) * tan(middle_stage_taper_deg);
    back_dr       = (t / 3) * tan(back_stage_taper_deg);
    r_middle_top  = r_front - front_dr;
    r_back_top    = r_middle_top - middle_dr;
    r_back        = r_back_top - back_dr;

    rotate_extrude(angle = 360, convexity = 4)
        polygon(points = [
            [0,             0],            // axis, back face
            [r_back,        0],            // back-face outer corner
            [r_back_top,    z_back_top],   // back / middle transition
            [r_middle_top,  z_middle_top], // middle / front transition
            [r_front,       z_front_top],  // front-face outer corner
            [0,             z_front_top],  // axis, front face
        ]);
}

// Helper: the back-stage outer radius, used to position pin bores so
// they start a hair outside the smallest stage wall.
function back_stage_outer_r() =
    (door_diameter_mm / 2)
    - (door_thickness_mm / 3) * tan(front_stage_taper_deg)
    - (door_thickness_mm / 3) * tan(middle_stage_taper_deg);

// The internal cavity that houses the gear mechanism. Sits behind a
// solid front face of `front_face_mm` so the cavity does not break
// through to the display side. Open to the back of the door.
module door_cavity() {
    cavity_depth = door_thickness_mm - front_face_mm + _eps;
    translate([0, 0, -_eps])
        cylinder(h = cavity_depth, d = _cavity_id_mm);
}

// N radial bores, one per pin, evenly spaced around the rim. Bore z
// is centred in the BACK stage (z = t/6) so the pin sits entirely in
// the cylindrical back zone -- away from the tapered side walls. The
// rack-and-pinion mechanism in the cavity must sit at the same z so
// the rack can drive the pin (see assembly.scad's _mech_z_center).
module pin_bores() {
    bore_z = door_thickness_mm / 6;
    bore_length = door_diameter_mm / 2 - _cavity_id_mm / 2 + 2 * _eps;
    for (i = [0 : pin_count - 1]) {
        rotate([0, 0, 360 * i / pin_count])
            translate([_cavity_id_mm / 2 - _eps, 0, bore_z])
                rotate([0, 90, 0])
                    cylinder(h = bore_length,
                             d = pin_diameter_mm + pin_bore_clearance);
    }
}

// N small holes on the inside face for the spur-gear shoulder-bolt
// axles. Sanity check: at default pin_count=12 these should sit on the
// 72 mm BCD at exactly 30 deg apart. The 24-hole / fill-every-other
// pattern Adam describes in video-01 is what we are emulating here.
module spur_axle_holes() {
    // Holes drilled from the BACK face inward (Adam machines them on
    // the inside of the door). Z origin is the back face.
    for (i = [0 : pin_count - 1]) {
        rotate([0, 0, 360 * i / pin_count])
            translate([spur_bcd_mm / 2, 0, -_eps])
                cylinder(h = spur_axle_depth_mm + _eps,
                         d = spur_axle_dia_mm);
    }
}

// Central pocket on the back face for the ring-gear mounting boss.
// Adam's "slip cut" at 2.003 in (Part 2).
module ring_boss_recess() {
    translate([0, 0, -_eps])
        cylinder(h = ring_boss_depth_mm + _eps, d = ring_boss_id_mm);
}

// Sector wedge subtraction so you can see inside the cavity in preview
// without rendering F6 quality. 120 deg wedge so the cutaway leaves
// 240 deg of door visible -- enough to read 8 of the 12 pin bores at
// once.
module cutaway() {
    h = door_thickness_mm + 2 * _eps;
    translate([0, 0, -_eps])
        linear_extrude(height = h)
            polygon(points = [
                [0, 0],
                [door_diameter_mm, 0],
                [door_diameter_mm * cos(120), door_diameter_mm * sin(120)],
            ]);
}

// ---------------------------------------------------------------------
//                            Main render
// ---------------------------------------------------------------------

// Wrapped in a module so assembly.scad can `use <door.scad>` and call
// `door()` without this file's top-level render firing on import.
module door() {
    difference() {
        door_body();
        door_cavity();
        pin_bores();
        spur_axle_holes();
        ring_boss_recess();
        if (show_cutaway) cutaway();
    }
}

door();

// ---------------------------------------------------------------------
// Source tags. Every constant above can be traced to one of these files:
//   [video-01] docs/vault/video-01-ring-gear-machining.md
//   [Part 2]   docs/vault/part-2.md  (door body, BCD, ring boss, pin diameter)
//   [Part 3]   docs/vault/part-3.md  (door thickness, front face, taper, frame clearance)
//   [Part 4]   docs/vault/part-4.md  (revised 10 mm pin diameter, rack details)
//   [Part 5]   docs/vault/part-5.md  (combo lock cage -- out of scope for door body)
// Canonical Python source of truth: src/vault/vault.py
// ---------------------------------------------------------------------
