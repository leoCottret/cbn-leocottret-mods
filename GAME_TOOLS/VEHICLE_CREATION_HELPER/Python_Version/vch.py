import PIL.ImageGrab
import pytesseract
import time
from pynput import keyboard
from pynput.keyboard import Key
import linecache
import msgspec
from msgspec import Struct
import pathlib
import json
import math
import datetime
import random
import sys
import traceback
import inspect

# GLOBALS (Uppercase doesn't mean I'm screaming at you, it's just a global variable)
# Flag to know if the current part needs a shape (so an Enter key pressed to start the installation)
NEEDS_SHAPE_TEXT = "Choose shape"
# Flag to know if a part can't be installed on a tile (usually there's a wall or something)
INSTALL_POSSIBLE_TEXT = "Time required"
# Flag to know if there's something that could be a danger (close monster, pain...)
DANGER_TEXTS = [ "(Case", "Sensitive)" ]
# Flags to know if we need to select a component (eg having a steel plating on the character and the ground)
SELECT_COMPONENT_TEXTS = [ "nearby)", "on person)" ]
# Get keyboard
KB = keyboard.Controller()
# Reference the original vch file name
VCH_FILE_NAME = "vch_original.json"
# Reference the updated vch file name,
VCH_UPDATED_FILE_NAME = "vch_updated.json"
# Options file name
OPTIONS_FILE_NAME = "options.json"
# Debug file name
DEBUG_FILE_NAME = "debug.txt"
# Will contain all the options from the options.json file
OPTIONS = None
# If true, script will be shut down in emergencey
EXIT_SCRIPT = False
# Take a screenshot of the screen
CURRENT_SCREENSHOT = PIL.ImageGrab.grab()
# Will contain all the data from vhc_original.json or vch_updated.json
VEHICLE_PARTS_DATA = []
# Explicit
INSTALLED_PARTS_COUNT = 0
# Store if the script has stopped correctly
SAFE_EXIT = False



# CLASSES
# defines the different possible data types
class DataType:
    OPTIONS, VEHICLE_PART = range(2)

# represent the cursor location in the install vehicle part menu
class Cursor():
	# horizontal position
    x: int = 0
    # vertical position
    y: list = 0

    def setxy(self, x, y):
        self.x = x
        self.y = y

# STRUCTS
# Represent the custom user controls
class Keys(Struct):
	# Key to fffilter vehicle parts to install
	ffilter: str
	install: str
	label: str
	# Since the lib doesn't support str|object
	up: object
	left: object
	right: object
	down: object

# Options representation, extracted from the options.json file
class OptionsData(Struct):
	# Change the time the script will wait between each key pressed, and between some actions. INCREASE if potato computer, and you may try to LOWER it if you have a beefy one. eg 2 -> 2 times slower, 0.5 -> 2 times faster.
	script_speed: float
	# How much time the script should wait when installing a part before stopping, because there's probably a problem. Recommended value: 45 seconds
	max_action_wait: float
	# How much time the script before the script starts, in seconds
	time_before_start: float
	# The script will stop if any of those text appear in the sidebar on the right side during a part installation. Extra safety, remove at your own risk
	custom_script_stop_flags: list
	# If you want to use the super duper save system or not
	use_save_system: bool
	# The custom user controls set in the options.json file
	keys: Keys


# a Vehicle Part Data representation
# 1 VPD = 1 json object in a vch file
class VehiclePartData(Struct):
	# The name of the vehicle part
    part_name: str
    # The "vehicle part map" each "X" will trigger an installation of the vehicle part at this location, other values are ignored
    vmap: list





# TEXT RECOGNITION FUNCTIONS
# Increment an index, and create one if it doesn't exist yet
def increment_char_frequency(llist, char):
	try:
		llist[char] = llist[char]
		llist[char] += 1
	except KeyError:
		llist[char] = 1

# Return the value from a dictionnary at this index if it exists, otherwise return 0
def get_value(dicti, index):
	try:
		return dicti[index]
	except KeyError:
		return 0

# Return the frequencies of all characters in the string
def get_character_frequencies(text):
	frequencies = {}
	for char in text:
		increment_char_frequency(frequencies, char)
	return frequencies

