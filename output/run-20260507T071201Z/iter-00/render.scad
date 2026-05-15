$fn = 60;

module chamfer_edge(size) {
    chamfer = size * 0.15;
    children();
}

module anvil_base() {
    translate([0, 0, 0])
        cube([65, 50, 8], center=true);
}

module anvil_body() {
    translate([0, 0, 16])
        cube([55, 42, 24], center=true);
}

module anvil_horn() {
    hull() {
        translate([27.5, 0, 16])
            cube([8, 30, 20], center=true);
        translate([48, 0, 20])
            cylinder(h=16, r=4, center=true);
    }
}

module anvil_heel() {
    translate([-27.5, 0, 16])
        cube([8, 30, 20], center=true);
}

module hardy_hole() {
    translate([0, 0, 28])
        cube([6, 6, 5], center=true);
}

module tolerance_hole() {
    translate([15, 0, 16])
        cylinder(h=30, r=2.5, center=true);
}

module rectangular_slot() {
    translate([-8, 0, 16])
        cube([3, 10, 30], center=true);
}

module horn_tip_round() {
    translate([48, 0, 20])
        sphere(r=4);
}

module emboss_text(text, x_pos, y_pos, depth) {
    translate([x_pos, y_pos, 0])
        linear_extrude(height=depth)
            text(text, size=8, halign="center", valign="center", font="Arial:Bold");
}

module rounded_anvil() {
    minkowski() {
        difference() {
            union() {
                anvil_base();
                anvil_body();
                anvil_horn();
                anvil_heel();
                horn_tip_round();
            }
            hardy_hole();
            tolerance_hole();
            rectangular_slot();
        }
        sphere(r=1.2);
    }
}

module final_anvil() {
    difference() {
        rounded_anvil();
        emboss_text("PYCON", -15, 21, 0.8);
        emboss_text("2026", 15, 21, 0.8);
    }
}

final_anvil();