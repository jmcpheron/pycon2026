$fn = 24;

module base() {
    cube([100, 70, 3], center = true);
}

module walls() {
    // Front wall (short side, Y direction)
    cube([100, 2, 22], center = true);
    translate([0, 0, 10]) cube([100, 2, 2], center = true);
    
    // Back wall (short side, Y direction)
    translate([0, 35, 0]) cube([100, 2, 22], center = true);
    translate([0, 35, 10]) cube([100, 2, 2], center = true);
    
    // Left wall (long side, X direction)
    translate([-50, 0, 0]) cube([2, 70, 22], center = true);
    translate([-50, 0, 10]) cube([2, 70, 2], center = true);
    
    // Right wall (long side, X direction)
    translate([50, 0, 0]) cube([2, 70, 22], center = true);
    translate([50, 0, 10]) cube([2, 70, 2], center = true);
}

module decorative_ribs() {
    // Three ribs on left wall (long outer wall)
    for (i = [0 : 2]) {
        offset = -7 + i * 7;
        translate([-50, offset, 6]) cube([1.5, 1.5, 1], center = true);
    }
    
    // Three ribs on right wall (long outer wall)
    for (i = [0 : 2]) {
        offset = -7 + i * 7;
        translate([50, offset, 6]) cube([1.5, 1.5, 1], center = true);
    }
}

module standoff() {
    cylinder(h = 6, r = 3.5, center = false);
}

module tray_body() {
    union() {
        base();
        walls();
        decorative_ribs();
        
        // Four standoffs at Pi 5 mounting hole positions
        // Hole pattern: 58 mm × 49 mm centers, relative to Pi center
        translate([-29, -24.5, 3]) standoff();
        translate([29, -24.5, 3]) standoff();
        translate([-29, 24.5, 3]) standoff();
        translate([29, 24.5, 3]) standoff();
    }
}

module embossed_text() {
    translate([0, -36, 0.4]) 
        linear_extrude(height = 1.2, center = true) {
            text("PYCON 2026", size = 8, halign = "center", valign = "center");
        }
}

module standoff_holes() {
    union() {
        translate([-29, -24.5, -0.5]) cylinder(h = 7, r = 1.35, center = false);
        translate([29, -24.5, -0.5]) cylinder(h = 7, r = 1.35, center = false);
        translate([-29, 24.5, -0.5]) cylinder(h = 7, r = 1.35, center = false);
        translate([29, 24.5, -0.5]) cylinder(h = 7, r = 1.35, center = false);
    }
}

difference() {
    tray_body();
    standoff_holes();
    embossed_text();
}