This is turning into a fantastic CAD exercise! In Part 4, Adam dives deep into the weeds of mass production, tolerances, and the compounding errors of concentricity. 

This video is a prime example of where CAD feels like "magic" compared to the real world. Adam spends the entire video fighting to make 12 identical, perfectly concentric parts—a task that requires a single mouse click in Onshape! 

Here are the extracted technical specs, dimensions, and mechanical engineering takeaways from Part 4 to update your model:

### 1. The Locking Pins (A Dimension Discrepancy!)
In Part 2, Adam noted his technical drawing called for 12mm locking pins. However, in this video, he picks up one of the pins and states:
*   **Revised Pin Diameter:** **10 mm** (He mentions it has a threaded hole in one side, likely an M10 or M6 depending on the internal tap). 
*   *CAD Tip:* This is why we use parametric modeling! If you hard-coded 12mm in your model, change it to a variable (e.g., `#Pin_Diameter = 10mm`). This allows you to update the pin size, and the corresponding holes in the acrylic hub and cast iron door will automatically scale to match.

### 2. The Racks (The Square Stock)
Adam is refining the 12 racks that screw into the bases of the locking pins.
*   **Stock Size:** **8mm square** material.
*   **The "Zero Point" Alignment:** Adam explains that for the 12 pins to lock and unlock simultaneously, the gear teeth on all 12 racks must start at the exact same distance from the shoulder. If they don't, the pins will protrude at different lengths. He uses a mill stop to shave the ends of all the blanks so they are perfectly uniform.
*   **Clearance Cut:** Adam notes that the back of the rack has a "curved relief" cut into it. Because the racks sit so tightly around the central ring gear, the backs of the square racks have to be slightly scooped out to avoid rubbing against it.

### 3. The Concentricity Error (The 12.5 Thou Problem)
This is the core problem of the video. Adam initially cut the threaded studs on the racks by hand using a die. 
*   **The Error:** Because human hands aren't perfectly straight, the studs were cut off-center by **0.0125 inches (12.5 thousandths)**. 
*   **The Result:** When screwed into the pins, the racks sat slightly sideways, causing the pins to rub and bind against the walls of the vault door.
*   **The Fix:** Adam uses an **8mm square 5C Collet** in his lathe. He uses a depth stop so every rack sticks out the exact same amount. He then locks the lathe spindle and uses a die held in the tailstock to cut the threads perfectly parallel and concentric to the center of the 8mm square stock.
*   **Quantity:** He is making **14 racks** even though he only needs 12. As he says, "Always make more than you need" because "assumptions kill" and mistakes happen. 

### Tips for Modeling this in Onshape:

1. **Rejoice in Digital Perfection:** In Onshape, when you sketch a circle exactly in the center of an 8mm square and extrude it, it is mathematically, flawlessly concentric. Take a moment to appreciate that you don't have to build a custom lathe setup to avoid a 0.0125" offset error!
2. **Boolean Subtract for the Rack Relief:** To make that "curved relief" on the back of your 8mm racks, don't try to guess the curve! Place your racks in the assembly around your ring gear. Go back to your Part Studio, and use a **Boolean Feature** set to "Subtract". Use a cylinder slightly larger than your ring gear as the "Tool". Onshape will automatically carve the perfect clearance curve into the back of your square rack.
3. **Setting Slider Mate Limits:** Because you are dealing with real-world dimensions now, you should add limits to your pins. Double-click the **Slider Mate** you applied to your pins in the assembly. Check the "Limits" box. You can measure the total length of the toothed section of your rack and input that as the maximum travel distance. Now, when you drag the vault door mechanism open and closed with your mouse, the pins will hit a hard stop when they run out of gear teeth, just like real life.
4. **Sub-Assemblies:** Adam is essentially building 12 identical "Sub-Assemblies" (1 Pin + 1 Rack + 1 Spur gear). If your main assembly is getting cluttered, you can create a new Assembly tab, mate just *one* pin, rack, and spur gear together, and then insert that entire Sub-Assembly into your main Vault Door assembly 12 times. This keeps the mating tree very clean!