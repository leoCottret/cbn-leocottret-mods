"""
Generates mods containing XL armors versions of all the mods in your /mods/ folder
"""


from __future__ import annotations
import json
import shutil
import math
import subprocess  # IMPORT FOR SUB PROCESS . RUN METHOD
import msgspec
import pathlib
from datetime import datetime

from typing import Literal
from typing import Optional
from msgspec import Struct
from typing_extensions import Self




# CHANGE OPTIONS HERE
# WARNING at each script execution the results folder is deleted to create clean files
# Please move the files from the results folder before editing them, to be safe

# explicit. Existing armors, recipes, data from mods etc. Everything is fetched thanks to this variable
game_folder_path = f"C:\Games\CDDA_MODDING_BN_dummy\cdda\data"
# the resulting folder, with, for each module, the xl armors, recipes and uncraft recipes
# PS: modules = mods + vanilla
pathlib.Path("results").mkdir(parents=True, exist_ok=True)
result_folder = pathlib.Path("results")
# we don't went to create XL versions of some armors, this is a list of those ids
blacklist_file_name = "armors_blacklist.txt"
# if the armor id contains one of those keywords, exclude it. Difference with the blacklist is, 
# this won't search for an exact match, but if the id contains one of those words
blacklist_keywords = [ "badge_", "_bracelet", "_cat_ears", "_collar", "_cufflinks", "_earring", "_necklace" ]
# if you want to exclude some mod folders, it's here
blacklist_mod_folders = [ "TEST_DATA", "Dark-Skies-Above" ]

# set to False if you don't want to use the powershell script to lint your files
linting = True
# powershell exe location. Is used to execute the powershell script
POWERSHELL_PATH = r'C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe'
# path to the powershell script that will lint the result with the help of json_formatter.exe
PS_SCRIPT_PATH = r'C:\Games\CDDA_BN_MY_MODS\cbn-leocottret-mods\DEV_TOOLS\XL_ARMORS_GENERATOR\style-json-cur-dir.ps1'

# how punishing the XL versions will be, eg 1.2 encumbrance means 20% more from the original version
class XLFactors():
    encumbrance: int = 1.2
    volume: int = 1.2
    weight: int = 1.2
    storage: int = 1.2
    materials: int = 1.2 # how much we want to increase the materials in the recipe, 1.3 = 30% more materials needed

# to check if the json object is a valid armor. I think this covers every kind of armors, but just in case, it's in the options
armor_types = [ "ARMOR", "TOOL_ARMOR" ]
# to check if the json object is a valid recipe. Same comment as above
recipe_types = [ "recipe", "uncraft" ]

# sort blacklist by alphabetical order on script load, and replace file content, could be useful if the file becomes big. Shouble probably be always True
sort_blacklist:bool = True
# END OPTIONS, YOU SHOULDN'T HAVE TO CHANGE THINGS BELOW THAT


# used to create the vanilla module files, and give them some kind of flag. Mods use their folder name instead.
# also the id of the main xl armor mod. Will also be written before the xl armor mod extensions for each mod
# eg xl armor mod for arcana will have for id XL_Armors_Arcana
VANILLA_FLAG = "XL_Armors"

# to check if the json object is a valid modinfo
modinfo_type = "MOD_INFO"

now = datetime.now()
current_date = str(now.year) + "/" + str(now.month) + "/" + str(now.day)

# get the armor name in the gazillon of possibilities
def get_armor_name(armor: XLArmor|Armor):
    armor_name = None
    if (isinstance(armor.name, str)):
        armor_name = armor.name
    elif (isinstance(armor, XLArmor)):
        if (armor.name.str):
            armor_name = armor.name.str
        elif (armor.name.str_sp):
            armor_name = armor.name.str_sp
    else:
        if (armor.name.get("str")):
            armor_name = armor.name.get("str")
        elif (armor.name.get("str_sp")):
            armor_name = armor.name.get("str_sp")
    return armor_name


