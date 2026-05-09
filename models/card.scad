// scadia PyCon 2026 — printable parametric badge
// 88.9 × 50.8 × 1.6 mm with a print-in-place spinning gear and embossed text.
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

/* [Gear pocket] */
pocket_x      = 27;
pocket_d      = 32;
pocket_depth  = 1.2;
post_d        = 2.4;
post_h        = 1.4;

/* [Print-in-place gear] */
gear_od     = 30;
gear_t      = 1.0;
gear_teeth  = 14;
gear_bore   = 3.0;   // +0.3 mm radial clearance over post_d
gear_z_lift = 0.2;   // sacrificial layer below gear

$fn = 96;

module rounded_card_2d() {
    offset(r = corner_r) offset(r = -corner_r)
        square([card_w, card_h], center = true);
}

module card_blank() {
    difference() {
        linear_extrude(card_t) rounded_card_2d();
        translate([pocket_x, 0, card_t - pocket_depth + 0.01])
            cylinder(d = pocket_d, h = pocket_depth + 0.02);
    }
}

module center_post() {
    translate([pocket_x, 0, card_t - pocket_depth])
        cylinder(d = post_d, h = post_h);
}

module spur_gear() {
    body_d = gear_od - 4;
    union() {
        difference() {
            cylinder(d = body_d, h = gear_t);
            cylinder(d = gear_bore, h = gear_t + 0.02);
        }
        for (i = [0 : gear_teeth - 1])
            rotate([0, 0, i * 360 / gear_teeth])
                translate([body_d / 2 - 0.1, 0, 0])
                    linear_extrude(gear_t)
                        polygon([[0, -1.6], [2.4, 0], [0, 1.6]]);
    }
}

module pip_gear() {
    translate([pocket_x, 0, card_t - pocket_depth + gear_z_lift])
        spur_gear();
}

// Outlined-square placeholder for the real GitHub mark. Inlined here so the
// badge renders standalone without depending on an external SVG.
module gh_mark(s = 6) {
    union() {
        difference() {
            offset(r = 0.4) square([s, s], center = true);
            offset(r = -0.4) square([s, s], center = true);
        }
        text("gh", size = s * 0.55, font = font,
             halign = "center", valign = "center");
    }
}

// Variant 2 from docs/devlog/2026-05-06-card-text-mockups.md:
//   [gh] <name>
//        <github>
module text_layout() {
    translate([-card_w/2 + 7,  6, card_t]) linear_extrude(emboss_h) gh_mark(6);
    translate([-card_w/2 + 12, 6, card_t]) linear_extrude(emboss_h)
        text(name, size = 5, font = font,
             halign = "left", valign = "center");
    translate([-card_w/2 + 7, -6, card_t]) linear_extrude(emboss_h)
        text(github, size = 5, font = font,
             halign = "left", valign = "center");
}

card_blank();
center_post();
pip_gear();
text_layout();
