"""
Converts a file into
"""


from __future__ import annotations
import json
import shutil
import math
import subprocess  # IMPORT FOR SUB PROCESS . RUN METHOD
import msgspec
import pathlib

from typing import Literal
from typing import Optional
from msgspec import Struct
from typing_extensions import Self





# CHANGE OPTIONS HERE
# WARNING at each script execution the results folder is deleted to create clean files
# Please move the files from the results folder before editing them, to be safe

# the folder with the armors (we'll create xl versions of those). Can be the folder of your own mod
targeted_folder_path = "C:/Games/CDDA_BN_MY_CURRENT_GAME/cdda/data/"
# is used to check if an item already has xl verion
# only use when check_if_xl_armor_exists is set to true, to verify that an xl armor doesn't already exists in a mod
game_folder_path = "C:/Games/CDDA_BN_MY_CURRENT_GAME/cdda/data/"
# the resulting folder (with xl armors, recipes, uncraft recipes)
pathlib.Path("results").mkdir(parents=True, exist_ok=True)
result_folder = pathlib.Path("results")
# by default, recipes will be fetched from vanilla. This will add an extra location to check (useful for a mod)
# to disable this, just write a non existence path
targeted_recipes_folder = pathlib.Path("AzXiouOUIFH").glob('**/*.json')
# delete results folder on script start (highly recommended to avoid bugs)


# armors that we don't want to create an xl version
blacklist_file_name = "armors_blacklist.txt"
# powershell exe location
POWERSHELL_PATH = r'C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe'
# path to the powershell script that will lint the result with the help of the json_formatter.exe
PS_SCRIPT_PATH = r'C:\Users\Sudo\Desktop\python_tests\style-json-cur-dir.ps1'


# how punishing the XL versions will be, eg 1.2 encumbrance means 20% more from the original version
class XLFactors():
    encumbrance: int = 1.2
    volume: int = 1.2
    weight: int = 1.2
    storage: int = 1.2
    encumbrance: int = 1.2
    materials: int = 1.2 # how much we want to increase the materials in the recipe, 1.3 = 30% more materials needed

# to check if the json object is a valid armor. I think this covers every kind of armors, but just in case, it's in the options
armor_types = [ "ARMOR", "TOOL_ARMOR" ]
# to check if the json object is a valid recipe
recipe_types = [ "recipe", "uncraft" ]

# sort blacklist by alphabetical order on script load, and replace file content, could be useful if the file becomes big
sort_blacklist:bool = True
# if set to true, the script will check if an armor already exists, and will print it in the console if that's the case. This slows down a script by a lot
check_if_xl_armor_exists:bool = True


# END OPTIONS, YOU SHOULDN'T HAVE TO CHANGE THINGS BELOW THAT

VANILLA_FLAG = "VANILLA"


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
def check_xl_armor_existence(armor: Armor, new_xl_armor: XLArmor, armor_blacklist_ids, potential_armors_data):
    global existing_xl_armor_found

    for module_files in potential_target_armors_data:
        for file_data in module_files:
            for a in file_data.data:
                # get armor name (either name is a string, it contains a str field, or a str_sp field)
                if (is_valid_armor(a, armor_blacklist_ids)):
                    # should cover most cases. Would have been simpler if there was some convention...
                    # If there's already an armor that has the same id as the original armor when 
                    #   the id starts with xl, and if we remove it, we have the same id EG xlboots_combat
                    #   the id starts with xl_, and if we remove it, we have the same id EG xl_jeans
                    #   the id ends with _xl, and if we remove this _xl, we get the same id EG armguard_acidchitin_xl
                    #   we replace _xl by _, and we get the same id EG tool_xlbelt

                    if (a.id[:2] == "xl" and a.id[2:] == armor.id) or (a.id[:3] == "xl_" and a.id[3:] == armor.id) or ("_xl" in a.id and a.id.replace("_xl", "_") == armor.id) or (a.id[-3:] == "_xl" and a.id[:-3] == armor.id):
                        # if it's the first time, add a warning message
                        if not existing_xl_armor_found:
                            print("EXISTING XL ARMOR(S) FOUND, printing original armor ids:")
                            existing_xl_armor_found = True
                        print(armor.id)
                        return