global existing_xl_armor_found
existing_xl_armor_found = False
# check if armor already exists in vanilla or one of your mods
def check_xl_armor_existence(armor: Armor, new_xl_armor: XLArmor, armor_blacklist_ids: list, potential_armors_data):
    global existing_xl_armor_found

    for module_files in potential_armors_data:
        for file_data in module_files:
            for a in file_data.data:
                # get armor name (either name is a string, it contains a str field, or a str_sp field)
                if (is_valid_armor(a, armor_blacklist_ids)):
                    # should cover most cases. Would have been simpler if there was some convention...
                    # if there's already an armor that has the same id as the original armor when 
                    #   the id starts with xl, and if we remove it, we have the same id EG xlboots_combat
                    #   the id starts with xl_, and if we remove it, we have the same id EG xl_jeans
                    #   the id ends with _xl, and if we remove this _xl, we get the same id EG armguard_acidchitin_xl
                    #   we replace _xl by _, and we get the same id EG tool_xlbelt
                    if (gus(a)[:2] == "xl" and gus(a)[2:] == gus(armor)) or (gus(a)[:3] == "xl_" and gus(a)[3:] == gus(armor)) or ("_xl" in gus(a) and gus(a).replace("_xl", "_") == gus(armor)) or (gus(a)[-2:] == "_xl" and gus(a)[:-2] == gus(armor)):
                        # if it's the first time, add a warning message
                        if not existing_xl_armor_found:
                            print("EXISTING XL ARMOR(S) FOUND, printing original armor ids:")
                            existing_xl_armor_found = True
                        print(armor.id)
                        return

# load all potential armors from this file. Returns a list of Armor objects
def get_potential_armors(targeted_file):
    if (not targeted_file.exists()):
        print("FILE DOESN T EXIST: " + targeted_file.name)
        exit()
        
    raw_json_object = msgspec.json.decode(targeted_file.read_bytes())
    new_raw_json_objects = []
    for raw_json in raw_json_object:
        valid:bool = False
        for allowed_armor_type in armor_types:
            # we want to avoid potential non armor objects in the file
            # so we check if it is of one of the armor type, if it has an id or a abstract field, and a name
            if ("'type': '"+allowed_armor_type+"'" in str(raw_json)) and ( ("'id': '" in str(raw_json)) or ("'abstract': '" in str(raw_json)) ) and ("'name':" in str(raw_json)):
                valid = True
        if (valid):
            new_raw_json_objects.append(raw_json)
    armors = msgspec.json.decode(json.dumps(new_raw_json_objects).encode('utf-8'), type=list[Armor])
    return armors

# load all potential recipes from this file. Returns a list of Recipe objects
def get_potential_recipes(targeted_file):
    if (not targeted_file.exists()):
        print("FILE DOESN T EXIST: " + targeted_file.name)
        exit()

    raw_json_object = msgspec.json.decode(targeted_file.read_bytes())
    new_raw_json_objects = []
    for raw_json in raw_json_object:
        valid:bool = False
        for allowed_recipe_type in recipe_types:
            # we want to avoid potential non recipe objects in the file
            if ("'type': '"+allowed_recipe_type+"'" in str(raw_json)) and ("'result': '" in str(raw_json)):
                valid = True
        if (valid):
            new_raw_json_objects.append(raw_json)
    recipes = msgspec.json.decode(json.dumps(new_raw_json_objects).encode('utf-8'), type=list[Recipe])
    return recipes