# Check if character frequencies are roughly similar, meaning that their differencies are below max_diff_allowed
def are_frequencies_roughly_similar(freq_1, freq_2, max_diff_allowed):
	# Store character differencies between text and line
	character_differencies_count = 0
	for char in freq_1:
		if abs(get_value(freq_1, char) - get_value(freq_2, char)) != 0:
			character_differencies_count += 1
	if character_differencies_count <= max_diff_allowed:
		return True
	return False

# Check if subline is roughly an anagram of text
# The main idea is that subline can have extra characters that move the rest of the characters
# So we check if they are "somewhat close", based on max_diff_allowed
# eg text:"house", subline:"hou s", max_diff_allowed = 1
# "hou" are ok
# "s" is ok because it's only one character on the right
# "e" cannot be found
# 80% of the characters have roughly the right position, so it's not an anagram.
# Also that's not exactly the definition of an anagram, but I didn't have a better word
def too_many_misplaced_characters(text, subline, max_diff_allowed):
	misplaced_character_count = 0
	for i in range(len(text)):
		character_found:bool = False
		for j in range(-max_diff_allowed, max_diff_allowed):
			# We skip any values out of range, in the text string
			if i+j < 0 or i+j>len(text)-1 or i+j>len(subline)-1:
				continue
			if text[i] == subline[i+j]:
				character_found = True

		if not character_found:
			misplaced_character_count += 1
	# We don't want a string with similar letter frequency but too many misplaced character, it's probably a word close to a anagram
	# If half of the letters are misplaced, we don't want it
	return (misplaced_character_count > max_diff_allowed)


# Returns the lines readen in defined borders of the last screenshot
def get_lines_on_screen_location(left, top, right, bottom, try_psm):
	global CURRENT_SCREENSHOT
	# Get img in delimited borders
	cropped_img = CURRENT_SCREENSHOT.crop((left, top, right, bottom))
	# Get lines in cropped image. 
	# The line below is by far the most computing heavy of the script, which is why I changed this current function to accept an array of texts
	lines = None
	if not try_psm:
		lines = pytesseract.image_to_string(cropped_img).split("\n")
	else:
		lines = pytesseract.image_to_string(cropped_img, config='--psm 6').split("\n")
	return lines


# Check if there is one of the texts on the screen, in the delimited borders given
def check_if_texts_are_on_screen_location(texts, left, top, right, bottom, do_update, threshold=10, try_psm=True):
	global CURRENT_SCREENSHOT
	# Update last screenshot of the screen
	if do_update:
		update_screenshot(threshold)
	
	lines = get_lines_on_screen_location(left, top, right, bottom, try_psm)

	# Iterate through all of the texts, then the lines
	for text in texts:
		# Compute character frequencies of text
		text_frequencies = get_character_frequencies(text)
		# Maximum difference allowed between line and text
		# The longer the text, the more errors are allowed
		# If (math.floor(len(text)/10) + 2) if (len(text) > 5) else 0
		max_diff_allowed = (math.floor(len(text)/17) + 2) if (len(text) > 5) else 0

		for line in lines:
			# First, check if the line has at least as much character as the text
			if not len(line) >= len(text):
				continue
			# Iterate over the line string, and return True if a match with text is found 
			# eg for "nice seats here", search for "seat", -> "nice", "ice ", "ce s", "e se", " sea", "seat" (bingo)
			start_char_nb = 0
			end_char_nb = len(text)
			while end_char_nb <= len(line):
				# Extract analyzed part of the line
				subline = line[start_char_nb:end_char_nb]
				# If one line is roughly equal to the text passed as parameter, return True
				line_frequencies = get_character_frequencies(subline)

				if are_frequencies_roughly_similar(text_frequencies, line_frequencies, max_diff_allowed) and are_frequencies_roughly_similar(line_frequencies, text_frequencies, max_diff_allowed):
					# We check if subline is not roughly an anagram of text. Can be the case for short words
					if not too_many_misplaced_characters(text, subline, max(max_diff_allowed, 1)) and not too_many_misplaced_characters(subline, text, max(max_diff_allowed, 1)):
						return True
				start_char_nb += 1
				end_char_nb += 1
	return False

