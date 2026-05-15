$fn = 24;

module anvil() {
    difference() {
        union() {
            // Base plate
            cube([50, 30, 5]);
            
            // Central body block
            translate([10, 0, 5])
                cube([30, 30, 20]);
            
            // Tapered horn (simplified via cylinder)
            translate([40, 15, 15])
                rotate([0, 90, 0])
                cylinder(h=20, r1=8, r2=1);
            
            // Heel block
            translate([0, 0, 5])
                cube([10, 30, 12]);
        }

        // Embossed Text
        translate([12, -0.1, 15])
            rotate([90, 0, 0])
            linear_extrude(height = 1)
                text("PYCON 2026", size = 5, halign = "left");
    }
}

anvil();