# load "all" potential mod info in this file. Sometimes mods contain non modinfo json objects (the mod content is in this file...). This filters it
def get_potential_mod_info(targeted_file):
    if (not targeted_file.exists()):
        print("FILE DOESN T EXIST: " + targeted_file.name)
        exit()

    raw_json_object = msgspec.json.decode(targeted_file.read_bytes())
    new_raw_json_objects = []
    for raw_json in raw_json_object:
        valid:bool = False
        # we want to avoid potential non modinfo objects in the file
        if ("'type': '"+modinfo_type+"'" in str(raw_json)) and ("'id': '" in str(raw_json)):
            new_raw_json_objects.append(raw_json)
    # will hopefully always be a list of one modinfo
    modinfo = msgspec.json.decode(json.dumps(new_raw_json_objects).encode('utf-8'), type=list[ModInfo])
    return modinfo

# if we want to avoid making a xl version of an armor, we put its id in the blacklist file
# this function load those ids and return them in an array
def load_blacklist_ids(file_name, sort_blacklist):
    blacklist_ids = []
    with open(file_name) as f:
        for armor_id in f:
            blacklist_ids.append(armor_id.replace('\n', ''))
    if (sort_blacklist):
        blacklist_ids = sorted(blacklist_ids)
        f = open(file_name, "w")
        for armor_id in blacklist_ids:
            f.write(armor_id + "\n")
        f.close()
    return blacklist_ids

# does this armor needs a xl version of it? Checks if it's in the blacklist, and if it has both no copy_from and no coverage
# an armor coverage means that this armor is only wearable by normal sized characters by default
# having encumbrance too!
def is_valid_armor(armor: ARMOR, armor_blacklist_ids: list | None):
    is_valid:bool = True
    # we don't create an xl version of blacklisted armor ids
    if armor_blacklist_ids:
        if (gus(armor) in armor_blacklist_ids):
            is_valid = False
    
    # we don't want to create a xl armor for something without coverage (and without copy-from), like earings, because they can be worn by mutants
    # having encumbrance will also
    elif (not armor.copy_from and (not armor.coverage or (armor.encumbrance != None and armor.encumbrance != 0))):
        is_valid = False
    # we don't want this armor if it contains one of the blacklisted keywords too
    for kw in blacklist_keywords:
        if kw in gus(armor):
            is_valid = False
            break

    return is_valid         

# was "get_unique_str" but it's used absolutly everywhere, so it's better that way
# now we have abstract armor objects! So we need a way to return either the id or the abstract field easily
def gus(armor: Armor):
    return armor.id if armor.id else armor.abstract

# return true if the armor is an xl armor
def is_xl_armor(armor: ARMOR):
    is_xl = False
    if "XL" in get_armor_name(armor):
        is_xl = True
    elif gus(armor)[:2] == "xl":
        is_xl = True
    elif "_xl" in gus(armor):
        is_xl = True
    elif gus(armor)[-2:] == "xl":
        is_xl = True

    return is_xl

# will check everything to be sure it's an armor that needs a XL version
# will be called recursively if copy_from is set
def check_if_needs_xl_armor(armor:Armor, armor_blacklist_ids, potential_armors_data, from_child=False):

    # if it's an abstract object and not from a child, we really don't want it!
    if armor.abstract and not from_child:
        return False

    # if it's an xl armor, not doubt, we don't want it
    # if it's a blacklisted id, has a blacklisted keyword, or has no coverage and no copy from, we also definitly don't want a XL armor
    if is_xl_armor(armor) or not is_valid_armor(armor, armor_blacklist_ids):
        return False

    # if it has the oversize flag, or inherit from itself, same, we don't want a XL version
    if (armor.flags and "OVERSIZE" in armor.flags) or (gus(armor) == armor.copy_from):
        return False

    # now if everything above passed, and the armor doesn't have a copy from, it's valid
    if not armor.copy_from:
        return True

    # otherwise, we get the parent and apply the same chekcs
    for module_files in potential_armors_data:
        for file_data in module_files:
            for a in file_data.data:
                # we found the parent (the copy-from id)!
                if gus(a) == armor.copy_from:
                    # IMPORTANT, we do not check if the armor is blacklisted here
                    # in case if we have an armor B that inherits from a blacklisted armor A
                    # well in that case, we don't care if armor A is blacklisted, we still need the info!
                    return check_if_needs_xl_armor(a, None, potential_armors_data, True)

    # if we didn't find the parent, it's best to create an armor
    # very rarely, an armor item inherit from a non armor item
    print(f"{armor.id}_xl -> Parent not found:{armor.copy_from} for the armor:{armor.id}. If the parent is from a non armor type, it's normal. Decides yourself if you want to keep the xl armor")
    return True