# Update stored screenshot of the screen, and convert it to a b&w version
# Original code from https://stackoverflow.com/questions/9506841/using-pil-to-turn-a-rgb-image-into-a-pure-black-and-white-image#9506960
# The basic idea:
# 1)
# In a colored image, each pixel stores a "RGB" value, so each pixel color is defined by 3 values (Red, Green, Blue)
#	Each value will have a range from 0 to 255. Pure white is (255, 255, 255) and pure black is (0, 0, 0)
# Converting a picture to black & white (shades of grey) basically means to do the average of those 3 values, for each pixel
# So after this we have a shade of grey for each pixel, which will be a value between 0 (pure white) and 255 (pure black)
# 2)
# To make the text recognition with pytesseract work best, we need a picture with only 2 color value for each pixel, 0 or 255, so the text contrast perfectly with the background
# 3)
# Most, if not all of the text in Cataclysm is white or clear color text on dark background. pytesseract works better with the opposit
# 
# With this basic knowledge, hopefully it becomes easier to understand what those parameters do
# threshold: is the limit at which a pixel will be either pure white or pure black, depending on its "shade of grey" value
# reverse: since pytesseract works (much) better with a black text on a white background, and cataclysm uses the opposit, we reverse the image (clear pixels become black, and the opposit)
def update_screenshot(threshold, reverse=True):
	global CURRENT_SCREENSHOT
	fn = None
	if reverse:
		fn = lambda x : 0 if x > threshold else 255
	else:
		fn = lambda x : 255 if x > threshold else 0

	CURRENT_SCREENSHOT = PIL.ImageGrab.grab().convert('L').point(fn, mode='1').convert('1')
	# CURRENT_SCREENSHOT.show() # Uncomment to see the resulting image for the text recognition
	# sys.exit()


# KEYBOARD FUNCTIONS (and listener)

# Press and release a key
def send_key(key):
	# if escape has been pressed, we just avoid sending the key. The exit function is handled in create_new_cvh_file
	if EXIT_SCRIPT:
		return
	# Send the key and wait X seconds
	KB.press(key)
	KB.release(key)
	time.sleep(0.0355*OPTIONS.script_speed)

# Press characters in a row
def send_text(text):
	for char in text:
		send_key(char)

# Open filter, send filter text, and confirm
def search_filter(text):
	global OPTIONS
	send_key(OPTIONS.keys.ffilter)
	send_text(text)
	send_key(Key.enter)

# Stop script if left control is pressed. Is executed each time a key is pressed
# Since this is asynchronous, we register that the player wants to stop the script, and stop it in the "main thread" ASAP
def on_press(key):
	global EXIT_SCRIPT
	if key == Key.ctrl_l:
		EXIT_SCRIPT = True

# Set the key objects for arrow keys if needed, otherwise use whatever the player set in options.json
def set_move_keys():
	global OPTIONS
	OPTIONS.keys.up = Key.up if (OPTIONS.keys.up=="UP") else OPTIONS.keys.up
	OPTIONS.keys.left = Key.left if (OPTIONS.keys.left=="LEFT") else OPTIONS.keys.left
	OPTIONS.keys.right = Key.right if (OPTIONS.keys.right=="RIGHT") else OPTIONS.keys.right
	OPTIONS.keys.down = Key.down if (OPTIONS.keys.down=="DOWN") else OPTIONS.keys.down

# FILE FUNCTIONS
# Store the updated VEHICLE_PARTS_DATA state (which parts have been successfully installed, and which ones are not)
# More importantly, if a vehicle part is installed in every locations where it needed to be, we remove the entire object to avoid moving the cursor for no reason
def update_vhc_updated_file():
	global VEHICLE_PARTS_DATA
	new_vehicle_parts_data = []
	for vpd in VEHICLE_PARTS_DATA:
		# Store if the vehicle part has been installed in every locations where it needed to be, or if that's not the case
		every_locations_installed: bool = True
		for vehicle_row in range(len(vpd.vmap)):
			for vehicle_col in range(len(vpd.vmap[vehicle_row])):
				if vpd.vmap[vehicle_row][vehicle_col] == "X":
					every_locations_installed = False
					break
			if not every_locations_installed:
				break
		if not every_locations_installed:
			new_vehicle_parts_data.append(vpd)
	# Finally, create the new vhc file
	if len(new_vehicle_parts_data) != 0:
		create_custom_pretty_json_file(VCH_UPDATED_FILE_NAME, new_vehicle_parts_data, 2)
	# If we have no more vehicle parts to install, delete the file instead
	else:
		pathlib.Path(VCH_UPDATED_FILE_NAME).unlink() if pathlib.Path(VCH_UPDATED_FILE_NAME).exists() else None


