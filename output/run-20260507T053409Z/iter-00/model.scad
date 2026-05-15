$fn = 60;

module hex_nut_m10() {
    // M10 hexagonal nut dimensions
    // Across flats (width): 15mm
    // Height: 8mm
    // Hole diameter: 10mm
    
    difference() {
        // Outer hexagon
        cylinder(h = 8, r = 15/2/cos(30), $fn = 6);
        
        // Inner hole
        cylinder(h = 8, r = 5, $fn = 60);
    }
}

hex_nut_m10();