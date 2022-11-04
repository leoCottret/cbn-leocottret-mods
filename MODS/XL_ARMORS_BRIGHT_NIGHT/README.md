# XL Armors for Bright Night
## Why this?
- Huge mutants have a tiny, ridiculous choice of armors. There are some XL armors in the base game, but they cover only a few % of the available armors
- There are some mods that add XL armors, but they are very far from covering every armors
- In general, mods don't add XL versions of their armor too

## How to solve this injustice?
- Add 606 XL armors, and even more recipes for them (more on that below)
- Everything was generated with the script found [here](../../DEV_TOOLS/XL_ARMORS_GENERATOR)
- The main idea was to create a script that can generate XL armors for the base game and any mod automatically
- So you can enjoy your XL light survivor suit, XL bondage mask, XL heavy power armor, XL clown shoes, XL ring of strength +4...
  - In theory, everything that couldn't be worn by a huge mutant, now has its XL version
- Right now, all of the XL armors have 20% more weight, volume, encumbrance and storage than their normal version
  - I think it's a right balance between a discutable choice of adding encumbrance to something that just fits someone larger, and giving it no drawback, and then breaking the intended balance of the game
  - Note that it is roughly 5 to 10% below what's used for vanilla, depending on the armors, so not a huge change
- Their recipes also need 20% more materials

## How is this possible?
- The script generates XL armors based on a few custom parameters
- Then, if it finds an existing recipe, it creates one with more materials for the XL armor
- And if it doesn't find a recipe (eg for a power armor, that don't have a crafting recipe)?
  - It just creates a reversible recipe to craft the XL version from the original version
  - If that's not clear, if you find a power armor, you can craft an XL version of it, and disassemble the XL version to get a normal one

## What about XL armors already added by other mods (or vanilla)?
- I created a list of XL armors already added in other mods with the help of the script
- Then I added those armors to a blacklist, to avoid creating a XL version of them
- The main mod that you would want to use, to get access to all XL armors, is [More Armor](https://github.com/Kenan2000/BrightNights-Structured-Kenan-Modpack/tree/master/Kenan-BrightNights-Structured-Modpack/Medium-Maintenance-Small-Mods/More_Armor) mod from [Kenan's modpack](https://github.com/Kenan2000/BrightNights-Structured-Kenan-Modpack)
  - With Kenan's agreement, I recently changed the XL armors with the same multipliers as the ones written in "How to solve this injustice?"
- Vanilla XL armors are left untouched, and XL armors already added by other mods too

## What if I don't like the values of the XL armors?
- Using a tool like sublime text, right click on the XL_ARMORS_BRIGHT_NIGHT folder, and select find in folder
![image](https://user-images.githubusercontent.com/71428793/199932628-2e8de802-65b1-43cc-86e2-30670806ad44.png)

![image](https://user-images.githubusercontent.com/71428793/199935367-a74199aa-a666-42a7-ae07-940580741f95.png)

- 1 - In the find field, paste this line: `"proportional": { "weight": 1.2, "volume": 1.2, "storage": 1.2, "encumbrance": 1.2 }`
- In the Replace field, paste the same line and edit it as you want. 
- 2 - For example, starting from the normal version, if you want to increase the weight and volume by 60%, the storage by 20% and have the same encumbrance (no change from the normal version), the line in Replace would look like this: `"proportional": { "weight": 1.6, "volume": 1.6, "storage": 1.2 }`
- 3 - Click on Replace down right
- 4 - Click on Replace in the pop up
- 5 - Use CTRL + W then Enter to save every files and close them one by one
- Of course it's different without sublime text, but if you're not alergic to IT it's just what it is, a big search and replace.

