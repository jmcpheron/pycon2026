// docs/vault/sandbox/assembly.scad
//
// Full vault-door assembly: parametric door body + imported gear/rack
// STLs + parametric locking pins. Open in the OpenSCAD GUI, View ->
// Customizer, slide `cam_progress` from 0 to 1 to watch the lock cycle.
//
// Coordinate convention (same as door.scad):
//   z = 0 is the BACK face of the door (cavity opens this way).
//   z = door_thickness_mm is the FRONT face (display side).
//   The gear / rack / pin stack lives inside the cavity, vertically
//   centred on the radial pin bores at z = mid_cavity.
//
// Geometry source: src/vault/vault.py (canonical params) and
// src/vault/mechanism.py (the layered z stack and the rack tangential
// offset that makes the rack-and-pinion mesh geometrically real).
//
// STLs come from docs/vault/assets/parts/, built by
// `uv run vault export-parts`. The renderer there uses
// MECH_GEAR_MODULE_MM = 1.0 and 60/12 tooth counts (not Adam's real
// 0.5 / 120 / 24) -- bd_warehouse's involute generator hits numerical
// limits at higher tooth counts. Same 5:1 ratio, same 72 mm BCD,
// chunkier teeth.

use <door.scad>

/* [Door body] */
// door.scad now models a three-stage tapered puck (back / middle /
// front). The pin bores live in the cylindrical back stage at
// z = door_thickness_mm / 6, and the gear stack rides at the same z so
// the rack-and-pinion drive aligns with the pin axis. These four
// params and the three taper angles below must match door.scad's
// defaults; OpenSCAD's `use <>` cascades them into the door() module
// so changing them here re-renders the imported door correctly.
door_diameter_mm        = 152.4;
door_thickness_mm       = 48;   // SANDBOX default; Adam's stock is 31.75
front_face_mm           = 12.7;
back_stage_taper_deg    = 0;    // straight wall in the pin band
middle_stage_taper_deg  = 6;    // gradual taper
front_stage_taper_deg   = 12;   // bigger taper near the display face

/* [Pins] */
pin_count          = 12;
pin_diameter_mm    = 12;       // Part 2 says 12; Part 4 revises to 10
pin_length_mm      = 30;       // [Part 2] M12 x 30

/* [Spur-axle bolt circle] */
spur_bcd_mm        = 72;       // [Part 2]

/* [Gear stack (rendered geometry from mechanism.py)] */
ring_teeth         = 60;       // MECH_RING_GEAR_TEETH (rendered, not real 120)
spur_teeth         = 12;       // MECH_SPUR_GEAR_TEETH (rendered, not real 24)
gear_module_mm     = 1.0;      // MECH_GEAR_MODULE_MM (rendered)
ring_thickness_mm  = 4.0;
spur_thickness_mm  = 4.0;
rack_stock_mm      = 8.0;      // [Part 2] 8x8 mm

/* [Cam (the master slider)] */
// Drag this from 0 to 1 to watch the lock cycle. cam_progress drives
// both ring rotation and pin extension, mapped through the canonical
// CAM_ROTATION_DEG (10 deg) and PIN_TRAVEL_MM (8 mm) values from
// src/vault/vault.py.
cam_progress       = 0;        // [0:0.05:1]
cam_rotation_max   = 10;       // CAM_ROTATION_DEG
pin_travel_max     = 8;        // PIN_TRAVEL_MM

/* [Visibility toggles] */
show_door          = true;
show_ring          = true;
show_spurs         = true;
show_racks         = true;
show_pins          = true;

/* [Rendering] */
fn_resolution      = 64;       // lower for fast preview while iterating
$fn = fn_resolution;

// ---------------------------------------------------------------------
//                          Derived geometry
// ---------------------------------------------------------------------

_eps = 0.01;
_cavity_depth = door_thickness_mm - front_face_mm;

// Pin bores sit at the centre of the BACK stage (z = t/6). The gear
// stack rides at the same z so the rack-and-pinion drive aligns with
// the pin axis. Must match the bore_z used by door.scad's pin_bores().
_mech_z_center = door_thickness_mm / 6;

// Pitch radii from module / tooth count (bd_warehouse convention).
_ring_pitch_r = gear_module_mm * ring_teeth / 2;        // 30 mm
_spur_pitch_r = gear_module_mm * spur_teeth / 2;        //  6 mm
_spur_center_r = spur_bcd_mm / 2;                       // 36 mm

// Rack tangential offset: the rack sits at +y = (spur pitch radius +
// half rack stock) above the spur's radial line so the spur's top
// tooth meets the rack's underside. This is what makes it a *real*
// rack-and-pinion mesh; see src/vault/mechanism.py _rack_y_offset.
_rack_y_offset = _spur_pitch_r + rack_stock_mm / 2;     // 10 mm

