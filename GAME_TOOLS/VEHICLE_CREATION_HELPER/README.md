# Vehicle Creation Helper
### What is this
- A "game tool", using a combination of text recognition and keys stimulation to automatically build your vehicle in game

### What does it do
- Having to repeat the same keys hundreds of times to install each part is tedious
- This script will make your character install every vehicle parts automatically
- Huge help to build a big vehicle
- **Supports every vehicle parts except the few that ask for a direction after installation (security camera, headlights,...).**

### How does it work (non technical explanation)?
- You first create you future vehicle in a json file, in an easy format for anyone not allergic to IT
- You get a reliable welding source and stockpile the needed components to install the vehicle parts
- Then you create a new one tile vehicle (the most top left part), open the vehicle menu, position your cursor on the first part to install and start the script

https://user-images.githubusercontent.com/71428793/205396697-3f1c69a4-99aa-445c-97f0-107e28fff973.mp4

- As you can see, the script will navigate through the vehicle tiles, and try to install the vehicle parts one by one
- Using text recognition, it can react to what happens in the game, eg:
	- 0:02 it detects that the foldable light frame is already installed, so it remembers it as "installed" and skips it
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
- First you have to create your vehicle in `vch_edit_me.json` (promise, it's dead simple)
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

- If that's enough explanations you can skip to the next part, otherwise click below ->
<details>

  <summary>Detailed explanation</summary>
	
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

</details>




#### Some set up tips
- Have an infinite welding source, or at least something that can last you for one day and the required tools eg:
	- a one tile vehicle welding rig on your left OR the integrated cutting torch CBM (very low power consumption)
	- a boomcrane installed on the one tile vehicle, to install wheels (or a bottlejack for anything but the biggest vehicles)
	- bolt turning 2, glare protection 2, hammering 2, screw driving 1, sewing 1, cutting 1, drilling 2 -> for reference `toolbox + pair of welding goggles` has everything you need
- You need to have the components for the vehicle parts to install in your character reach. Avoid having them on yourself, it will create an extra menu. Ideally, enough of them to last you for a day
- Make the area around you safe, wall yourself in if needed
- Start the script in the morning (in game), Turgid and Engorged
- Disable safe mode or at least make it pause the game only when hostiles are close. Maybe autosave too if it takes too long.
- Meeting all those requirement, you can install vehicle parts until dead tired, then eat, drink, sleep and repeat

#### Final set up and start the script
- Set up your options in the `options.json` file (most should be left default, check your keys, and the screen settings if you use several screens or a special resolution)
- Start a vehicle construction on your right, as usual (`*` -> Start a Vehicle Construction -> Enter -> Right direction)
- Examine the vehicle tile
- Move your cursor on the upper left tile of your vehicle, or the first part to install of the first row
	- most of the time, your first row will have some kind of ram, so if you use a rectangle shape vehicle, you just have to go up one tile
- Most of the time, this will be your second row, because the first will have some kind of ram
- Start the script, switch back to the game, and (hopefully) be amazed. To start the script:

##### If you're on windows (never tried it, but theoritically:)
 - install tesseract-ocr https://youtu.be/2kWvk4C1pMo
 - install python 3 https://youtu.be/C3bOxcILGu4
 - in a terminal type `python -m pip install pytesseract msgspec screeninfo` or `pip3 install pytesseract msgspec screeninfo`
 - if you have any difficulty don't hesitate to ask a LLM like chatgpt how to run the script https://chatgpt.com/



##### If you're on linux
- install tesseract-ocr `sudo apt-get install tesseract-ocr`
- install python 3 `sudo apt install python3`
- install python dependencies `pip3 install pytesseract msgspec screeninfo` install python dependencies
- `cd Python_Version; python3 vch.py`


#### Misc info
- All those vehicles have been fully built with the script, and are included in the VCH_Examples folder

![image](https://user-images.githubusercontent.com/71428793/205408545-80d87d19-fa21-4919-8ed0-b2496eac24c9.png)

#### Important notes
- **you can stop the script at any time by pressing Alt**
- when the script stops it will save the already installed parts in a `vch_parts_left_to_install.json` file, so it can starts at the next parts to install when you execute it again (`"D"` = Done, this part is installed)
- this means you can then tweak the `vch_parts_left_to_install.json` file if you know what you're doing

## Troubleshooting
- if the script skipped a part when it shouldn't, increase the script speed in options (it will slow the script down). Or just delete the `vch_parts_left_to_install.json` file, and the script will take more time at the beginning by verifying that all previous parts have been installed
- If script doesn't work when you start it, look at the last lines in the `debug.txt` file.

- *If it's still not clear, you can start the script, stop it after it sends a few keys, and look at the generated `vch_parts_left_to_install.json` file, you might get a clearer representation of what your vehicle will look like*


# Known bugs
- Do note use the `"` character, even as `\"` it will mess up vch_updated.json generation ---> eg: `32\" armored wheel` -> :(, `armored wheel` -> :) (bad example, the vehicle part name is "armored wheel" anyway, but you get the idea)