# Print the text and append it to the debug file
def print_and_log(text):
	global DEBUG_FILE_NAME
	print(text)
	f = open(DEBUG_FILE_NAME, "a")
	f.write(text + "\n")
	f.close()
# Create a prettier version of the vch_updated file
# Similar to the vch_updated_formater.ps1 file but without external dependencies, reducing crossplateform compatibility
# It has a very generic name but it's just compatible enough for this script
def create_custom_pretty_json_file(file_name, objects, spaces_count):
	f = open(file_name, "w")
	spaces = " " * spaces_count
	nested_level = 0
	file_content = ""

	file_content += (nested_level*spaces) + "[\n"
	nested_level+=1

	for o_nb in range(len(objects)):
		file_content += (nested_level*spaces)+"{\n"
		nested_level+=1
		
		user_defined_attributes = []
		for attribute in inspect.getmembers(objects[o_nb]):
			# Excluding default unrelated attributes
			if not attribute[0].startswith('__'):
				user_defined_attributes.append(attribute)
		for a_nb in range(len(user_defined_attributes)):
			# For each attribute, we'll repeat this operation
			# Write attribute name
			file_content += (nested_level*spaces)+'"' +user_defined_attributes[a_nb][0]+ '": '
			# Write its value, taking the type into account
			a = user_defined_attributes[a_nb][1]
			# The function is not generic for now, it's just adapted for vmap.
			# To make it generic, one would have to make a recursive function to find the last nested array, and only write this one on one line (at least that's my idea)
			if type(a) == list:
				# Build one vmap
				file_content += "[\n"
				nested_level+=1
				for row in range(len(a)):
					# Build one line
					file_content += (nested_level*spaces)+"["
					for col in range(len(a[row])):
						if col != len(a[row])-1:
							file_content += f" \"{a[row][col]}\","
						else:
							file_content += f" \"{a[row][col]}\""
					if row != len(a)-1:
						file_content += " ],\n"
					else:
						file_content += " ]\n"
				# End of vmap
				nested_level-=1
				file_content += (nested_level*spaces)+"]"
			elif type(a) == str:
				file_content += f"\"{a}\""
			# End of one attribute
			if a_nb != len(user_defined_attributes)-1:
				file_content += ",\n"
			else:
				file_content += "\n"
		# End of one json object
		nested_level-=1
		if o_nb != len(objects)-1:
			file_content += (nested_level*spaces)+"},\n"
		else:
			file_content += (nested_level*spaces)+"}\n"
	
	nested_level-=1
	file_content += "]" + "\n"
	f.write(file_content)
	f.close()

# Check if the file is correctly formatted and exist, then call the right function to load the objects type
# Load either the objects from the vch_original.json file, or from the options.json one
def get_objects_from_file(targeted_file, data_type:DataType):
    # try to decode the file, if there's an error in the json formatting, it will print the absolute path and stop the script
    raw_json_objects = None
    try:
        raw_json_objects = msgspec.json.decode(targeted_file.read_bytes())
    except msgspec.DecodeError:
        exit_with_msg(f"FILE JSON DECODE ERROR on file: {targeted_file.resolve()} \nPlease format it correctly.")

    if data_type == DataType.VEHICLE_PART:
        return msgspec.json.decode(json.dumps(raw_json_objects).encode('utf-8'), type=list[VehiclePartData])
    elif data_type == DataType.OPTIONS:
        return msgspec.json.decode(json.dumps(raw_json_objects).encode('utf-8'), type=list[OptionsData])
    else:
        exit_with_msg("WRONG DATA TYPE")




