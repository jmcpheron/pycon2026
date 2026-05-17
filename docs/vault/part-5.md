This is a fantastic pivot in the project! In Part 5, Adam returns to the vault after an 18-month hiatus. He steps away from the massive cast iron and acrylic components to tackle the part that intimidated him the most: the delicate, watchmaker-scale combination lock.

This part of the build transitions from heavy machining into micro-mechanics. You are going to be building a miniature combination lock that ultimately acts as the gatekeeper for the massive ring gear you modeled in Part 1. 

Here are the extracted technical specs, dimensions, and mechanical insights from Part 5 to update your Onshape model:

### 1. The Combination Lock Cage (The "Standalone Mechanism")
Adam decides to build the lock as a completely separate, self-contained mechanism before integrating it into the vault door.
*   **Overall Dimensions:** The maximum envelope of the lock cage is **0.75 inches long** by **0.5 inches wide**. 
*   **Material:** The lock body/escapement cage is built out of **0.025-inch (25 thousandths)** thick brass sheet (which Adam notes is just slightly over 0.5 mm thick).
*   **Construction:** It is a tiny box held together with miniature standoffs and tiny flathead screws.

### 2. The Combination Wheels (The Dials)
Inside that 0.75" x 0.5" cage sit the actual combination discs.
*   **Quantity:** **3 wheels** (meaning it's a standard 3-number combination lock).
*   **Wheel Diameter:** Adam mentions the discs are **0.450 inches (450 thousandths)** in diameter. 
*   **Features:** Every wheel requires three things modeled into it:
    1.  A **center spindle hole** (to rotate freely).
    2.  A **drive tab** (a small pin or raised bump that catches the adjacent wheel to spin it).
    3.  A **locking slot** (a notch cut into the perimeter of the wheel).

### 3. The Front Dial & "Adam Math" 
This is the knurled knob on the front of the safe that the user actually spins.
*   **Center Spindle:** The dial is attached to a **1/8-inch** brass rod, which passes through the door and drives the combination wheels.
*   **The Engraving Math Error:** Adam mounts the dial to his rotary table to engrave the combination numbers. He states he is going to make **36 divisions** and says, *"One for every degree."* 
    *   *CAD Tip:* $360 \text{ degrees} / 36 \text{ divisions} = \mathbf{10 \text{ degrees per division}}$. In your CAD model, your tick marks should be 10 degrees apart!
*   **Tick Mark Styling:** To make it look like a real safe dial, he makes a short tick mark for the 1s, a slightly longer tick mark every 5th division, and an even longer line every 10th division. 

### 4. The Unlocking Kinematics (The Bell Crank)
Adam finally explains how this tiny watchmaker lock interacts with the massive 120-tooth ring gear. 
*   **The Drop Arm:** When the user dials the correct 3-number combination, the locking slots on all three 0.450" wheels align perfectly. A small lever arm inside the 0.75" cage drops down ("thunks") into those aligned slots.
*   **The Bell Crank Coupling:** The dropping of that arm is connected to a bell crank linkage. Moving this linkage releases the giant brass ring gear, allowing the user to throw the lever that shoots the 12 pins outward.

### 5. Fixing the Pins (Again)
Adam realizes he has to pull all 12 locking pins out of the door yet again. Because they screw onto the racks, their rotational orientation can shift. To machine them correctly, he has to insert a tiny locking pin into each of the 12 posts to freeze their orientation permanently. 

### Tips for Modeling this in Onshape:

1. **Use a Sub-Assembly:** Take Adam's advice and build the 0.75" x 0.5" combination lock in its own, completely separate Assembly tab. Get the three 0.450" wheels, the cage, and the 1/8" spindle aligned perfectly before inserting this sub-assembly into your main Vault Door assembly. 
2. **Modeling the Combination Logic:** Real combination wheels use "drive pins" (tabs). When Wheel 3 does a full rotation, its tab hits the tab on Wheel 2 and starts dragging it along. To model this physically in CAD without breaking your computer's physics solver, model a small raised arc on the face of your wheels. You can use **Tangent Mates** or **Limit Constraints** on your Revolute Mates to simulate the dials catching and dragging each other!
3. **Circular Patterns for the Dial:** To recreate Adam's engraved dial, sketch three lines of varying lengths (short, medium, long) on the front face of your dial. Use the **Circular Pattern** tool in the sketch menu. Set the short lines to instance 36 times (every 10 degrees). 
4. **Appreciate the "Perfectly Centered" Hole:** Adam has to completely scrap his first front dial because his drill bit wandered and the center hole was off by a fraction of a millimeter, causing an eccentric wobble. In Onshape, when you sketch a 1/8" circle on the origin of your dial face, it is mathematically flawless. Take a second to enjoy the fact that your digital drill bit will never, ever wander! 
5. **The Bell Crank Linkage:** To connect the lock to the ring gear, you will get to play with spatial linkages. A bell crank is just an L-shaped pivot. You can use a **Pin-Slot Mate** or a **Revolute Mate** to link the dropping lever of your combo lock to the locking mechanism of your 120-tooth ring gear.