def get_potential_armors(targeted_file):
    if (not targeted_file.exists()):
        print("FILE DOESN T EXIST: " + targeted_file.name)
        exit()

    raw_json_object = msgspec.json.decode(targeted_file.read_bytes())
    new_raw_json_objects = []
    for raw_json in raw_json_object:
        valid:bool = False
        for allowed_armor_type in armor_types:
            # if it has no id, eg an abstract object, skip it
            # if it has no name, skip it
            # we also want to avoid potential non armor objects in the file
            if ("'type': '"+allowed_armor_type+"'" in str(raw_json)) and ("'id': '" in str(raw_json)) and ("'name':" in str(raw_json)):
                valid = True
        if (valid):
            new_raw_json_objects.append(raw_json)
    armors = msgspec.json.decode(json.dumps(new_raw_json_objects).encode('utf-8'), type=list[Armor])
    return armors

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


# if we want to avoid making an xl version of an armor, we put its id in the blacklist file
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

def is_valid_armor(armor: ARMOR, armor_blacklist_ids):
    # get armor name (either name is a string, it contains a str field, or a str_sp field)
    armor_name = get_armor_name(armor)
    is_valid:bool = True
    # we don't create an xl version of blacklisted armor ids
    if (armor.id in armor_blacklist_ids):
        is_valid = False
    # we don't want to create a xl armor for something without coverage (and without copy-from), like earings, because they can be worn by mutants
    elif(not armor.copy_from and not armor.coverage):
        is_valid = False

    return is_valid         

# return true if the armor is an xl armor
def is_xl_armor(armor: ARMOR):
    ret_is_xl_armor = False
    if "XL" in get_armor_name(armor):
        ret_is_xl_armor = True
    elif armor.id[:2] == "xl":
        ret_is_xl_armor = True
    elif armor.id[:3] == "xl_":
        ret_is_xl_armor = True
    elif "_xl" in armor.id:
        ret_is_xl_armor = True
    return ret_is_xl_armor

# load every potential recipes or armors, and store them with their respective file name, and it's origin (the mod folder or "IS_VANILLA")
def load_potential_data(potential_data_folders, data_type, origin):
    potential_data = []
    for file_group in potential_data_folders:
        for targeted_file_path in file_group:
            data = []
            if (data_type == "ARMOR"):
                data = get_potential_armors(targeted_file_path)
            elif (data_type == "RECIPE"):
                data = get_potential_recipes(targeted_file_path)
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
    if (new_file.exists()):
        print("File already exists " + str(new_file.match))
    return pathlib.Path(file_path)








# store the file name and the potential data (armors or recipes) in a file
class FileData:
    def __init__(self, file_path, data, origin):
        self.data = data
        self.file_path = file_path
        self.origin = origin


class Name(Struct, omit_defaults=True):
    """Name of a Armor."""

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



class BNJsonObject(Struct):
    id: str | None = None # This might seem dangerous, but this can be true if an object is "abstract". In that case we skip the object
    type: str | None = None

class Armor(Struct, rename={"copy_from": "copy-from"}, omit_defaults=True):
    """A minimal armor representation to generate its XL variants."""

    id: str # This might seem dangerous, but this can be true if an object is "abstract". In that case we skip the object
    name: object
    type: str | None = None
    description: object | None = None
    copy_from: str | None = None # Used in conjunction with below, must not be set. Avoid excluding items for nothing, better than nothing
    coverage: int | None = None # To check if it exists. If it doesn't (eg earing), the object can be worn
    flags: list[str] | str | None = None # To check if it already has the OVERSIZE flag


class Proportional(Struct, omit_defaults=True):
    """A proportional value modifier for armor."""

    weight: float 
    volume: float
    storage: float
    encumbrance: float


class Extend(Struct):
    """An extend value modifier for armor."""

    flags: list[str] = ["OVERSIZE"]


class XLArmor(Armor, rename={"copy_from": "copy-from"}, omit_defaults=True):
    """XL Armor representation."""

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



class Recipe(Struct, rename={"copy_from": "copy-from"}, omit_defaults=True):
    """Armor recipe representation"""
    
    result: str | None = None
    copy_from: str|None = None # not sure if supported, but if it is one day, here it is
    id_suffix: str|None = None
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

    @classmethod
    def from_recipe(cls, recipe: Recipe, XL_factors: XLFactors) -> Self:
        """Generate the new XL armor recipe"""
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

    @classmethod
    def from_original(cls, armor:Armor, recipe_type:str) -> Self:
        """Generate XL recipes for armors that don't have one in the game. So you can convert an armor to its xl version, and the opposit"""
        return cls(
            type=recipe_type,
            result=f"{armor.id}_xl",
            id_suffix=f"from_{armor.id}",
            skill_used="fabrication",
            skill_required=recipe.skill_required,
            time="20 m",
            reversible=True,
            autolearn=True,
            components=[ [ [ armor.id, 1 ] ] ]
        )









