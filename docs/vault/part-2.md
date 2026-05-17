This is a perfect continuation for your Onshape project! In Part 2, Adam moves past the basic rotating gears and tackles the actual linear locking mechanism (the racks and pins) as well as the main vault door body. 

He also drops some incredible mechanical engineering wisdom regarding timing, alignment, and compounding errors, which translates perfectly into CAD constraints.

Here are the extracted technical specs, dimensions, and math from Part 2 to continue your Onshape model:

### 1. The Locking Pins & Racks (The Linear Motion)
The actual locking mechanism uses a rack-and-pinion setup driven by the spur gears.
*   **The Racks:**
    *   **Stock Size:** 8mm x 8mm square gear rack.
    *   **Module:** Mod 0.5 (matching the ring and spur gears).
    *   **Modifications:** One end is turned down to a 6mm shaft and threaded (M6). The back side of the rack gets a groove milled into it (using a ball end mill) to ensure it clears the rotating gears. 
*   **The Locking Pins:**
    *   **Diameter:** 12mm.
    *   **Length:** 30mm (Adam's drawing notes "M12 x 30").
    *   **Mounting:** The base of the pin has an M6 threaded hole. The threaded gear rack screws directly into the base of this pin. 

### 2. The Main Vault Door Body (The Hub)
Adam machines the main structural body of the door out of clear acrylic so the mechanism remains visible.
*   **Overall Dimensions:** 6-inch outer diameter, cut from 1.25-inch thick stock. *(Note: Adam mentions specifically using "Cast" acrylic rather than "Extruded" because extruded melts on the lathe—good physical shop trivia, even if it doesn't change your CAD model!)*
*   **Spur Gear Layout (BCD):** Adam notes he laid the spur gears out on a **72mm diameter circle**. 
*   **Ring Gear Mounting Hub (Inner Diameter):** He cuts a "slip cut" boss in the center of the acrylic for the ring gear to sit on. He notes this dimension is **2.003 inches** ("Two inches plus about 3 thousandths"). So, the Inner Diameter (ID) of your ring gear should be exactly 2.003".
*   **Radial Pin Holes:** The perimeter of the acrylic body gets twelve 12mm holes drilled radially inward for the locking dowel pins to slide back and forth through.

### 3. Fasteners and Clearances
*   **Spur Gear Axles:** Adam uses shoulder bolts as the axles for the 12 spur gears. He notes that the smooth shoulder of the bolt is exactly **0.1 mm smaller** in diameter than the center hole of the spur gears, providing a perfect slip-fit so they can spin freely without wobbling. 

### 4. The "Timing" Math (Adam's Wisdom Bomb)
Adam explains exactly *why* the gear counts matter so much for alignment:
*   **The Divisor Math:** You have 12 pins. For the mechanism to work, the ring gear's tooth count (120) *must* be perfectly divisible by 12. 120 / 12 = 10. This means there are exactly 10 teeth between the center point of each spur gear.
*   **The Rack Alignment Error:** Adam points out a massive trap he almost fell into. When threading the 8mm racks, the thread must start at the *exact same point relative to the gear teeth* on all 12 racks. If it doesn't, the 12mm pins will screw on to slightly different depths, meaning the locking pins will stick out of the door at uneven lengths. He had to build a custom fixture just to machine the racks identically to within a tenth of a millimeter.

### Tips for Modeling this in Onshape:

1. **Modeling the Pins and Racks:** Model the 12mm pin and the 8x8mm rack as a single "Part" in your Part Studio to save yourself the hassle of mating M6 threads together in the assembly. You can visually add the threads later if you want the detail, but structurally, treat them as one solid object.
2. **Rack and Pinion Relation:** In your Assembly tab, use a **Slider Mate** to allow the pin to slide radially in and out of the acrylic body. Then, use the **Rack and Pinion Relation** tool. You will select the Revolute Mate of the spur gear and the Slider Mate of the pin. Onshape will automatically sync the rotation of the gear to the linear sliding of the pin!
3. **The Beauty of CAD Arrays:** To avoid Adam's "Rack Alignment Error," you only need to model *one* perfect pin, rack, and spur gear. Once you have that single mechanism perfectly timed and mated in your assembly, you can use a **Circular Assembly Pattern** to instance it 12 times around the 360-degree hub. Onshape will mathematically guarantee that all 12 pins are identically "timed."

Adding the sliding radial pins tied to the spinning gears is going to make your assembly animation look absolutely incredible. Have fun!