# load every potential recipes or armors, and store them with their respective file name, and it's origin (the mod folder or "IS_VANILLA")
# TODO set data_type as an enum
def load_potential_data(potential_data_folders, data_type, origin):
    potential_data = []
    for file_group in potential_data_folders:
        for targeted_file_path in file_group:
            data = []
            if (data_type == "ARMOR"):
                data = get_potential_armors(targeted_file_path)
            elif (data_type == "RECIPE"):
                data = get_potential_recipes(targeted_file_path)
            elif (data_type == "MOD_INFO"):
                data = get_potential_mod_info(targeted_file_path)
            else:
                print("WRONG DATA TYPE")
                exit()
            if len(data) > 0:
                file_data = FileData(targeted_file_path, data, origin)
                potential_data.append(file_data)
    return potential_data

# create a new file while being sure to not overwrite an existing file
def create_new_file(file_path):
    new_file = pathlib.Path(file_path)

    i:int = 2
    # if file exists, rename to name_2.json, and if it also exists name_3.json etc.
    # can happen if the mod uses at least 2 files with the same name and valid armors/recipes in all of them
    # those files being at different places in the mod tree. Tested, it works (doesn't exist in vanila)
    while new_file.exists():
        new_path = file_path.replace(".json", "_" + str(i) + ".json")
        new_file = pathlib.Path(new_path)
        i += 1
    return new_file

def create_mod_info_file(result_folder, file_origin, mod_info:ModInfo|None = None):
    new_modinfo_path = pathlib.Path(f"{result_folder}/{file_origin}/modinfo.json")
    # if mod_info is not null, this is the mod info file for a mod, otherwise it's the new xl armor mod for vanilla
    new_mod_info = ModInfo.from_mod_info(mod_info) if mod_info else ModInfo.generate_vanilla_file()
    new_mod_info_json = json.loads(msgspec.json.encode(new_mod_info))
    result_recipe_file = create_new_file(f"{result_folder}/{file_origin}/modinfo.json")
    result_recipe_file.write_bytes(json.dumps(new_mod_info_json, indent=2).encode('utf-8'))










# store the file name and the potential data (armors or recipes) in a file
class FileData:
    def __init__(self, file_path, data, origin):
        self.data = data
        self.file_path = file_path
        self.origin = origin

# set the name of an armor. Handle the 4 cases of
# 1) name:str 2) name:{str_sp} 3) name:{str} 4) name:{str, str_pl}
class Name(Struct, omit_defaults=True):

    str: str | None = None
    str_pl: str | None = None
    str_sp: str | None = None

    @classmethod
    def from_original_name(cls, original_name:list|str) -> Self:
        """Add the 'XL' in the name(s), at the right position"""
        # rare, annoying case of `name: armor_name`, handled here
        if (isinstance(original_name, str)):
            return cls(str=f"XL {original_name}", str_pl=None)

        local_str = original_name.get("str")
        local_str_pl = original_name.get("str_pl")
        local_str_sp = original_name.get("str_sp")

        # handle case like "pair of boots/gloves"
        if (local_str and "pair of " in local_str):
            begin, _, end = local_str.partition("pair of ")
            local_str = f"{begin}pair of XL {end}" 
            if (local_str_pl):
                begin_pl, _, end_pl = local_str_pl.partition("pairs of ")
                local_str_pl = f"{begin_pl}pairs of XL {end_pl}" 

        # otherwise, just add it at the start
        else:
             local_str = f"XL {local_str}" if local_str else None
             local_str_pl = f"XL {local_str_pl}" if local_str_pl else None
             local_str_sp = f"XL {local_str_sp}" if local_str_sp else None

        return cls(str=local_str, str_pl=local_str_pl, str_sp=local_str_sp)