// Where the rack starts (inner end) and ends (outer end), in radius.
_rack_inner_r = _spur_center_r + _spur_pitch_r + gear_module_mm; // ~43 mm
_door_inner_r = door_diameter_mm / 2 - 2.0;
_rack_length = max(_door_inner_r - _rack_inner_r, 20);

// Outer radius of the BACK stage (the cylindrical zone where the pins
// live). Same formula as door.scad's back_stage_outer_r() helper --
// kept duplicated here because OpenSCAD's `use <>` cascades top-level
// VARIABLES across files but not arbitrary function lookups in
// expressions outside a module body.
_back_stage_outer_r =
      door_diameter_mm / 2
    - (door_thickness_mm / 3) * tan(front_stage_taper_deg)
    - (door_thickness_mm / 3) * tan(middle_stage_taper_deg);

// Pin rest centre: pin TIP is flush with the BACK-stage outer wall
// when retracted (cam_progress = 0). When extended (cam_progress = 1)
// the pin tip pokes out into the frame opening by pin_travel_max mm.
// NB pin and rack overlap radially -- mechanism.py renders them
// end-to-end in a flat schematic; in a 3D thick puck the pin has to
// retract INTO the door instead. The overlap is hidden whenever
// show_door is true.
_pin_rest_r = _back_stage_outer_r - pin_length_mm / 2;

// Because the rack and pin sit at +y = _rack_y_offset in the spur's
// LOCAL pre-rotation frame, the pin centre lands at angle atan2(y_off,
// pin_radius) relative to the spur's radial line. We counter-rotate
// the WHOLE per-k frame by -this so the pin lands at the exact 30*k
// degrees the door's bores are drilled at.
_pin_angular_offset = atan2(_rack_y_offset, _pin_rest_r);  // ~8.7 deg

// Cam-driven motion. Linear in cam_progress; the GIF in mechanism.py
// uses a smoothstep, but a plain linear feel reads better when you're
// dragging a slider by hand.
_theta_deg     = cam_progress * cam_rotation_max;
_pin_ext       = cam_progress * pin_travel_max;
_spur_rotation = -_theta_deg * ring_teeth / spur_teeth;   // -5 * theta

// STL z-position. The STLs are built centred at z = thickness / 2 by
// build123d, so to land them at our mid-cavity z we translate by
// (_mech_z_center - thickness/2).
_ring_stl_z = _mech_z_center - ring_thickness_mm / 2;
_spur_stl_z = _mech_z_center - spur_thickness_mm / 2;
_rack_stl_z = _mech_z_center;   // Box centred in all 3 axes

// ---------------------------------------------------------------------
//                            Modules
// ---------------------------------------------------------------------

module ring_gear_stl() {
    translate([0, 0, _ring_stl_z])
        rotate([0, 0, _theta_deg])
            import("../assets/parts/ring-gear.stl", convexity = 6);
}

module spur_gears_stl() {
    for (k = [0 : pin_count - 1]) {
        phi = 360 * k / pin_count - _pin_angular_offset;
        rotate([0, 0, phi])
            translate([_spur_center_r, 0, _spur_stl_z])
                rotate([0, 0, _spur_rotation])
                    import("../assets/parts/spur-gear.stl", convexity = 4);
    }
}

module racks_stl() {
    for (k = [0 : pin_count - 1]) {
        phi = 360 * k / pin_count - _pin_angular_offset;
        // Rack centre slides radially outward by _pin_ext.
        rack_center_r = _rack_inner_r + _rack_length / 2 + _pin_ext;
        rotate([0, 0, phi])
            translate([rack_center_r, _rack_y_offset, _rack_stl_z])
                import("../assets/parts/rack.stl", convexity = 4);
    }
}

// Pins are simple cylinders -- no STL needed. Same +y offset as the
// rack so the pin centreline matches the rack centreline. Pin's
// long-axis is radial (+x in pre-rotation frame); rotated by phi.
module pins() {
    for (k = [0 : pin_count - 1]) {
        phi = 360 * k / pin_count - _pin_angular_offset;
        pin_center_r = _pin_rest_r + _pin_ext;
        rotate([0, 0, phi])
            translate([pin_center_r, _rack_y_offset, _mech_z_center])
                rotate([0, 90, 0])
                    cylinder(h = pin_length_mm, d = pin_diameter_mm,
                             center = true);
    }
}

// ---------------------------------------------------------------------
//                            Main render
// ---------------------------------------------------------------------

if (show_door)  color("Tan",     0.6) door();
if (show_ring)  color("Gold",    1.0) ring_gear_stl();
if (show_spurs) color("Silver",  1.0) spur_gears_stl();
if (show_racks) color("DimGray", 1.0) racks_stl();
if (show_pins)  color("Crimson", 1.0) pins();
