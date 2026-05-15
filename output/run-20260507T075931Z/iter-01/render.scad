```
$fn = 24;

module base_plate() {
    difference() {
        // Main base plate: 95 × 65 × 4 mm
        cube([95, 65, 4], center = true);
        
        // Four M2.5 clearance holes (2.7 mm diameter) at mounting positions
        // Mounting hole pattern: 58 mm × 49 mm centers
        translate([29, 24.5, -1])
            cylinder(h = 6, r = 1.35);
        translate([29, -24.5, -1])
            cylinder(h = 6, r = 1.35);
        translate([-29, 24.5, -1])
            cylinder(h = 6, r = 1.35);
        translate([-29, -24.5, -1])
            cylinder(h = 6, r = 1.35);
        
        // Two wall-mount keyhole slots (8 mm wide × 14 mm long × 2 mm deep)
        // Near the short edges, recessed into the top surface
        // Top keyhole slot
        translate([-4, 30, 2])
            cube([8, 14, 2.1], center = false);
        // Bottom keyhole slot
        translate([-4, -44, 2])
            cube([8, 14, 2.1], center = false);
    }
}

module standoff() {
    cylinder(h = 6, r = 3);
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
```