# a minimal armor representation to generate its XL variants
class Armor(Struct, rename={"copy_from": "copy-from"}, omit_defaults=True):
    id: str | None = None# This might seem dangerous, but this can be true if an object is "abstract". In that case we skip the object
    abstract: str | None = None
    name: object
    type: str | None = None
    description: object | None = None
    copy_from: str | None = None # Used in conjunction with below, must not be set. Avoid excluding items for nothing, better than nothing
    coverage: int | None = None # To check if it exists. If it doesn't (eg earings), the object can be worn by a mutant by default
    encumbrance: int | None = None # To check if it exists. If it does (eg belts), the object can be worn by a mutant by default
    flags: list[str] | str | None = None # To check if it already has the OVERSIZE flag

# a proportional value modifier for armor. WIll generate the proportional field of the XL armor
class Proportional(Struct, omit_defaults=True):
    weight: float 
    volume: float
    storage: float
    encumbrance: float

# an extend value modifier for armor.
class Extend(Struct):
    flags: list[str] = ["OVERSIZE"]

# a XL Armor representation. 
class XLArmor(Armor, rename={"copy_from": "copy-from"}, omit_defaults=True):
    copy_from: str
    type: str
    proportional: Proportional
    extend: Extend

    @classmethod
    def from_armor(cls, armor: Armor, XL_factors: XLFactors) -> Self:
        """Generate an XL variant from a given armor."""
        added_description:str = "  This can be worn regardless of your state of mutation"
        if (hasattr(armor.description, "str")):
            description = f"{armor.description.str}{added_description}"
        else:
            description = f"{armor.description}{added_description}"        

        return cls(
            id=f"{armor.id}_xl",
            copy_from=armor.id,
            type=armor.type,
            name=Name.from_original_name(armor.name),
            extend=Extend(),
            description=description,
            proportional=Proportional(
                weight=XL_factors.weight, 
                volume=XL_factors.volume, 
                storage=XL_factors.storage, 
                encumbrance=XL_factors.encumbrance
            )
        )


# an armor recipe representation
class Recipe(Struct, rename={"copy_from": "copy-from"}, omit_defaults=True):    
    result: str | None = None
    copy_from: str | None = None # not sure if supported (very rarely used), but if it is one day, here it is
    id_suffix: str | None = None
    type: str | None = None
    category: str | None = None
    subcategory: str | None = None
    skill_used: str | None = None
    difficulty: int | None = None
    skill_required: list | None = None # complete type list[list[str|int]] | list[str|int] | None -> is not supported in python
    time: str | int | None = None
    reversible: bool | None = None
    autolearn: bool | list[list[str|int]] | None = None # can be bool or array
    decomp_learn: list[list[str|int]] | int | None = None # complete type list[list[str|int]] | list[?] | int | None
    book_learn: bool | list[list[str|int]] | None = None # can be bool or array
    qualities: list[object] | None = None
    using: list[list[str|int]] | None = None
    tools: list | str | None = None
    components: list[list[list[str|int]]] | None = None
    delete_flags: list[str] | None = None
    flags: list[str] | None = None

    # generate the XL armor recipe from the recipe of the original armor
    @classmethod
    def from_recipe(cls, recipe: Recipe, XL_factors: XLFactors) -> Self:
        # we mostly want to copy everything as is, except components, where we need to increase the number of materials used
        # very rare, but there can be no "components" field
        if recipe.components:
            for x in range(len(recipe.components)):
                for y in range(len(recipe.components[x])):
                    recipe.components[x][y][1] = math.floor(recipe.components[x][y][1] * XL_factors.materials)

        return cls(
            type=recipe.type,
            copy_from=recipe.copy_from,
            id_suffix=recipe.id_suffix,
            result=f"{recipe.result}_xl",
            category=recipe.category,
            subcategory=recipe.subcategory,
            skill_used=recipe.skill_used,
            skill_required=recipe.skill_required,
            time=recipe.time,
            difficulty=recipe.difficulty,
            reversible=recipe.reversible,
            autolearn=recipe.autolearn,
            book_learn=recipe.book_learn,
            components=recipe.components,
            decomp_learn=recipe.decomp_learn,
            qualities=recipe.qualities,
            tools=recipe.tools,
            using=recipe.using,
            delete_flags=recipe.delete_flags,
            flags=recipe.flags
        )

    # generate a XL recipe for an armor that doesn't have one in the game. So you can convert an armor to its xl version, and the opposit
    @classmethod
    def from_original_armor(cls, armor:Armor, recipe_type:str) -> Self:
        return cls(
            type=recipe_type,
            result=f"{armor.id}_xl",
            id_suffix=f"from_{armor.id}",
            skill_used="fabrication",
            time="20 m",
            reversible=True,
            autolearn=True,
            components=[ [ [ armor.id, 1 ] ] ]
        )


