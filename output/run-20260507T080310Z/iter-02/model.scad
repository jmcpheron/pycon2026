$fn = 24;

module base_plate() {
    cube([95, 65, 4], center=true);
}

module standoff(height) {
    cylinder(h=height, r=3, center=false);
}

module clearance_hole() {
    cylinder(h=10, r=1.35, center=false);
}

module keyhole_slot() {
    // Keyhole slot: 8mm wide x 14mm long
    // Composed of: rectangular slot (8x14mm) + hanging hole (6mm dia)
    union() {
        // Main slot opening: 8mm wide x 14mm long
        cube([8, 14, 6], center=true);
        
        // Hanging hole at top of slot: 6mm diameter cylinder
        translate([0, 7, 3]) 
            cylinder(h=6, r=3, center=true);
    }
}

// Calculate mounting hole positions (centered on 58mm x 49mm pattern)
hole_x_offset = 58 / 2;
hole_y_offset = 49 / 2;

difference() {
    union() {
        // Base plate positioned at z=0 to z=4
        translate([0, 0, 2]) base_plate();
        
        // Four standoffs extending from z=4 to z=10
        translate([-hole_x_offset, -hole_y_offset, 4]) 
            standoff(6);
        
        translate([hole_x_offset, -hole_y_offset, 4]) 
            standoff(6);
        
        translate([-hole_x_offset, hole_y_offset, 4]) 
            standoff(6);
        
        translate([hole_x_offset, hole_y_offset, 4]) 
            standoff(6);
    }
    
    // Four clearance holes (M2.5 = 2.7mm) drilled through standoffs and base
    // Positioned at z=4 to cleanly drill through the 6mm standoffs
    translate([-hole_x_offset, -hole_y_offset, 4]) 
        clearance_hole();
    
    translate([hole_x_offset, -hole_y_offset, 4]) 
        clearance_hole();
    
    translate([-hole_x_offset, hole_y_offset, 4]) 
        clearance_hole();
    
    translate([hole_x_offset, hole_y_offset, 4]) 
        clearance_hole();
    
    // Two keyhole slots on short edges (65mm side)
    // Left edge keyhole
    translate([-47.5, 0, 2]) 
        rotate([0, 0, 90])
        keyhole_slot();
    
    // Right edge keyhole
    translate([47.5, 0, 2]) 
        rotate([0, 0, 90])
        keyhole_slot();
}