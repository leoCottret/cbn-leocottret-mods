First, big thanks to @scarf that helped me build the start of the script, and was even kind enough to give me a Proof of Concept of it

### What is this for?
- It's a script to generate XL versions of normal armors, based on custom parameters.
- Probably for technical people or highly motivated ones.
- Otherwise, go get the ready to use version here (when it's ready) *TODO put link*

### Why should I care?
- The amount of XL versions in vanilla is tiny (~16, compare that to the number of armors that a huge mutant can't wear)
- With this script, you can create your own version of missing XL armors for vanilla ones, and even your mods!
- So it's especially interesting for modders that want to create XL versions of their armors (although I can do it too, you might want to balance them yourself)

### How does it work?
- First, you set the different options, including how much you want each xl armor to change from its normal version one
	- you can increase the encumbrance, volume, weight and storage by 20% for example (those are the default values, and what is used in the ready to use version). You can set individual modifiers for each values.
- Basically, it checks through your game folder and in all of your current mod files if an armor has an xl version of it
- If that's not the case, it creates one
- Then, if there's a recipe for it (recipe and uncraft), it adds an XL version of it
- If it doesn't, and I especially like this "hack", it just creates a recipe to convert a normal armor to the xl one, and the opposit
- That's how this script can cover ALL armors, without adding non craftable versions to spawn locations (which would have been a pain, and maybe unrealistic in some cases)
- It will give some false positive though (armors that shouldn't have an XL version because it's not needed), but I'm working on removing all of them, and you can just remove them from the json files. If you could execute the script, you obviously have the knowledge for it
- 🔴🔴🔴**THE SCRIPT DELETES THE "results" FOLDER EACH TIME IT'S STARTED**🔴🔴🔴
	- This means, for safety, move the files somewhere else before editing them

### What is this blacklist file?
- The blacklist file contains a list of armor ids that shouldn't have an XL version, but could. 
	- Most of the time, it's because I saw that it was already created in other mods, so I added it in the blacklist. 
	- Somtimes, it's because that made no sense, eg saddle bags are tagged as armor, not pet armor, so you can create an XL version and put it on your mutant. 	- To continue this example, if that's your thing, remove the id from the blacklist file, and run the script
- If you want to add some ids to the blacklist for some valid reason, you can open an issue or make a PR about it, if you feel like it.
	- Balance isn't one, I'm totally ok with mutants being able to modify power armors to be able to wear them.  People that are not ok with it can remove them after the script or create their own blacklist, but balance should never be the reason to change the default blacklist.
- If at least one of the armor already has an XL version, it will print it to the console. Then you have to manually add it to the blacklist, by copy pasting the output, and restart the script (it's quite fast)

### How to use it?
- Install python 3 latest version
- Install the required libraries with pip `python -m pip install msgspec` (and maybe other libraries too, cf beginning of the script)
- Change your options in the script (every options are explained)
- Execute the script `python3 generate_xl_armors.py`
	- This will create the missing xl versions, for every mods and vanilla
	- Each xl armor/recipe/uncraft will be placed in the corresponding module, like below

![image](https://user-images.githubusercontent.com/71428793/199604364-d3536380-f20c-4202-b51c-285fff7e25de.png)
- Then, remove/change what you want, and drag and drop the files in your `mods` folder


### Some misc technical explanations
- the powershell script (.ps1) and the excecutable (.exe) are used to lint (rearange) the json files. They are executed at the very end of the python script
- the powershell script is just a slightly modified version of the one that can be found in `cdda/msvc-full-features/`. It lints the json files starting from the current directory, instead of trying to lint an inexistent data folder
- the executable is run by the powershell script on each file, again, to lint everything. This is the same version as the one you get when you build the entire solution, with visual studio (it's then in `cdda/tools/format/`)
- you can also set the linting option to False and lint your files through other means