if __name__ == "__main__":

    # delete results folder content
    shutil.rmtree("results", True)
    pathlib.Path("results").mkdir(parents=True, exist_ok=True)

    # load XL factors (cf options)
    XL_factors = XLFactors()

    # load all potential armors
    # get every mod folders
    targeted_folders = [x for x in pathlib.Path(game_folder_path + "/mods/").iterdir() if not x.is_file()]
    # append vanilla folder




    # load all potential armors
    vanilla_files = pathlib.Path(game_folder_path + "/json/items/" ).glob('**/*.json')
    potential_vanilla_armor_data = load_potential_data([vanilla_files], "ARMOR", VANILLA_FLAG)
    potential_target_armors_data = []
    potential_target_armors_data.append(potential_vanilla_armor_data)

    for mf in targeted_folders:
        mod_files = pathlib.Path(str(mf)).glob('**/*.json')
        potential_mod_armor_data = load_potential_data([mod_files], "ARMOR", mf.name)
        potential_target_armors_data.append(potential_mod_armor_data)

    # load all potential recipes
    vanilla_recipe_files = pathlib.Path(game_folder_path + "/json/recipes").glob('**/*.json')
    vanilla_uncraft_files = pathlib.Path(game_folder_path + "/json/uncraft").glob('**/*.json')
    potential_vanilla_recipes_data = load_potential_data([vanilla_recipe_files, vanilla_uncraft_files], "RECIPE", VANILLA_FLAG)
    potential_target_recipes_data = []
    potential_target_recipes_data.append(potential_vanilla_recipes_data)


    for mf in targeted_folders:
        mod_files = pathlib.Path(str(mf)).glob('**/*.json')
        potential_mod_armor_data = load_potential_data([mod_files], "RECIPE", mf.name)
        potential_target_recipes_data.append(potential_mod_armor_data)

    # set json and mods folder, will be used to create recipe files further
    armor_blacklist_ids = load_blacklist_ids(blacklist_file_name, sort_blacklist)

    for module_files in potential_target_armors_data:
        for file_data in module_files:
            # will contain the xl armor jsons, that we will store in the output file
            xl_armors_json = []
            # store the selected armors to avoid duplicating the checks for the recipes
            selected_armors = []
            result_path = pathlib.Path(f"{result_folder}/{file_data.origin}")

            for armor in file_data.data:
                # we don't want to create a xl armor of a xl armor. Is not checked in is_valid_armor because this function is used in check_xl_armor... too   
                if is_valid_armor(armor, armor_blacklist_ids) and not is_xl_armor(armor) and not (armor.flags and "OVERSIZE" in armor.flags) and armor.id != armor.copy_from:
                    xl_armor = XLArmor.from_armor(armor, XL_factors)
                    if (check_if_xl_armor_exists):
                        check_xl_armor_existence(armor, xl_armor, armor_blacklist_ids, potential_target_armors_data)
                    xl_armor_json = json.loads(msgspec.json.encode(xl_armor))
                    xl_armors_json.append(xl_armor_json)
                    selected_armors.append(armor)


            # create a file with the new XL armors, with the same name as the original armor file, but with xl_ before
            if xl_armors_json:
                # TODO set vanilla if vanilla, otherwise set mod
                pathlib.Path(f"{result_path}/items/armor").mkdir(parents=True, exist_ok=True)
                result_file = create_new_file(f"{result_path}/items/armor/xl_{file_data.file_path.name}")
                result_file.write_bytes(json.dumps(xl_armors_json, indent=2).encode('utf-8'))


            xl_recipes_json = []
            xl_recipes_uncraft_json = []
            # iterate through all potential recipe files
            for armor in selected_armors:
                armor_found:bool = False
                for module_files_recipes in potential_target_recipes_data:
                    for file_data_recipes in module_files_recipes:
                        # TODO, instead of checking for recipes in the mod folder or vanilla files, add support for dependencies of the mod too
                        # NOTE, if you want to get recipes from all the mods, just add or true below
                        if file_data_recipes.origin == file_data.origin or file_data_recipes.origin == VANILLA_FLAG:   
                            for recipe in file_data_recipes.data:
                                # we found the recipe of one of the selected armor, let's create the XL recipe from it
                                # note that, with this system, armors that have no recipes (eg power armor) are simply ignored, so the xl version will be created, but not the recipe
                                # so one would have to spawn himself an XL version of the armor
                                # or an other crazy idea could be to add the XL version to the loot tables, whenever the normal version spawn
                                if (recipe.result == armor.id):
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
                    xl_recipe = Recipe.from_original(armor, "recipe")
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

    # lint xl armors and their recipes
    print("Linting everything...")
    subprocess.run([POWERSHELL_PATH, PS_SCRIPT_PATH], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)

