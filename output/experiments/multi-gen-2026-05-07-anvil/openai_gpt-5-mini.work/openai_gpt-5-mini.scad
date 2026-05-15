$fn = 60;

module base_plate(bx,by,th) {
    translate([-bx/2, -by/2, 0])
        cube([bx, by, th]);
}

module body_block(w,d,h,base_th) {
    translate([-w/2, -d/2, base_th])
        cube([w,d,h]);
}

module horn(len, r1, r2, body_d, body_h, base_th) {
    // cone along +Y, centered in X, vertically centered on body
    translate([0, body_d/2, base_th + body_h/2])
        rotate([90,0,0])
            cylinder(h=len, r1=r1, r2=r2);
}

module heel(w, len, h, body_d, base_th) {
    // short block on -Y side, centered in X
    translate([-w/2, -body_d/2 - len, base_th])
        cube([w, len, h]);
}

module embossed_text(str, size, depth, body_w, body_d, body_h, base_th) {
    // Create extruded text, rotate so it extrudes into -X, place on +X side of body
    text_obj = linear_extrude(height=depth)
                rotate([0,0,-90])
                    text(str, size=size, halign="center", valign="center");
    // rotate to extrude into -X, position so front face sits slightly outside body face
    translate([body_w/2 + 0.01, 0, base_th + body_h/2])
        rotate([0,-90,0])
            children_safe(text_obj);
}

// Helper to include generated geometry (OpenSCAD doesn't allow assigning child to variable in older versions)
// Implement children_safe as wrapper that just places the geometry passed by direct call
module children_safe(obj) {
    // obj is a group produced by linear_extrude(...); calling it here emits it
    obj;
}

//// Parameters
body_w = 40;
body_d = 18;
body_h = 18;
base_th = 4;
horn_len = 22;
heel_len = 10;
horn_r1 = 6;
horn_r2 = 1;
heel_w = 18;
heel_h = 12;
text_size = 8;
text_depth = 2;

total_len = body_d + horn_len + heel_len;
base_x = body_w + 10;
base_y = total_len + 8;

module anvil() {
    difference() {
        union() {
            base_plate(base_x, base_y, base_th);
            body_block(body_w, body_d, body_h, base_th);
            horn(horn_len, horn_r1, horn_r2, body_d, body_h, base_th);
            heel(heel_w, heel_len, heel_h, body_d, base_th);
        }
        // subtract text: placed and rotated to cut into the right side (+X) of the body
        // Using a direct inline call to build the extruded text and subtract it
        translate([body_w/2 + 0.01, 0, base_th + body_h/2])
            rotate([0,-90,0])
                linear_extrude(height=text_depth)
                    rotate([0,0,-90])
                        translate([0,0,0])
                            text("PYCON 2026", size=text_size, halign="center", valign="center");
    }
}

anvil();