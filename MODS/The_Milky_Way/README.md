**_TLDR: "Add Prolactin Amplification to the Cattle mutation branch, allowing you to milk NPCs once a day with a bucket in your inventory"_**

- How do I get the Prolactin Amplification mutation?
  - (worst solution) Take (normal) mutagen, or get irradiated (or any kind of way to get random mutations), and pray 
  - (best solution) Find or make cattle mutagen, then take them until you get it 
  - **Remember that you can control NPCs by talking to them with `C`**. This allows you to easily make them take the mutagens
- How do I milk my NPCs?
  - Have an empty bucket *in your inventory*
  - Be sure that they have the Prolactin Amplification mutation
  - (optional but better) Have a big container *in your inventory* (can be wielded), eg: a 60L metal tank. Make sure it's empty, or that the milk in it isn't old
  - Go next to your NPC, press `e` then select your NPC (arrow keys or numpad)
  - The container with the highest space available will be filled with 20 milk. If a container has milk in it, it will be prioritized.
- Can I... milk myself?
  - Yes (kind of), but you need a NPC. Control the NPC, milk yourself, then control yourself
- Sometimes I see extra messages after I milk a NPC, what are those?
 - Each time you milk a NPC, you get a random chance to get those messages
 - The chance depends on: your speaking skill, your dexterity, if you have the Prolactin Amplification mutation yourself, and a "d100 dice"
 - Critical Failure: angers The Cow-God, bad moral for this NPC
 - Critical Success: increase your relation with this NPC, even better moral for this NPC
 - PS: milking NPCs will increase your speaking skill, simply because you're talking during the deed
#### Known bugs and their solution
- 1) If you have a container with old milk, the new milk will stack on top of the old milk in it, and you will see "2 items" instead of the amount of milk
  - Solution: don't do that, use an empty container or with milk that is somewhat recent (a few hours). So milking a few NPC in a row is completely safe
  - PS: you can empty the older milk with `U` + select container + `g` + direction (they didn't mix in the container, it's high tech)
- 2) If you milk a NPC (milking a human appears), but don't get milk
  - Solution: increase the number next to `MILK_ACTIVITY_MARGIN = `. In theory it should never happen, but there might be some strange interactions with other mods that causes this, so I created this system just in case