# OTHER FUNCTIONS

# Convert compressed vehicle rows from vch_original.json to their uncompressed versions (eg [nb1:nb2, ...] and [nb3, ...])
def process_vehicle_parts(raw_vehicle_parts_data):
	# Iterate on vehicle parts
	for vpd in raw_vehicle_parts_data:
		# We begin at row one
		cursor:int = 1
		new_vmap = []
		# We iterate through all of the rows
		for vehicle_row in range(len(vpd.vmap)):
			# We iterate through the cols of each row
			first_symbol_row = None
			for vehicle_col in range(len(vpd.vmap[vehicle_row])):
				if vpd.vmap[vehicle_row][vehicle_col] != " ":
					first_symbol_row = vpd.vmap[vehicle_row][vehicle_col]
					break
			# We have the first symbol, now to process what it means
			# If it's a X, or the line is full of spaces, just append the row and skip to the next one
			if first_symbol_row == "X" or not first_symbol_row:
				# making a deep copy of the row, otherwise all rows will share the same content
				new_vmap.append(vpd.vmap[vehicle_row].copy())
				cursor += 1
				continue
			# If it contains a ":", we have a range of number
			if ":" in first_symbol_row:
				nb_before, nb_after = first_symbol_row.split(":")
				# First, we have to reach the first number by appending rows of space
				while cursor < int(nb_before):
					new_vmap.append([" "])
					cursor += 1

				# Then, we need to change the case with the range to a X (to avoid duplications if we save and reload it)
				for vehicle_col in range(len(vpd.vmap[vehicle_row])):
					if ":" in vpd.vmap[vehicle_row][vehicle_col]:
						vpd.vmap[vehicle_row][vehicle_col] = "X"

				# Finally we append this "processed row" until we reach nb_after
				while cursor <= int(nb_after):
					new_vmap.append(vpd.vmap[vehicle_row].copy())
					cursor += 1
				continue

			# If it contains a digit (and it's not a range), just append rows of space until we reach this row, then append the row
			if first_symbol_row.isnumeric():
				# First, we have to reach the first number by appending rows of space
				while cursor < int(first_symbol_row):
					new_vmap.append([" "])
					cursor += 1
				# Then, we need to change the case with the range to a X (to avoid duplications if we save and reload it)
				for vehicle_col in range(len(vpd.vmap[vehicle_row])):
					if vpd.vmap[vehicle_row][vehicle_col].isnumeric():
						vpd.vmap[vehicle_row][vehicle_col] = "X"

				new_vmap.append(vpd.vmap[vehicle_row])
				cursor += 1
				continue
		# Replace the vmap with the freshly created one
		vpd.vmap = new_vmap
	# Return as processed
	return raw_vehicle_parts_data



def exit_with_msg(msg):
	global SAFE_EXIT
	print_and_log(msg)
	if OPTIONS.use_save_system:
		update_vhc_updated_file()
	SAFE_EXIT = True
	sys.exit()

# Since we check it several item, I made a function for it
def is_vehicle_part_installed(vehicle_part_name, try_psm = False):
	return check_if_texts_are_on_screen_location([vehicle_part_name], 0, CURRENT_SCREENSHOT.height/3, CURRENT_SCREENSHOT.width/4, CURRENT_SCREENSHOT.height-165, True, 120, try_psm)

# Since filters tend to give weird results sorting eg you search for "aisle", and the results will be "aisle with lights", then "aisle"
# Get the part that matches our result (supposing it's a perfect match). And if it's not the first result, press down until we're on it ><
# TODO improve it by using the frequencies system, for now it's good enough since this kind of problem happen on short words, who rarely have mistakes in their recognition
# And long words tend to don't have this problem since, well, they are long enough to be the only result
def select_vehicle_part_to_install(vehicle_part_name):
	vparts_choices = get_lines_on_screen_location(CURRENT_SCREENSHOT.width/3, 0, 2*CURRENT_SCREENSHOT.width/3, CURRENT_SCREENSHOT.height/2, False)
	shortest_vehicle_part_name_index = 0
	shortest_vehicle_part_name_len = 999 
	for vp_index in range(len(vparts_choices)):
		# if one of the proposed part to install contains our vehicle part name, check if it's shorter than the previous one
		if vehicle_part_name in vparts_choices[vp_index]:
			if len(vparts_choices[vp_index])<shortest_vehicle_part_name_len:
				shortest_vehicle_part_name_len = len(vparts_choices[vp_index])
				shortest_vehicle_part_name_index = vp_index
	# If the part with our vehicle part name and the shortest name isn't the first one, move to it!
	if shortest_vehicle_part_name_index != 0:
		curs = 0
		while curs < shortest_vehicle_part_name_index:
			send_key(Key.down)
			curs += 1


