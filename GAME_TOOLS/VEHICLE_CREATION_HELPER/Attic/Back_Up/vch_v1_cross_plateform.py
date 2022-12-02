# Older version of the VCH, with less dependencies and lots of differencies
import time
from pynput import keyboard
from pynput.keyboard import Key

import msgspec
from msgspec import Struct
import pathlib
import json

# OPTIONS
# Delay between each key pressed, in seconds
KEYS_DELAY = 0.05
# Will change the time that the script waits before trying to install a new part. Depends on what's on the map and the computer specs. Increase if it's laggy.
LAG_FACTOR = 200
# The number of minutes in game before the script stop. When it stops, it will create a new vch file with the updated state of the vehicle
TIME_BEFORE_SCRIPT_STOP = 261

# Get keyboard
kb = keyboard.Controller()
# Reference vch file name, for file incrementation
vch_file_name = "vch.json"
# If true, script will be shut down in emergencey
exit_script = False
current_part_installed = False



# CLASSES
class CurrentVPartData():
    row: int = -1
    col: int = -1
    part_name: str = ""


# STRUCTS
# a Vehicle Part Data representation
# 1 VPD = 1 json object in a vch file
class VehiclePartData(Struct):
    part_name: str
    estimated_time: int
    needs_shape: int
    vmap: list




# FUNCTIONS
# Press and release a key
def sendKey(key):
	# if escape has been pressed, we just avoid sending the key. The exit function is handled in create_new_cvh_file
	if exit_script:
		return
	# Send the key and wait X seconds
	kb.press(key)
	kb.release(key)
	time.sleep(KEYS_DELAY)

# Press characters in a row
def sendText(text):
	for char in text:
		sendKey(char)

# Open filter, send filter text, and confirm
def searchFilter(text):
	sendKey("/")
	for char in text:
		sendText(char)
	sendKey(Key.enter)

# Install a vehicle part at current cursor location
def installVehiclePart(vehicle_part_name, needs_shape, estimated_time):
	global current_part_installed 
	current_part_installed = False
	# Open install menu
	sendKey("i")
	searchFilter(vehicle_part_name)
	sendKey(Key.enter)
	if needs_shape:
		sendKey(Key.enter)

	# We consider the part installed only if we just sent the last key to start the installation without exiting the script
	if not exit_script:
		current_part_installed = True
	final_estimated_time = (estimated_time/5) * (LAG_FACTOR/100)
	time.sleep(final_estimated_time)


# Stop script if the escape key has been pressed
def on_press(key):
	global exit_script
	global vehicle_parts_data
	if key == Key.esc:
		create_new_vhc_file(vehicle_parts_data)
		exit_script = True


# Get the most recent vch file, or get the next one to create
def get_vch_file(file_path, get_last_existing_file=False):
    i:int = 1
    # if file exists, rename to name_00002.json, and if it also exists name_00003.json etc.
    while True:
        file = pathlib.Path(file_path.replace(".json", "_" + str(i).zfill(5) + ".json"))
        if not file.exists():
            if get_last_existing_file:
                file = pathlib.Path(file_path.replace(".json", "_" + str(i-1).zfill(5) + ".json"))
            return file
        i += 1

# Get last VCH file data
# Check if the file is correctly formatted and exist, then call the right function to load the objects type
def get_vch_data(targeted_file):
    # try to decode the file, if there's an error in the json formatting, it will print the absolute path and stop the script
    raw_json_objects = None
    try:
        raw_json_objects = msgspec.json.decode(targeted_file.read_bytes())
    except msgspec.DecodeError:
        print(f"FILE JSON DECODE ERROR on file: {targeted_file.resolve()} \nPlease format it correctly.")
        exit()
    return msgspec.json.decode(json.dumps(raw_json_objects).encode('utf-8'), type=list[VehiclePartData])


# Stop script if escape is pressed. Is executed each time a key is pressed
def on_press(key):
	global exit_script
	print(key)
	if key == Key.esc:
		exit_script = True

# Create the new vhc file, because the script needs to stop. Either because the player pressed Escape, or the character needs to eat/drink/sleep
def create_new_vhc_file(vehicle_parts_data:VehiclePartData):
	global lastInstalledVPartData
	after_current_part:bool = False
	new_vehicle_parts_data_json = []
	for vpd in vehicle_parts_data:
		# If we're before this part, we already fully did it, so we skip it
		if not after_current_part and vpd.part_name != lastInstalledVPartData.part_name:
			continue
		# If we're on the current part
		if vpd.part_name == lastInstalledVPartData.part_name:
			new_vpd = vpd
			after_current_part = True
			after_current_point:bool = False
			# here we need to update the current part, then we store it
			for vehicle_row in range(len(vpd.vmap)):
				for vehicle_col in range(len(vpd.vmap[vehicle_row])):

					# We assume that the current vehicle part is installed
					if vehicle_row == lastInstalledVPartData.row and vehicle_col == lastInstalledVPartData.col:
						after_current_point = True
						vpd.vmap[vehicle_row][vehicle_col] = " "
						break
					# Remove already installed parts
					if not after_current_point and vpd.vmap[vehicle_row][vehicle_col] == "X":
						vpd.vmap[vehicle_row][vehicle_col] = " "
				if after_current_point:
					break
			new_vehicle_parts_data_json.append(json.loads(msgspec.json.encode(new_vpd)))
			continue


		new_vehicle_parts_data_json.append(json.loads(msgspec.json.encode(vpd)))
	# Finally, create the new vhc file
	new_vhc_file = get_vch_file(vch_file_name)
	new_vhc_file.write_bytes(json.dumps(new_vehicle_parts_data_json, indent=2).encode('utf-8'))
	exit()





# --- MAIN ---
# Wait 5 seconds to leave the player the time to switch to the game
time.sleep(4)

# Keeps track of the current cursor location and the vehicle part we're installing
lastInstalledVPartData = CurrentVPartData()

# Load vehicle parts data from the most recent vch file
current_vch_file = get_vch_file(vch_file_name, True)
vehicle_parts_data = get_vch_data(current_vch_file)

# Listen for keys pressed, so the script can be stopped if ESCAPE is pressed
listener = keyboard.Listener(on_press=on_press)
listener.start()

# Stores the time spent since last
time_spent = 0
for vpd in vehicle_parts_data:
	for vehicle_row in range(len(vpd.vmap)):
		for vehicle_col in range(len(vpd.vmap[vehicle_row])):
			# If we spent enough in game time installing parts, we create the new vhc file and stop the script
			# Notice that the current part is the last installed part
			if time_spent > TIME_BEFORE_SCRIPT_STOP or exit_script:
				create_new_vhc_file(vehicle_parts_data)

			# if there's a X on the vmap, at this row and this column, install the part with the name "part_name"
			if vpd.vmap[vehicle_row][vehicle_col] == "X":
				installVehiclePart(vpd.part_name, vpd.needs_shape, vpd.estimated_time)
				time_spent += vpd.estimated_time

			if current_part_installed:
				# stores the last installed vehicle part data here, so that we have this info from anywhere in the script
				lastInstalledVPartData.row = vehicle_row
				lastInstalledVPartData.col = vehicle_col
				lastInstalledVPartData.part_name = vpd.part_name

			sendKey(Key.right)
		# next row!
		sendKey(Key.down)
		# after completing a row installation, move back to the first column
		for v in range(len(vpd.vmap[vehicle_row])):
			sendKey(Key.left)
	# after completing a vehicle part installation, move back to the first row
	for v in range(len(vpd.vmap)):
		sendKey(Key.up)

exit()