# a modinfo file representation
class ModInfo(Struct, omit_defaults=True):
    type: str
    id: str
    name: str
    description: str # used for the "vanilla mod"
    authors: list | None = None
    maintainers: list | None = None
    dependencies: list | None = None # in the futur (maybe), this will be used to generate xl armors and their recipes taking into account dependencies
    category: str
    version: str | None = None

    @classmethod
    def from_mod_info(cls, mod_info:ModInfo) -> Self:
        new_mod_name = "<color_cyan>" + VANILLA_FLAG.replace("_", " ") + "</color> for " + mod_info.name
        return cls(
            id=f"{VANILLA_FLAG}_{mod_info.id}",
            name=new_mod_name,
            type=modinfo_type,
            description=f"This is an extension that adds XL armors for the {mod_info.name} mod.",
            authors=["leoCottret"],
            maintainers=["leoCottret"],
            # in the futur (maybe), this will be used to generate xl armors and their recipes taking into account dependencies
            # this was also the main idea between this modinfo file generation for each mod
            # with this players won't have errors because they added a folder from a mod that they don't use in their world
            dependencies=[mod_info.id], 
            category="content",
            version=f"Bright Night, last update {current_date}"
        )

    @classmethod
    def generate_vanilla_file(cls) -> Self:
        new_mod_name = "<color_cyan>" + VANILLA_FLAG.replace("_", " ") + "</color>"
        return cls(
            id=VANILLA_FLAG,
            name=new_mod_name,
            type=modinfo_type,
            description=f"This is the main XL armors mod, that adds XL armors for vanilla.",
            authors=["leoCottret"],
            maintainers=["leoCottret"],
            dependencies=["bn"], 
            category="content",
            version=f"Bright Night, last update {current_date}"
        )