# Install a vehicle part at current cursor location
def install_vehicle_part(vehicle_part_name):
	global EXIT_SCRIPT
	global OPTIONS
	# Open install menu
	send_key(OPTIONS.keys.install)
	time.sleep(0.1*OPTIONS.script_speed)
	# Check if we can construct a part here, if that's the case, early return
	if not check_if_texts_are_on_screen_location([INSTALL_POSSIBLE_TEXT], CURRENT_SCREENSHOT.width/2, 0, CURRENT_SCREENSHOT.width, CURRENT_SCREENSHOT.height/2, True):
		print_and_log(f"{vehicle_part_name} has been skipped, no installation possible here")
		return False

	search_filter(vehicle_part_name)

	# If a similar part is already installed or we don't have the materials, the part won't appear, or won't appear with enough contrast to be read
	if not check_if_texts_are_on_screen_location([vehicle_part_name], CURRENT_SCREENSHOT.width/3, 0, 2*CURRENT_SCREENSHOT.width/3, CURRENT_SCREENSHOT.height/4, True, 230):
		print_and_log(f"{vehicle_part_name} has been skipped")
		send_key(Key.esc)
		return False
	# Most of the time is the already selected one, but sometimes we have to select an other further below
	select_vehicle_part_to_install(vehicle_part_name)

	# Start installation
	send_key(Key.enter)
	# Select shape if needed
	send_key(Key.enter)
	time.sleep(0.1*OPTIONS.script_speed)

	# Wait until part is installed
	# Update the last screenshot of the scren only once every 500ms, no need to burn the computer
	time_waited = 0
	try_psm: bool = False
	while not is_vehicle_part_installed(vehicle_part_name, try_psm):
		# Check if the game needs us to select a part location
		if check_if_texts_are_on_screen_location(SELECT_COMPONENT_TEXTS, CURRENT_SCREENSHOT.width/3, CURRENT_SCREENSHOT.height/3, CURRENT_SCREENSHOT.width*2/3, CURRENT_SCREENSHOT.height*2/3, False):
			send_key(Key.enter)

		if EXIT_SCRIPT:
			exit_with_msg("User pressed the exit key, stopping the script")
		if time_waited > OPTIONS.max_action_wait:
			exit_with_msg("For unknown reasons, the vehicle part couldn't be installed")


		if time_waited > 5:
			# Check for warning messages (center of the screen)
			if check_if_texts_are_on_screen_location(DANGER_TEXTS, CURRENT_SCREENSHOT.width/5, CURRENT_SCREENSHOT.height/4, CURRENT_SCREENSHOT.width*4/5, CURRENT_SCREENSHOT.height*3/4, False):
				exit_with_msg("Warning message detected! Could be dangerous, stopping the script")	


		# Check for flags on the right sidebar that indicates that we need to stop the script. Can be customized in the options.json file
		# Since they are a bit computing heavy, we do those check once at the start of each part
		if len(OPTIONS.custom_script_stop_flags) > 0 and time_waited == 0 and INSTALLED_PARTS_COUNT % 3 == 0:
			if check_if_texts_are_on_screen_location(OPTIONS.custom_script_stop_flags, CURRENT_SCREENSHOT.width*2/3, 0, CURRENT_SCREENSHOT.width, CURRENT_SCREENSHOT.height/2, True):
				exit_with_msg("Custom script stop flag detected! Stopping the script")

		try_psm = not try_psm

		time.sleep(0.3*OPTIONS.script_speed)
		time_waited += (0.3*OPTIONS.script_speed)
	return True

