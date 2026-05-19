This is a brilliant progression for your CAD model! In Part 3, the project moves from the intricate internal clockwork (gears and pins) into the massive, heavy structural elements: the vault door itself, the frame, and the complex hinge kinematics. 

Adam runs into a classic engineering hurdle in this video—door swing clearances—which is exactly the kind of thing CAD is designed to solve *before* you start cutting metal. You are going to have a great time setting this up in Onshape.

Here are the extracted technical specs, dimensions, and math from Part 3 to continue your assembly:

### 1. The Main Vault Door (The "Heavy Puck")
This is the massive structural block that houses the acrylic and gear assembly you modeled in Parts 1 and 2.
*   **Material:** Cast Iron (Adam initially calls it steel, but later confirms it's cast iron). 
*   **Weight Target:** 15 to 20 lbs in real life.
*   **Dimensions:** It is meant to fit a **6-inch diameter** hole.
*   **Internal Cavity:** Adam machines out the center of this puck to house the gear mechanism. The internal bore stops exactly **0.5 inches** from the front face (leaving a solid half-inch thick face on the front of the door).
*   **The Tapered Edge:** Real vault doors aren't perfect cylinders; they are tapered so they can "thunk" into the frame perfectly. Adam estimates the edge taper to be around **10 degrees**, though he notes it will actually be broken into three slightly different stepped angles. 
*   **Door Thickness Issue:** Adam discovers his door is too thick to swing open without hitting the frame. He has to thin the door down so that it pushes exactly **0.75 inches** back into its closure without binding on the hinge.

### 2. The Door Frame / Display Base
The door needs a massive wall to sit in and attach to.
*   **Material:** 1/2-inch thick 6061 Aluminum plate.
*   **Overall Size:** A square platform, roughly **10 to 12 inches** on each side.
*   **The Main Opening:** A **6-inch** hole is bored directly in the center for the door. 
*   **Clearance:** Adam is working with incredibly tight tolerances here. He mentions he has exactly **0.020 inches (20 thousandths)** of clearance around the door when it is seated in the frame. 

### 3. The Massive Hinge
Hanging a heavy door requires a complex, multi-pivoting hinge to handle torsional loads.
*   **Thrust Bearings:** To handle the lateral/torsional load without sagging, the hinge uses a stack of **3/8-inch outer-diameter bearings** running on a **1/8-inch center pin**. 
*   **Fasteners:** The hinge blocks are attached to the door and frame using **28 M2 screws**. *(Adam notes his "Plan B" is to use M6 threads if the tiny M2s fail under the weight, but in CAD, you can safely use the scaled-accurate M2s).*

### 4. The Hinge Mounting Coordinates (DRO Math)
Adam talks through the exact X/Y coordinates he uses on his mill's Digital Readout (DRO) to drill the mounting holes for the hinge blocks on the aluminum plate. Assuming **0,0** is the absolute center of the 6-inch vault door opening:
*   **X-Axis (Horizontal layout):** The inner column of holes is located at **0.245 inches** from the center line. The distance between the holes on the hinge block is **0.508 inches**. Therefore, the outer column of holes is at **0.753 inches** (0.245 + 0.508).
*   **Y-Axis (Vertical layout):** The total height span of the mounting block is 1.825 inches. Half of that is **0.9125 inches**. So, the top holes are **+0.9125 inches** from the center, and the bottom holes are **-0.9125 inches**.

### Tips for Modeling this in Onshape:

1. **Test the Kinematics (The Door Swing):** Adam had to physically cut metal to find out his door was too thick to swing open on its hinge. You don't! Once you model the door, frame, and hinge, use a **Revolute Mate** on the hinge pin. Grab the door with your mouse and drag it open. 
2. **Use Interference Detection:** While dragging the door open in the assembly, you can visually check if the back edge of the door clips the aluminum frame. Better yet, you can use Onshape's **Interference Detection** tool at different open angles to see exactly where (and by how much) the door binds.
3. **Use Variables for the Taper and Thickness:** In your Part Studio, create a Variable for the `Door_Thickness` and `Door_Taper_Angle`. Because you need the door to look meaty but still clear the frame when swinging, you can tweak these variables in the Part Studio and instantly watch the Assembly update until you achieve a perfectly swinging door with 0.020" of clearance!
4. **The Lapping Plate:** Adam spends a huge chunk of time using a lapping plate to remove 0.0005" (half a thousandth) of an inch of a "crown" to make the door perfectly flat. In Onshape, your parts are mathematically perfectly flat by default. Take a moment to appreciate the magic of CAD while you skip that hour of sanding!