$fn = 60;

module anvil_base() {
    cube([50, 30, 5]);
}

module anvil_body() {
    translate([10, 5, 5]) {
        cube([30, 20, 20]);
    }
}

module anvil_horn() {
    translate([40, 15, 5]) {
        rotate([0, -45, 0]) {
            union() {
                cylinder(h = 20, r1 = 10, r2 = 2, $fn = 60);
                translate([0, 0, 10]) {
                    cube([5, 20, 10]);
                }
            }
        }
    }
}

module anvil_heel() {
    translate([0, 5, 5]) {
        cube([10, 20, 15]);
    }
}

module anvil_text() {
    translate([40, -0.1, 15]) { // Adjusted Y for embossing, Z for vertical centering
        rotate([90, 0, 90]) {
            linear_extrude(height = 2) {
                text("PYCON 2026", size = 8, font = "Sans:style=Bold");
            }
        }
    }
}

union() {
    anvil_base();
    anvil_body();
    anvil_horn();
    anvil_heel();
    difference() {
        anvil_body();
        anvil_text();
    }
}