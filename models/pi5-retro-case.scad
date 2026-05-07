$fn = 24;

module base() {
    cube([100, 70, 3], center = true);
}

module walls() {
    // Front wall (short side, Y direction) - single solid wall
    translate([0, -35, 11]) cube([100, 2, 22], center = true);
    
    // Back wall (short side, Y direction) - single solid wall
    translate([0, 35, 11]) cube([100, 2, 22], center = true);
    
    // Left wall (long side, X direction) - single solid wall
    translate([-50, 0, 11]) cube([2, 70, 22], center = true);
    
    // Right wall (long side, X direction) - single solid wall
    translate([50, 0, 11]) cube([2, 70, 22], center = true);
}

module decorative_ribs() {
    // Three ribs on left wall (long outer wall)
    // Ribs: 1 mm tall × 1.5 mm deep, raised on outer surface
    for (i = [0 : 2]) {
        offset = -21 + i * 21;
        // Positioned at outer wall surface, protruding outward
        translate([-51.75, offset, 11]) cube([1.5, 1.5, 1], center = true);
    }
    
    // Three ribs on right wall (long outer wall)
    for (i = [0 : 2]) {
        offset = -21 + i * 21;
        translate([51.75, offset, 11]) cube([1.5, 1.5, 1], center = true);
    }
}

module standoff() {
    cylinder(h = 6, r = 3.5, center = false, $fn = 24);
}

module tray_body() {
    union() {
        base();
        walls();
        decorative_ribs();
        
        // Four standoffs at Pi 5 mounting hole positions
        // Hole pattern: 58 mm × 49 mm centers, relative to Pi center at origin
        translate([-29, -24.5, 3]) standoff();
        translate([29, -24.5, 3]) standoff();
        translate([-29, 24.5, 3]) standoff();
        translate([29, 24.5, 3]) standoff();
    }
}

module embossed_text() {
    // Text positioned on front wall, intersecting wall material
    // Front wall is at Y = -35, Z from 0 to 22
    // Position text at Z = 11 (middle of wall) to ensure intersection
    translate([0, -36.2, 11]) 
        linear_extrude(height = 1.2, center = true) {
            text("PYCON 2026", size = 7, halign = "center", valign = "center");
        }
}

module standoff_holes() {
    union() {
        translate([-29, -24.5, -0.5]) cylinder(h = 7, r = 1.35, center = false, $fn = 24);
        translate([29, -24.5, -0.5]) cylinder(h = 7, r = 1.35, center = false, $fn = 24);
        translate([-29, 24.5, -0.5]) cylinder(h = 7, r = 1.35, center = false, $fn = 24);
        translate([29, 24.5, -0.5]) cylinder(h = 7, r = 1.35, center = false, $fn = 24);
    }
}

difference() {
    tray_body();
    standoff_holes();
    embossed_text();
}