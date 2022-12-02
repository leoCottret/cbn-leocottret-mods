# Vehicle Creation Helper
### What is this
- A "game tool", using a combination of text recognition and keys stimulation to automatically build a vehicle in game

### Why does it do
- Having to repeat the same keys hundreds of times to install each part is tedious
- This script will make your character install every vehicle parts automatically
- Huge help to build big vehicle

### How does it work (non technical explanation)?
- INSERT VIDEO HERE
- INSERT VIDEO EXPLANATIONS HERE

### How does it work (technical explanation)?
- INSERT TEC EXPLANATIONS HIDDEN BY DEFAULT

### How to use it?
#### Create your vehicle file
- First you have to create your vehicle in vch_original.json (promise, it's dead simple)
- There are several complete vehicle examples in the VCH_Examples
- Let's look at a concrete example with everything you'll need to know
```json
[
  {
    "part_name": "heavy duty frame",
    "vmap": [ 
      [ " ", " ", " " ],
      [ "X", "X", "X" ], 
      [ "X", "X", "X" ],
      [ "X", "X", "X" ]
    ]
  },
  {
    "part_name": "military composite ram",
    "vmap": [ 
      [ "X", "X", "X" ]
    ]
  },
  {
    "part_name": "heavy duty board",
    "vmap": [ 
      [ "2", " ", "X" ], 
      [ "4", "X", "X" ]
    ]
  },
  {
    "part_name": "heavy duty roof",
    "vmap": [
      [ "2:4", "X", "X" ]
    ]
  },
  {
    "part_name": "seat",
    "vmap": [
      [ " ", "3", " " ]
    ]
  }
]
```
- The final result will look like this
INSERT PICTURE
- each vehicle part is defined between `{}`
- `part_name` is the name of the vehicle part to install
- `vmap` (vehicle part map) defines where the vehicle part will be installed
	- each vehicle part row is defined between `[]`
	- each tile in a row is separated by a `","`
	- `" "` -> nothing will be installed
	- `"X"` -> the vehicle part will be installed
	- `"number"` -> the script will install the vehicle parts at this row number
	- `"number1:number2"` -> the script will install the vehicle parts at number1 row, and repeat for each row number until it reaches row number2
	- `"number"` or `"number1:number2"` must be defined in the first encountered vehicle row tile, starting from the left
- If that's enough explanations you can skip to the next part, otherwise ->
(TODO hide it by default)
- heavy duty frame
	- we're building a 3x4 vehicle including the ram, so we skip the first row, and then build a 3x3 square of frames
- military composite ram
	- since it's installed at the first row, we can just add a row of "X"
- heavy duty board
	- row 2 are define like that so we can add a reinforced windshield in the middle
	- row 3 has nothing because we'll add doors on each side, and the middle will be where the player will drive
	- row 4 is the back of the vehicle
- heavy duty roof
	- has the exact same vmap content as heavy duty frame, but in a compressed format. Very handy for big vehicles
- seat
	- we add the driver's seat, in the only "interior" tile of the vehicle
- And for those that never use json, notice that every last vehicle part and vmap row don't have a comma at the end

#### Final set up and start the script
- start a vehicle construction on your right, as usual (`*` -> Start a Vehicle Construction -> Enter -> Right direction)
- examine the vehicle tile
- move your cursor on the upper left tile of your vehicle, or the first part to install of the first row
	- most of the time, your first row will have some kind of ram, so if you use a rectangle shape vehicle, you just have to go up one tile
- most of the time, this will be your second row, because the first will have some kind of ram
- start the script, switch back to the game, and (hopefully) be amazed

#### Important notes
- **you can stop the script at any time by pressing Left Control**
- when the script stops it will save the already installed parts in a `vch_updated.json` file, so it can starts at the next part to install when you execute it again (`"D"` = Done, this part is installed)
- this means you can then tweak the `vch_updated.json` file if you installed some parts without the script, or just delete the `vch_updated.json` file, and the script will take more time at the beginning by verifying that all previous parts have been installed
- If script doesn't work when you start it, look at the last lines in the debug.txt file

#### Some set up tips
- have an infinite welding source, or at least something that can last you for one day, eg:
	- a one tile vehicle welding rig on your left
	- the integrated cutting torch CBM (very low power consumption)
- you need to have the components for the vehicle parts to install on yourself or in your character reach. Ideally, enough of them to last you for a day
- start the script in the morning (in game), Turgid and Engorged
