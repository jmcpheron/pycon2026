$fn = 24;

module standoff() {
    cylinder(h = 6, r = 3);
}

module keyhole_slot() {
    union() {
        // Circular top of keyhole
        translate([0, 0, -0.5])
            cylinder(h = 5, r = 4);
        // Rectangular stem
        translate([-4, -7, -0.5])
            cube([8, 7, 5]);
    }
}

module base_plate() {
    difference() {
        // Main base plate: 95 × 65 × 4 mm
        cube([95, 65, 4], center = true);
        
        // Four M2.5 clearance holes (2.7 mm diameter) at mounting positions
        // Mounting hole pattern: 58 mm × 49 mm centers, relative to board center
        // Pi 5 board center at (85/2, 56/2) = (42.5, 28)
        // Hole positions offset from board center
        translate([29, 24.5, -1])
            cylinder(h = 6, r = 1.35);
        translate([29, -24.5, -1])
            cylinder(h = 6, r = 1.35);
        translate([-29, 24.5, -1])
            cylinder(h = 6, r = 1.35);
        translate([-29, -24.5, -1])
            cylinder(h = 6, r = 1.35);
        
        // Two wall-mount keyhole slots (8 mm wide × 14 mm long)
        // Near the short edges (top and bottom when mounted)
        translate([0, 30.5, 3.5])
            rotate([90, 0, 0])
            keyhole_slot();
        translate([0, -30.5, 3.5])
            rotate([90, 0, 0])
            keyhole_slot();
    }
}

module standoffs_positive() {
    // Four standoffs at mounting hole positions
    translate([29, 24.5, 2])
        standoff();
    translate([29, -24.5, 2])
        standoff();
    translate([-29, 24.5, 2])
        standoff();
    translate([-29, -24.5, 2])
        standoff();
}

// Final assembly
union() {
    base_plate();
    standoffs_positive();
}