$fn = 24;

module tolerance_hole() {
    translate([0, 0, -1])
        cylinder(h = 22, r = 2);
}

module anvil() {
    // Base - wide, flat platform
    cube([55, 35, 4], center = true);
    
    // Main body block
    translate([0, 0, 9])
        cube([45, 30, 14], center = true);
    
    // Horn - tapered wedge approximation using scaled cube
    translate([28, 0, 12]) {
        difference() {
            cube([20, 28, 10], center = true);
            // Taper by removing corner material
            translate([10, 0, 0])
                cube([15, 32, 12], center = true);
        }
    }
    
    // Heel block on opposite side
    translate([-26, 0, 9])
        cube([12, 28, 14], center = true);
    
    // Tolerance hole through main body
    tolerance_hole();
}

module text_emboss() {
    // Simple recessed rectangles to approximate "PYCON"
    // P
    translate([-18, 16, 19.5]) {
        cube([3, 6, 0.8]);
        translate([0, -3, 0]) cube([6, 3, 0.8]);
        translate([0, 0, 0]) cube([6, 2, 0.8]);
    }
    
    // Y
    translate([-8, 16, 19.5]) {
        cube([3, 3, 0.8]);
        translate([3, 0, 0]) cube([3, 3, 0.8]);
        translate([1.5, -3, 0]) cube([3, 3, 0.8]);
    }
    
    // C
    translate([4, 16, 19.5]) {
        cube([6, 2, 0.8]);
        cube([2, 6, 0.8]);
        translate([4, 4, 0]) cube([2, 2, 0.8]);
    }
    
    // O
    translate([16, 16, 19.5]) {
        cube([6, 2, 0.8]);
        cube([2, 6, 0.8]);
        translate([4, 0, 0]) cube([2, 6, 0.8]);
        translate([0, 4, 0]) cube([6, 2, 0.8]);
    }
    
    // N
    translate([26, 16, 19.5]) {
        cube([2, 6, 0.8]);
        translate([4, 0, 0]) cube([2, 6, 0.8]);
        cube([6, 2, 0.8]);
    }
}

difference() {
    anvil();
    text_emboss();
}