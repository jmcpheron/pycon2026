$fn = 24;

module anvil() {
    // Base
    cube([50, 30, 8], center = true);
    
    // Central body block
    translate([0, 0, 12])
        cube([40, 25, 16], center = true);
    
    // Horn (tapered cone from one side)
    translate([22, 0, 12]) {
        cylinder(h = 16, r1 = 8, r2 = 3, center = true);
    }
    
    // Heel block on opposite side
    translate([-18, 0, 12])
        cube([12, 20, 14], center = true);
}

module text_emboss() {
    // "PYCON 2026" embossed on the side
    translate([-15, -15, 20]) {
        linear_extrude(height = 1.5) {
            text("PYCON 2026", size = 6, halign = "center", valign = "center", font = "Arial:style=Bold");
        }
    }
}

module anvil_with_text() {
    difference() {
        anvil();
        text_emboss();
    }
}

anvil_with_text();