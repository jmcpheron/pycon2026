// docs/vault/sandbox/ring_gear.scad
//
// Parametric spur gear in pure OpenSCAD -- no external library, no
// FeatureScript. The same gear that Onshape's Spur Gear FeatureScript
// generates with 4 clicks, expressed here as ~20 lines of editable
// expressions. See docs/vault/onshape-vs-openscad.md for the side-by-
// side comparison and the tradeoffs.
//
// Approximation: tooth flanks are STRAIGHT lines drawn from the root
// circle to the tip circle, slanted by the pressure angle. A real
// involute curve would be a 5-8 point arc per flank. The straight-
// flank version reads as a recognisable gear at this scale and is
// quick to grok; if you need a metrology-grade involute, use BOSL2's
// spur_gear() or the build123d / bd_warehouse pipeline in
// src/vault/mechanism.py.
//
// Open in OpenSCAD GUI, View -> Customizer, drag sliders. To export
// the ring gear alone as an STL:
//   openscad -o ring_gear.stl -D 'show_spurs=false' ring_gear.scad

/* [Gear math (the only knobs that affect meshing)] */
m_module       = 0.5;    // module: mm of pitch diameter per tooth
pressure_deg   = 20;     // pressure angle (degrees)

/* [Ring (sun) gear] */
ring_teeth     = 120;    // Adam's vault ring                          [video-01]
ring_thickness = 4;      // face width
ring_bore_dia  = 50.876; // 2.003 in central mounting bore             [Part 2]

/* [Satellite spurs (set false when exporting an STL of the ring only)] */
show_spurs     = true;
spur_teeth     = 24;     // Adam's spur                                [video-01]
spur_thickness = 4;
spur_bore_dia  = 3;      // shoulder-bolt clearance, illustrative
spur_count     = 12;

/* [Resolution] */
fn_res = 150;
$fn = fn_res;

// ---------------------------------------------------------------------
//                       Derived circle radii
// ---------------------------------------------------------------------
// Pure functions of (n, m). These three expressions are EXACTLY what
// Onshape's Spur Gear FeatureScript computes internally before it draws
// any teeth. The whole gear is determined by `m` and `n` -- everything
// else is geometry.

function pitch_radius(n, m) = n * m / 2;
function tip_radius(n, m)   = pitch_radius(n, m) + m;        // addendum  = m
function root_radius(n, m)  = pitch_radius(n, m) - 1.25 * m; // dedendum  = 1.25m

// ---------------------------------------------------------------------
//                       The gear primitive
// ---------------------------------------------------------------------

module gear_2d(n, m, pa) {
    pitch_r = pitch_radius(n, m);
    tip_r   = tip_radius(n, m);
    root_r  = root_radius(n, m);

    // Half the circular pitch -- the tooth's arc thickness at the
    // pitch circle. (Arc ~ chord for small tooth angles.)
    half_arc_at_pitch = m * PI / 4;

    // Cartesian half-widths at the root and tip circles, slanted by
    // the pressure angle.
    half_root_y = half_arc_at_pitch + (pitch_r - root_r) * tan(pa);
    half_tip_y  = max(half_arc_at_pitch - (tip_r - pitch_r) * tan(pa),
                      0.02);  // keep a sliver so the tip isn't a knife edge

    union() {
        circle(r = root_r);
        for (k = [0 : n - 1]) {
            rotate([0, 0, k * 360 / n])
                polygon(points = [
                    [root_r, -half_root_y],
                    [root_r,  half_root_y],
                    [tip_r,   half_tip_y],
                    [tip_r,  -half_tip_y],
                ]);
        }
    }
}

module gear(n, m, pa, thickness, bore_dia) {
    linear_extrude(height = thickness)
        difference() {
            gear_2d(n, m, pa);
            if (bore_dia > 0) circle(d = bore_dia);
        }
}

// ---------------------------------------------------------------------
//                            Render
// ---------------------------------------------------------------------

// Central ring (sun) gear at the origin.
color("Gold")
    gear(ring_teeth, m_module, pressure_deg, ring_thickness, ring_bore_dia);

// Satellite spurs. Centre distance falls straight out of the same
// pitch-radius math:
//
//   centre_distance = pitch_radius(ring) + pitch_radius(spur)
//                   = (120 + 24) * 0.5 / 2  =  36 mm
//
// Which is also (BCD / 2) where BCD = 72 mm -- the number Adam reads
// off his drawing. Knowing m and the tooth counts FORCES the BCD;
// it's not an independent dimension.
if (show_spurs) {
    centre_distance =
        pitch_radius(ring_teeth, m_module)
        + pitch_radius(spur_teeth, m_module);
    color("Silver")
        for (k = [0 : spur_count - 1]) {
            rotate([0, 0, k * 360 / spur_count])
                translate([centre_distance, 0, 0])
                    gear(spur_teeth, m_module, pressure_deg,
                         spur_thickness, spur_bore_dia);
        }
}