# Process the cursor movements to reach the goal (the tile with the vehicle part to install), on the install vehicle part menu
def process_cursor_move(current_cursor:Cursor, next_goal:Cursor):
	while(current_cursor.x != next_goal.x or current_cursor.y != next_goal.y):
		if current_cursor.x < next_goal.x:
			send_key(Key.right)
			current_cursor.x += 1
		if current_cursor.x > next_goal.x:
			send_key(Key.left)
			current_cursor.x -= 1
		if current_cursor.y < next_goal.y:
			send_key(Key.down)
			current_cursor.y += 1
		if current_cursor.y > next_goal.y:
			send_key(Key.up)
			current_cursor.y -= 1

# --- MAIN ---
try:
	# Load the OPTIONS object from the options.json file
	OPTIONS = get_objects_from_file(pathlib.Path(OPTIONS_FILE_NAME), DataType.OPTIONS)[0]
	set_move_keys()
	# Load the vehicle parts objects from the vch_original.json file, or the vhc_updated.json one (if use_save_system is set to true, and the updated file exists)
	raw_vehicle_parts_data = get_objects_from_file(pathlib.Path(VCH_UPDATED_FILE_NAME if (OPTIONS.use_save_system and pathlib.Path(VCH_UPDATED_FILE_NAME).exists()) else VCH_FILE_NAME), DataType.VEHICLE_PART)
	# We must process data only if it's in a compressed state (coming from the original file)
	VEHICLE_PARTS_DATA = process_vehicle_parts(raw_vehicle_parts_data) if (not OPTIONS.use_save_system or not pathlib.Path(VCH_UPDATED_FILE_NAME).exists()) else raw_vehicle_parts_data
	
	# Wait X seconds to leave the player the time to switch to the game
	time.sleep(OPTIONS.time_before_start)

	# Listen for keys pressed, so the script can be stopped if Left Control is pressed. Hardcoded because it also monitors the keys sent by the script... could be improved
	listener = keyboard.Listener(on_press=on_press)
	listener.start()

	# Logging when the script starts
	print_and_log("\nNew script execution: "+ str(datetime.datetime.now()))
	# Cursor position in the install vehicle part menu
	current_cursor = Cursor()
	# Position (tile coordinates) of the next vehicle part to install
	next_goal = Cursor()
	for vpd in VEHICLE_PARTS_DATA:
		next_goal.setxy(0, 0)
		# Iterate through all vehicle parts
		for vehicle_row in range(len(vpd.vmap)):
			for vehicle_col in range(len(vpd.vmap[vehicle_row])):
				# Stops the script because of user
				if EXIT_SCRIPT:
					exit_with_msg("User pressed the exit key, stopping the script")
				# If there's a X on the vmap, set it as goal for the cursor
				if vpd.vmap[vehicle_row][vehicle_col] == "X":
					next_goal.setxy(vehicle_col, vehicle_row)
				# No need to go further, this part doesn't need an install
				else:
					continue
				# Process the cursor movements to reach the goal, then mark them as done
				process_cursor_move(current_cursor, next_goal)
				current_cursor.setxy(next_goal.x, next_goal.y)

				# Install part if it's not already installed
				if not (is_vehicle_part_installed(vpd.part_name) or is_vehicle_part_installed(vpd.part_name, True)):
					# If installation finished successfully, change the value to D(one)
					if install_vehicle_part(vpd.part_name):
						vpd.vmap[vehicle_row][vehicle_col] = "D"
						INSTALLED_PARTS_COUNT += 1
				# If the part is already installed without the script, mark it as installed
				else:
					vpd.vmap[vehicle_row][vehicle_col] = "D"

	# Show that the script is fully finished
	send_text(f"{OPTIONS.keys.label}Script finished :)")
	time.sleep(2)
	send_key(Key.esc)
	exit_with_msg("Script fully finished")

except:
	# If SAFE_EXIT hasn't been set to true, nothing has been written in the debug file
	# It's probably an unhandled exception or the player that stopped the script abruptly
	# So we log the exception here
	if not SAFE_EXIT:
	    exit_with_msg(str(traceback.format_exc()))