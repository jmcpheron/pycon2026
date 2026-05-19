// docs/vault/sandbox/rack.scad
//
// Parametric gear rack for the 12-pin vault mechanism. Meshes with a
// module-0.5, 20-deg pressure-angle, 24-tooth spur pinion -- the
// satellite spurs documented in docs/vault/onshape-notes.md.
//
// Why here and not in Onshape: Onshape's standard rack FeatureScripts
// have uneven support across versions, and a rack is dead simple to
// express directly. So the rack source-of-truth lives in this .scad
// file (git-trackable, diffable) and the STL goes straight to the
// slicer for printing.
//
// **The tooth profile is mathematically exact, not an approximation.**
// A rack is the involute's degenerate case at infinite radius -- the
// involute curve flattens out into a straight line slanted by the
// pressure angle. So `polygon()` with four points per tooth is the
// correct mating shape for a module-matched spur, not a simplification.
//
// To export the rack alone (no pinion) for printing:
//   openscad -o rack.stl -D 'show_pinion_for_mesh_check=false' rack.scad
//
// To visualise the mesh with the 24T pinion in the GUI:
//   set `show_pinion_for_mesh_check = true` in the Customizer.

use <ring_gear.scad>

/* [Gear math (must match the pinion in onshape-notes.md)] */
m_module       = 0.5;     // module: mm of pitch DIAMETER per tooth
pressure_deg   = 20;      // pressure angle (degrees)
face_width_mm  = 6;       // depth (z) -- match the pinion's Depth setting

/* [Rack body] */
num_teeth      = 12;      // tooth count on the toothed strip
stock_height_mm = 8;      // total cross-section height; Adam's stock is 8x8 mm
end_pad_mm     = 1;       // overhang past first/last tooth root corner

/* [Mounting stud (the end that attaches to the pin)] */
include_stud   = true;
stud_dia_mm    = 4;       // diameter of cylindrical stud
stud_length_mm = 10;      // how far it sticks out past the rack body

/* [Mesh-preview pinion (visual confirmation only -- not exported)] */
show_pinion_for_mesh_check = false;
pinion_teeth   = 24;      // matches the satellite spur

/* [Resolution] */
fn_res = 120;
$fn = fn_res;

// ---------------------------------------------------------------------
//                       Derived rack geometry
// ---------------------------------------------------------------------
// Standard ISO/AGMA rack math. Adapt these expressions and the tooth
// polygon below if you ever want a non-standard tooth profile (e.g.
// stub teeth, extended addendum).

_addendum       = m_module;          // tooth height above pitch line
_dedendum       = 1.25 * m_module;   // tooth depth below pitch line
_circular_pitch = PI * m_module;     // distance between matching tooth points

// Tooth half-widths at the three reference y-levels.
_half_pitch_w = _circular_pitch / 4;
_half_tip_w   = _half_pitch_w - _addendum * tan(pressure_deg);
_half_root_w  = _half_pitch_w + _dedendum * tan(pressure_deg);

// y-levels. y = 0 is the BACK face of the rack (opposite the teeth).
// y_tip = stock_height_mm is the original top-of-stock; teeth are
// "cut into" the top of the stock down to y_root.
_y_tip   = stock_height_mm;
_y_pitch = _y_tip - _addendum;
_y_root  = _y_tip - _addendum - _dedendum;

// First tooth center x. Pad slightly so the strip doesn't end right
// on a root corner -- looks cleaner and prints better.
_first_tooth_cx = end_pad_mm + _half_root_w;
_total_length   = _first_tooth_cx
                  + (num_teeth - 1) * _circular_pitch
                  + _half_root_w + end_pad_mm;

// ---------------------------------------------------------------------
//                            Modules
// ---------------------------------------------------------------------

// One tooth in 2D, centred on x=0. Walks CCW: bottom-right root, up
// the right flank to the tip, across the tip, down the left flank.
module rack_tooth_2d() {
    polygon(points = [
        [ _half_root_w, _y_root],
        [ _half_tip_w,  _y_tip],
        [-_half_tip_w,  _y_tip],
        [-_half_root_w, _y_root],
    ]);
}

// 2D outline of the entire rack: backing strip up to the root level,
// then N teeth sticking up to the tip level.
module rack_2d() {
    union() {
        square([_total_length, _y_root]);
        for (k = [0 : num_teeth - 1]) {
            translate([_first_tooth_cx + k * _circular_pitch, 0])
                rack_tooth_2d();
        }
    }
}

// 3D rack: 2D profile extruded along z by the face width.
module rack_solid() {
    linear_extrude(height = face_width_mm)
        rack_2d();
}

// Cylindrical stud sticking out the +x end of the rack, axis along
// +x, centred on the rack's cross-section middle. Print smooth and
// tap to thread, or model a hole for a heat-set insert if your
// printer can't hold the thread.
module mounting_stud() {
    translate([_total_length, stock_height_mm / 2, face_width_mm / 2])
        rotate([0, 90, 0])
            cylinder(h = stud_length_mm, d = stud_dia_mm);
}

// One pinion gear, sized and placed to demonstrate the mesh. Pinion
// centre sits `pinion_pitch_radius` above the rack's pitch line, so
// the pitch line is tangent to the pitch circle -- the geometric
// definition of "in mesh".
module mesh_preview_pinion() {
    pinion_pitch_r = m_module * pinion_teeth / 2;
    // Mid-rack x for the pinion location.
    cx = _total_length / 2;
    // y so the pinion pitch circle is tangent to the rack pitch line.
    cy = _y_pitch + pinion_pitch_r;
    color("Silver", 0.9)
        translate([cx, cy, 0])
            // gear(n, m, pa, thickness, bore_dia) -- from ring_gear.scad
            gear(pinion_teeth, m_module, pressure_deg, face_width_mm, 3);
}

// ---------------------------------------------------------------------
//                            Main render
// ---------------------------------------------------------------------

color("DimGray") {
    union() {
        rack_solid();
        if (include_stud) mounting_stud();
    }
}

if (show_pinion_for_mesh_check) mesh_preview_pinion();

// ---------------------------------------------------------------------
// Printing notes
// ---------------------------------------------------------------------
// At m_module = 0.5, the tip width is ~0.21 mm. That's narrower than
// a typical 0.4 mm FDM nozzle, so the tip will print as a single
// rounded bead. Fine for a low-load study rack; for a load-bearing
// rack consider:
//   * bumping m_module to 1.0 (tip width 0.42 mm -- one bead wide)
//   * printing with a 0.2 mm nozzle
//   * printing in nylon or polycarbonate instead of PLA
// Print orientation matters too: lay the rack flat on the bed with
// teeth pointing UP so each tooth is built up in layers from the
// root rather than hanging off the side.
