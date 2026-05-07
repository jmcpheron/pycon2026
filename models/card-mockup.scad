// Text/logo layout mockups for the PyCon 2026 business card.
// This file is for design exploration only — production geometry is in card.scad.
//
// Render all six variants:
//   for n in 1 2 3 4 5 6; do
//     openscad -D variant=$n -o variant-$n.png \
//       --imgsize 1400,800 --camera 0,0,90,0,0,0,90 \
//       --projection ortho --colorscheme Cornfield --render \
//       card-mockup.scad
//   done

variant = 1;

card_w   = 88.9;
card_h   = 50.8;
card_t   = 1.6;
corner_r = 4.5;
emboss_h = 0.4;
font     = "Liberation Mono:style=Bold";
pocket_x = 27;
pocket_d = 32;

$fn = 64;

module rounded_card() {
    linear_extrude(card_t)
        offset(r =  corner_r) offset(r = -corner_r)
            square([card_w, card_h], center = true);
}

// Faint outline showing where the gear pocket lands — keeps the
// "available real estate" honest in every mockup.
module pocket_marker() {
    translate([pocket_x, 0, card_t + 0.01])
        linear_extrude(0.05)
            difference() {
                circle(d = pocket_d);
                circle(d = pocket_d - 0.5);
            }
}

// Placeholder for the GitHub mark — outlined "gh" square. Replaced
// later with the real SVG once a layout variant is chosen.
module gh_mark(s = 7) {
    union() {
        difference() {
            offset(r = 0.4) square([s, s], center = true);
            offset(r = -0.4) square([s, s], center = true);
        }
        text("gh", size = s * 0.55, font = font,
             halign = "center", valign = "center");
    }
}

module v1() {
    // [gh] jmcpheron / pycon2026   — single line
    translate([-card_w/2 + 7, 0, card_t]) linear_extrude(emboss_h) gh_mark(7);
    translate([-card_w/2 + 13, 0, card_t]) linear_extrude(emboss_h)
        text("jmcpheron / pycon2026", size = 5, font = font,
             halign = "left", valign = "center");
}

module v2() {
    // [gh] jmcpheron  /  pycon2026 — two lines, no slash
    translate([-card_w/2 + 7,  6, card_t]) linear_extrude(emboss_h) gh_mark(6);
    translate([-card_w/2 + 12, 6, card_t]) linear_extrude(emboss_h)
        text("jmcpheron", size = 5, font = font,
             halign = "left", valign = "center");
    translate([-card_w/2 + 7, -6, card_t]) linear_extrude(emboss_h)
        text("pycon2026", size = 5, font = font,
             halign = "left", valign = "center");
}

module v3() {
    // jmcpheron \n / pycon2026 — slash as line prefix (file-pathy)
    translate([-card_w/2 + 7,  6, card_t]) linear_extrude(emboss_h)
        text("jmcpheron",   size = 5.5, font = font,
             halign = "left", valign = "center");
    translate([-card_w/2 + 7, -6, card_t]) linear_extrude(emboss_h)
        text("/ pycon2026", size = 5.5, font = font,
             halign = "left", valign = "center");
}

module v4() {
    // [gh] in top-left corner + stacked left-aligned text
    translate([-card_w/2 + 7,  card_h/2 - 7, card_t]) linear_extrude(emboss_h) gh_mark(6);
    translate([-card_w/2 + 7,  3, card_t]) linear_extrude(emboss_h)
        text("jmcpheron", size = 5, font = font,
             halign = "left", valign = "center");
    translate([-card_w/2 + 7, -6, card_t]) linear_extrude(emboss_h)
        text("pycon2026", size = 5, font = font,
             halign = "left", valign = "center");
}

module v5() {
    // [gh] corner + stacked right-aligned (text crowds the gear)
    translate([-card_w/2 + 7, card_h/2 - 7, card_t]) linear_extrude(emboss_h) gh_mark(6);
    translate([8,  3, card_t]) linear_extrude(emboss_h)
        text("jmcpheron", size = 5, font = font,
             halign = "right", valign = "center");
    translate([8, -6, card_t]) linear_extrude(emboss_h)
        text("pycon2026", size = 5, font = font,
             halign = "right", valign = "center");
}

module v6() {
    // Full repo path on a single line, smaller font
    translate([-card_w/2 + 7, 0, card_t]) linear_extrude(emboss_h)
        text("github.com/jmcpheron/pycon2026", size = 4, font = font,
             halign = "left", valign = "center");
}

color("#dde2e6") rounded_card();
color("#888")    pocket_marker();
color("#1a1a1a") {
    if      (variant == 1) v1();
    else if (variant == 2) v2();
    else if (variant == 3) v3();
    else if (variant == 4) v4();
    else if (variant == 5) v5();
    else if (variant == 6) v6();
}