# the line below was from scarf, and means that this code will be executed only if we execute the script directly
# so this is interesting if the file get used as a "library" file, even if it's far from being ready for it
if __name__ == "__main__":
    # delete results folder content
    shutil.rmtree("results", True)
    pathlib.Path("results").mkdir(parents=True, exist_ok=True)

    # from vanilla files
    new_armors_amount_vanilla = 0
    # from mods
    new_armors_amount_mods = 0

    # load XL factors (cf options)
    XL_factors = XLFactors()

    # get every mod folders
    mod_root_folders = [x for x in pathlib.Path(game_folder_path + "/mods/").iterdir() if (not x.is_file() and x.name not in blacklist_mod_folders)]

    # load all potential armors, and put them in potential_armors_data
    vanilla_files = pathlib.Path(game_folder_path + "/json/items/" ).glob('**/*.json')
    potential_armors_data = []
    potential_armors_data.append(load_potential_data([vanilla_files], "ARMOR", VANILLA_FLAG))

    for mf in mod_root_folders: # mf for mod folder
        mod_files = pathlib.Path(str(mf)).glob('**/*.json')
        potential_mod_armor_data = load_potential_data([mod_files], "ARMOR", mf.name)
        potential_armors_data.append(potential_mod_armor_data)

    # load all potential recipes, and put them in potential_recipes_data
    vanilla_recipe_files = pathlib.Path(game_folder_path + "/json/recipes").glob('**/*.json')
    vanilla_uncraft_files = pathlib.Path(game_folder_path + "/json/uncraft").glob('**/*.json')
    potential_recipes_data = []
    potential_recipes_data.append(load_potential_data([vanilla_recipe_files, vanilla_uncraft_files], "RECIPE", VANILLA_FLAG))

    for mf in mod_root_folders:
        mod_files = pathlib.Path(str(mf)).glob('**/*.json')
        potential_mod_armor_data = load_potential_data([mod_files], "RECIPE", mf.name)
        potential_recipes_data.append(potential_mod_armor_data)

    # load blacklisted armor ids
    armor_blacklist_ids = load_blacklist_ids(blacklist_file_name, sort_blacklist)

    # "main loop"
    for module_files in potential_armors_data:
        for file_data in module_files:
            result_path = pathlib.Path(f"{result_folder}/{file_data.origin}")

            # XL armor generation part
            # will contain the xl armor jsons, that we will store in the output file
            xl_armors_json = []
            # store the selected armors to avoid duplicating the checks for the recipes
            selected_armors = []
            for armor in file_data.data:
                # we don't want to create a xl armor of a xl armor. Is not checked in is_valid_armor because this function is used in check_xl_armor... too   
                if check_if_needs_xl_armor(armor, armor_blacklist_ids, potential_armors_data):
                    xl_armor = XLArmor.from_armor(armor, XL_factors)
                    check_xl_armor_existence(armor, xl_armor, armor_blacklist_ids, potential_armors_data)
                    xl_armor_json = json.loads(msgspec.json.encode(xl_armor))
                    xl_armors_json.append(xl_armor_json)
                    selected_armors.append(armor)
                    if file_data.origin == VANILLA_FLAG:
                        new_armors_amount_vanilla += 1
                    else:
                        new_armors_amount_mods += 1

            # create a file with the new XL armors, with the same name as the original armor file, but with xl_ before
            if xl_armors_json:
                pathlib.Path(f"{result_path}/items/armor").mkdir(parents=True, exist_ok=True)
                result_file = create_new_file(f"{result_path}/items/armor/xl_{file_data.file_path.name}")
                result_file.write_bytes(json.dumps(xl_armors_json, indent=2).encode('utf-8'))

            # XL armor recipe generation part
            xl_recipes_json = []
            xl_recipes_uncraft_json = []
            # iterate through all potential recipe files
            for armor in selected_armors:
                armor_found:bool = False
                for module_files_recipes in potential_recipes_data:
                    for file_data_recipes in module_files_recipes:
                        # TODO, instead of checking for recipes in the mod folder or vanilla files, add support for dependencies of the mod too
                        # NOTE, you can still do this by putting only your mod and their dependencies in your mods folder, and then add "or True" below
                        if file_data_recipes.origin == file_data.origin or file_data_recipes.origin == VANILLA_FLAG:   
                            for recipe in file_data_recipes.data:
                                # we found the recipe of one of the selected armor, let's create the XL recipe from it
                                # note that, with this system, armors that have no recipes (eg power armor) are simply ignored, so the xl version will be created, but not the recipe
                                # so one would have to spawn himself an XL version of the armor
                                # or an other crazy idea could be to add the XL version to the loot tables, whenever the normal version spawn
                                if (recipe.result == armor.id):
                                    # only normal recipe means we found a recipe to craft the armor, not uncraft ones!
                                    if recipe.type == "recipe":
                                        armor_found = True
                                    xl_recipe = Recipe.from_recipe(recipe, XL_factors)
                                    xl_recipe_json = json.loads(msgspec.json.encode(xl_recipe))

                                    if (xl_recipe.type == "recipe"):
                                        xl_recipes_json.append(xl_recipe_json)
                                    elif (xl_recipe.type == "uncraft"):
                                        xl_recipes_uncraft_json.append(xl_recipe_json)
                                    else:
                                        print("Unrecognised recipe type " + xl_recipe.type + " for " + xl_recipe.result)
                                        exit()

                # if the armor has no recipe, no matter! Add a recipe to create an XL version from the original
                # so you can enjoy you XL linux tee-shirt, XL beekeeping gloves, XL clownshoes etc.
                if (not armor_found):
                    # we don't want recipes for active objects
                    if not armor.id[-3:] == "_on":
                        xl_recipe = Recipe.from_original_armor(armor, "recipe")
                        xl_recipe_json = json.loads(msgspec.json.encode(xl_recipe))
                        xl_recipes_json.append(xl_recipe_json)

            # create a file with the new XL recipes, with the same name as the original armor file, but with xl_ before
            if xl_recipes_json:
                pathlib.Path(f"{result_path}/recipes/armor").mkdir(parents=True, exist_ok=True)
                result_recipe_file = create_new_file(f"{result_path}/recipes/armor/xl_{file_data.file_path.name}")
                result_recipe_file.write_bytes(json.dumps(xl_recipes_json, indent=2).encode('utf-8'))

            if xl_recipes_uncraft_json:
                pathlib.Path(f"{result_path}/uncraft/armor").mkdir(parents=True, exist_ok=True)
                result_recipe_file = create_new_file(f"{result_path}/uncraft/armor/xl_{file_data.file_path.name}")
                result_recipe_file.write_bytes(json.dumps(xl_recipes_uncraft_json, indent=2).encode('utf-8'))

    # second "main loop", create the mod file for the corresponding mods
    mod_info_files = [x for x in pathlib.Path(game_folder_path + "/mods/").glob('**/*modinfo.json')]
    new_xl_armor_mods_folders = [x for x in pathlib.Path(f"{result_folder}").iterdir()]

    # get all mod info data of the modules from the newly generated xl armors and recipes
    mod_info_data = []
    for nxamf in new_xl_armor_mods_folders:
        for mif in mod_info_files:
            # if the modfile was in the same folder as this newly created one
            if nxamf.name == mif.parent.name:
                modinfo_data = load_potential_data([[mif]], "MOD_INFO", nxamf.name)
                mod_info_data.append(modinfo_data)

    # generate the new mod info files for the new folders in results
    # yes those are "valid mods" entirely generated by a script
    for module_files in mod_info_data:
        for file_data in module_files:
            for mod_info in file_data.data:
                create_mod_info_file(result_folder, file_data.origin, mod_info)
    # create the mod info file for the main XL armors mod
    create_mod_info_file(result_folder, VANILLA_FLAG)          

    # rename the module folder with vanilla flag, so they can be drag and drop in the /mods/ folder
    for nxamf in new_xl_armor_mods_folders:
        if not nxamf.name == VANILLA_FLAG:
            nxamf.rename(f"{result_folder}/{VANILLA_FLAG}_{nxamf.name}")
    print(f"New armors amount from vanilla files: {new_armors_amount_vanilla}")
    print(f"New armors amount from mods: {new_armors_amount_mods}")

    # lint XL armors and their recipes
    if linting:
        print("Linting everything...")
        process_result = subprocess.run([POWERSHELL_PATH, PS_SCRIPT_PATH], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
        if process_result.returncode == 0:  # COMPARING RESULT
            process_message = "Linting finished successfully"
        else:
            process_message = "An error Occurred! Did you specify the powershell script (absolute) path correctly?"
        print(process_message)