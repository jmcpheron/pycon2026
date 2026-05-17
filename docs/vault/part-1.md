This sounds like an incredibly fun and challenging project for Onshape! Modeling mechanical assemblies with meshing gears is a great way to level up your CAD skills. 

To save you from having to scrub back and forth through the video, I have extracted all the technical specifications, gear ratios, math, and dimensions Adam discusses. 

Here is the technical breakdown you need to model this in Onshape:

### 1. The Core Gear Math (The Most Important Part)
For gears to mesh properly in CAD (and in real life), they must share the same **Module** (often just called "Mod").
*   **Gear Module:** 0.5 mm (This is the critical number you will need when generating your gears in Onshape).
*   **Real-World Vault Door Math (Base 12):** Adam notes that real vault doors have 24 spur gears (with 24 teeth each) surrounding a ring gear with 288 teeth. 
*   **Adam’s 1/12th Scale Version:** To keep the project manageable at a miniature scale, Adam cuts the math in half.
    *   **Number of Spur Gears (and locking pins):** 12
    *   **Spur Gear Teeth:** 24 teeth per gear.
    *   **Ring Gear Teeth:** 120 teeth.

### 2. The Ring Gear Specs
This is the piece Adam spends the video machining out of a solid cylinder.
*   **Material:** 416 Stainless Steel (just an FYI, though not strictly needed for CAD).
*   **Outer Diameter (OD):** 2.401 inches (Adam notes it is basically exactly 2.4 inches).
*   **Number of Teeth:** 120
*   **Depth of Gear Cut:** 0.044 inches (44 thousandths). When drawing your gear profile, the depth from the outer diameter to the root of the tooth is 0.044".

### 3. The Layout and Spacing (The Base Plate)
Toward the end of the video, Adam shows a black rectangular test plate where he mounts the spur gears to test the meshing with the ring gear.
*   **Hole Spacing:** Adam uses a dividing plate on his mill to drill the mounting holes for the spur gears. He mentions the plate is divided into **15-degree increments**. 
*   Because $360 / 15 = 24$, his test plate actually has 24 holes drilled in a circle. However, because he is only building a 12-pin door, he places the 12 spur gears in every *other* hole.
*   **CAD Layout:** When you sketch the bolt-circle diameter for your spur gear axles, you will want an array of 12 points spaced exactly **30 degrees apart**.

### 4. The Locking Pins
Though he hasn't built them yet in this video, Adam shows his technical drawing and explains how the pins work.
*   **Pin Diameter:** 12 mm.
*   **Mechanism:** The bottom of each 12mm pin will have a straight gear "rack" machined into it. 
*   **Action:** Turning the 120-tooth central ring gear will turn all twelve 24-tooth spur gears simultaneously. Those spur gears will engage the racks on the bottoms of the pins, driving all 12 pins outward into the vault wall at the same time.

### Tips for Modeling this in Onshape:
1.  **Use the FeatureScript "Spur Gear" Generator:** Do not try to draw the involute gear teeth by hand! Go to the "Add custom features" tool in Onshape and search for the standard "Spur Gear" creator. 
2.  **Generate the Spur Gear:** Input a Module of **0.5 mm** and **24 teeth**.
3.  **Generate the Ring Gear:** You can use the same gear generator. Set it to **Internal Gear** (or Ring Gear, depending on the specific script version), Module **0.5 mm**, and **120 teeth**. Ensure the Outer Diameter matches Adam's 2.4-inch dimension. 
4.  **Mate Connectors:** When you move to the Assembly tab, you can use a "Revolute Mate" to fix the gears to the base plate, and then use the "Gear Relation" tool to make them actually spin together. Onshape will calculate the ratio automatically based on the teeth count (120:24, which is a 5:1 ratio).

Have fun with the build! Getting all 13 gears to spin together smoothly in the Onshape assembly animation will be incredibly satisfying.