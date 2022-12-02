# Vehicle Creation Helper
### What is this
- A "game tool", using a combination of text recognition and keys stimulation to automatically build a vehicle in game

### Why does it do
- Having to repeat the same keys hundreds of times to install each part is tedious
- This script will make your character install every vehicle parts automatically
- Huge help to build big vehicle

### How does it work (non technical explanation)?


https://user-images.githubusercontent.com/71428793/205396697-3f1c69a4-99aa-445c-97f0-107e28fff973.mp4

- As you can see, the script will navigate through the vehicle tiles, and try to install the vehicle parts one by one
- Using text recognition, it can react to what happens in the game, eg:
	- 0:02 it detects that the foldable light frame is already installed, so it remembers it as "installed" and skip it
	- 0:03 the foldable light frame isn't installed yet, so it filters its name and select it to be installed
	- 0:19 it finds the "nearby)" (and "on person)") keyword in the pop up, so it presses enter to terminate the installation
	- 0:38 same idea as above, but notice that it works for welding tools and vehicle part components
	- 1:09 since the text isn't white, and should be here, it detects that the part can't be installed, so it mark it as uninstalled and will try to reinstall it when you restart the script
	- (not in the video) if, after filtering, the first proposed vehicle part isn't the right now, it will navigate to it by pressing the "go down" key and select the right one instead
	- (not in the video) any warning popup will make the script stop (eg if a hostile monster gets too close, or if you're "Dead Tired")

### How does it work (technical explanation)?
- The python script (vch.py) is heavily commented, go take a look if you're interested

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
![image](https://user-images.githubusercontent.com/71428793/205400378-eba4fa49-a24e-4488-9989-1a2b4087709f.png)
- Each vehicle part is defined between `{}`
- `part_name` is the name of the vehicle part to install
- `vmap` (vehicle part map) defines where the vehicle part will be installed
	- Each vehicle part row is defined between `[]`
	- Each tile in a row is separated by a `","`
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
- Start a vehicle construction on your right, as usual (`*` -> Start a Vehicle Construction -> Enter -> Right direction)
- Examine the vehicle tile
- Move your cursor on the upper left tile of your vehicle, or the first part to install of the first row
	- most of the time, your first row will have some kind of ram, so if you use a rectangle shape vehicle, you just have to go up one tile
- Most of the time, this will be your second row, because the first will have some kind of ram
- Start the script, switch back to the game, and (hopefully) be amazed. To start the script:
	- if you use the windows version, just double click the .exe
	- if you use the python version
		- install python 3
		- try to execute the script `python3 vch.py` (or `python`), it will most probably warn you about missing libraries
		- install all the missing libraries with `pip3 install <missing library name>` (or `pip`), until you can execute the script without error

#### Important notes
- **you can stop the script at any time by pressing Left Control**
- when the script stops it will save the already installed parts in a `vch_updated.json` file, so it can starts at the next part to install when you execute it again (`"D"` = Done, this part is installed)
- this means you can then tweak the `vch_updated.json` file if you installed some parts without the script, or just delete the `vch_updated.json` file, and the script will take more time at the beginning by verifying that all previous parts have been installed
- If script doesn't work when you start it, look at the last lines in the `debug.txt` file

#### Some set up tips
- Have an infinite welding source, or at least something that can last you for one day, eg:
	- a one tile vehicle welding rig on your left
	- the integrated cutting torch CBM (very low power consumption)
- You need to have the components for the vehicle parts to install on yourself or in your character reach. Ideally, enough of them to last you for a day
- Start the script in the morning (in game), Turgid and Engorged
- Avoid having monsters around you that could stop the script if they get too close
- Obviously, disable safe mode and such. Maybe autosave if it takes too long.
- Meeting all those requierment, you can install vehicle parts until dead tired, then eat, drink, sleep and repeat
