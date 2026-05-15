$fn = 24;

module base_plate() {
    cube([95, 65, 4], center=true);
}

module standoff(height) {
    cylinder(h=height, r=3, center=false);
}

module clearance_hole() {
    cylinder(h=15, r=1.35, center=false);
}

module keyhole_slot() {
    // Keyhole slot: 8mm wide x 14mm long, functional mounting slot
    cube([8, 14, 5], center=true);
}

// Calculate mounting hole positions (centered on 58mm x 49mm pattern)
hole_x_offset = 58 / 2;
hole_y_offset = 49 / 2;

difference() {
    union() {
        // Base plate centered at z=2
        translate([0, 0, 2]) base_plate();
        
        // Four standoffs - union them into the base before drilling
        translate([-hole_x_offset, -hole_y_offset, 0]) 
            standoff(6);
        
        translate([hole_x_offset, -hole_y_offset, 0]) 
            standoff(6);
        
        translate([-hole_x_offset, hole_y_offset, 0]) 
            standoff(6);
        
        translate([hole_x_offset, hole_y_offset, 0]) 
            standoff(6);
    }
    
    // Four clearance holes (M2.5 = 2.7mm) - drilled through standoffs and base
    // Front-left
    translate([-hole_x_offset, -hole_y_offset, 0]) 
        clearance_hole();
    
    // Front-right
    translate([hole_x_offset, -hole_y_offset, 0]) 
        clearance_hole();
    
    // Back-left
    translate([-hole_x_offset, hole_y_offset, 0]) 
        clearance_hole();
    
    // Back-right
    translate([hole_x_offset, hole_y_offset, 0]) 
        clearance_hole();
    
    // Two keyhole slots on short edges (65mm side)
    // Left edge keyhole
    translate([-47.5, 0, 2]) 
        keyhole_slot();
    
    // Right edge keyhole
    translate([47.5, 0, 2]) 
        keyhole_slot();
}