// scadia PyCon 2026 — printable parametric badge
// 88.9 × 50.8 × 1.6 mm with TWO print-in-place gears engaged in the upper-left:
//   - a big dial (the knob you spin)
//   - a smaller hex GitHub-logo gear that's engaged with the dial
// Embossed name + handle along the bottom.
//
// Override the embossed text from the command line via badgeforge:
//   uv run badgeforge build --name "Your Name" --github "yourhandle"
// or directly with OpenSCAD:
//   openscad -D 'name="Jane"' -D 'github="janedev"' -o out.stl card.scad

/* [Identity] */
name   = "jmcpheron";
github = "pycon2026";

/* [Card] */
card_w     = 88.9;
card_h     = 50.8;
card_t     = 1.6;
corner_r   = 4.5;
emboss_h   = 0.4;
font       = "Liberation Mono:style=Bold";

/* [Dial gear — the spinner] */
dial_x       = -card_w/2 + 14;          // upper-left, inset 14 mm
dial_y       =  card_h/2 - 14;
dial_od      = 18;
dial_t       = 1.0;
dial_teeth   = 16;
dial_bore    = 3.0;

/* [Hex GH gear — engaged with the dial] */
// Engagement geometry: dial body_d=14 → tooth tip reach 9.3mm; hex_pp=16 → hex point 8mm.
// Center distance 15.5 puts a tooth tip ~0.7 mm past the hex flat — visible mesh,
// dial spin will step the hex (occasional bind by design).
hex_center_d = 15.5;
hex_x        = dial_x + hex_center_d;
hex_y        = dial_y;
hex_pp       = 16;                      // hex point-to-point diameter
hex_t        = 1.0;
hex_bore     = 3.0;

/* [Pocket — peanut-shaped, encompasses both gears] */
pocket_depth = 1.2;
post_d       = 2.4;
post_h       = 1.4;
gear_z_lift  = 0.2;

$fn = 96;

// ─── card body ──────────────────────────────────────────────────────────
module rounded_card_2d() {
    offset(r = corner_r) offset(r = -corner_r)
        square([card_w, card_h], center = true);
}

// Peanut-shaped recess: union of two circles, one per gear
module pocket_2d() {
    translate([dial_x, dial_y]) circle(d = dial_od + 2);
    translate([hex_x, hex_y]) circle(d = hex_pp + 1.5);
}

module card_blank() {
    difference() {
        linear_extrude(card_t) rounded_card_2d();
        translate([0, 0, card_t - pocket_depth + 0.01])
            linear_extrude(pocket_depth + 0.02) pocket_2d();
    }
}

// ─── posts (one per gear) ───────────────────────────────────────────────
module dial_post() {
    translate([dial_x, dial_y, card_t - pocket_depth])
        cylinder(d = post_d, h = post_h);
}

module hex_post() {
    translate([hex_x, hex_y, card_t - pocket_depth])
        cylinder(d = post_d, h = post_h);
}

// ─── big dial: standard 16-tooth spur gear ──────────────────────────────
module dial_gear() {
    body_d = dial_od - 4;
    union() {
        difference() {
            cylinder(d = body_d, h = dial_t);
            cylinder(d = dial_bore, h = dial_t + 0.02);
        }
        for (i = [0 : dial_teeth - 1])
            rotate([0, 0, i * 360 / dial_teeth])
                translate([body_d / 2 - 0.1, 0, 0])
                    linear_extrude(dial_t)
                        polygon([[0, -1.6], [2.4, 0], [0, 1.6]]);
    }
}

// ─── hex GH gear: regular hexagon with "GH" engraved on top ─────────────
// Text is shifted up so the central bore (post tip is visible there) sits
// below the lettering instead of cutting through it.
module hex_gear() {
    difference() {
        // Hex body — circle($fn=6) gives point-to-point = d
        linear_extrude(hex_t) circle(d = hex_pp, $fn = 6);
        // Center bore for the post
        translate([0, 0, -0.01])
            cylinder(d = hex_bore, h = hex_t + 0.02);
        // GH text engraved on top face, shifted up clear of the bore
        translate([0, 2.6, hex_t - 0.35 + 0.01])
            linear_extrude(0.35 + 0.02)
                text("GH", size = 4.5, font = font,
                     halign = "center", valign = "center");
    }
}

module pip_dial() {
    translate([dial_x, dial_y, card_t - pocket_depth + gear_z_lift])
        dial_gear();
}

module pip_hex() {
    translate([hex_x, hex_y, card_t - pocket_depth + gear_z_lift])
        hex_gear();
}

// ─── bottom-of-card text ────────────────────────────────────────────────
module text_layout() {
    translate([-card_w/2 + 7, -7, card_t]) linear_extrude(emboss_h)
        text(name, size = 5.5, font = font,
             halign = "left", valign = "center");
    translate([-card_w/2 + 7, -16, card_t]) linear_extrude(emboss_h)
        text(github, size = 5.5, font = font,
             halign = "left", valign = "center");
}

card_blank();
dial_post();
hex_post();
pip_dial();
pip_hex();
text_layout();
