# I mainly use this script to check the text recognition part of vch.py
import PIL.ImageGrab
from PIL import Image
import pytesseract
import time
import math


# take a screenshot of the screen
CURRENT_SCREENSHOT = PIL.ImageGrab.grab()

# Increment an index, and create one if it doesn't exist yet
def incrementCharFrequency(llist, char):
	try:
		llist[char] = llist[char]
		llist[char] += 1
	except KeyError:
		llist[char] = 1

# Return the value from a dictionnary at this index if it exists, otherwise return 0
def getValue(dicti, index):
	try:
		return dicti[index]
	except KeyError:
		return 0

# Return the frequencies of all characters in the string
def getCharacterFrequencies(text):
	frequencies = {}
	for char in text:
		incrementCharFrequency(frequencies, char)
	return frequencies

# Check if character frequencies are roughly similar, meaning that their differencies are below max_diff_allowed
def areFrequenciesRoughlySimilar(freq_1, freq_2, max_diff_allowed):
	# Store character differencies between text and line
	character_differencies_count = 0
	for char in freq_1:
		if abs(getValue(freq_1, char) - getValue(freq_2, char)) != 0:
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
	return (misplaced_character_count >= len(text)/2)

# Check if there is one of the texts on the screen, in the delimited borders given
def checkIfTextsAreOnScreenLocation(texts, left, top, right, bottom, do_update, threshold=10, use_psm=False):
	global CURRENT_SCREENSHOT
	# Update last screenshot of the screen
	if do_update:
		updateScreenshot(threshold)
	# Get img in delimited borders
	cropped_img = CURRENT_SCREENSHOT.crop((left, top, right, bottom))	
	# Get lines in cropped image. 
	# The line below is by far the most computing heavy of the script, which is why I changed this current function to accept an array of texts
	lines = None
	if not use_psm:
		lines = pytesseract.image_to_string(cropped_img).split("\n")
	else:
		lines = pytesseract.image_to_string(cropped_img, config='--psm 6').split("\n")

	# Iterate through all of the texts, then the lines
	for text in texts:
		# Compute character frequencies of text
		text_frequencies = getCharacterFrequencies(text)
		# Maximum difference allowed between line and text
		# The longer the text, the more errors are allowed
		max_diff_allowed = (math.floor(len(text)/10) + 2) if (len(text) > 5) else 0
		print(lines)
		for line in lines:
			print(line)
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
				line_frequencies = getCharacterFrequencies(subline)

				if areFrequenciesRoughlySimilar(text_frequencies, line_frequencies, max_diff_allowed) and areFrequenciesRoughlySimilar(line_frequencies, text_frequencies, max_diff_allowed):
					# We check if subline is not roughly an anagram of text. Can be the case for short words
					if not too_many_misplaced_characters(text, subline, max(max_diff_allowed, 1)):
						return True
				start_char_nb += 1
				end_char_nb += 1
	return False


# Update stored screenshot of the screen, and convert it to a b&w version
# Original code from https://stackoverflow.com/questions/9506841/using-pil-to-turn-a-rgb-image-into-a-pure-black-and-white-image#9506960
# The basic idea:
# 1)
# In a colored pictured, each pixel stores a "RGB" value, so each pixel color is defined by 3 values (Red, Green, Blue)
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
def updateScreenshot(threshold=70, reverse=True):
	global CURRENT_SCREENSHOT
	fn = None
	if reverse:
		fn = lambda x : 0 if x > threshold else 255
	else:
		fn = lambda x : 255 if x > threshold else 0

	CURRENT_SCREENSHOT = PIL.ImageGrab.grab().convert('L').point(fn, mode='1').convert('1')
	# CURRENT_SCREENSHOT.show() # Uncomment here and below to see the resulting image for the text recognition
	# exit()


# Display the cropped img from screenshot in borders
# I use it as a debug function, to see what part of the screen will be used
def display_cropped_img(left, top, right, bottom, threshold):
	global CURRENT_SCREENSHOT
	updateScreenshot(threshold)
	# Get img in delimited borders
	cropped_img = CURRENT_SCREENSHOT.crop((left, top, right, bottom))
	cropped_img.show()
	exit()


# --- MAIN ---
time.sleep(2)
updateScreenshot()
# display image
# display_cropped_img(0, CURRENT_SCREENSHOT.height/3, CURRENT_SCREENSHOT.width/4, CURRENT_SCREENSHOT.height-165, 120)



txt_to_test = [ "aisle" ]
try_psm: bool = True
for i in range(1):
	if checkIfTextsAreOnScreenLocation(txt_to_test, CURRENT_SCREENSHOT.width/3, 0, 2*CURRENT_SCREENSHOT.width/3, CURRENT_SCREENSHOT.height/2, True, 230):
		print(f"is on screen in delimited borders")
	else:
		print(f"is NOT on screen in delimited borders")




# Check if we're on the install vehicle part screen
# checkIfTextIsOnScreenLocation("Name: The Game Plays Itsel (Your Followers)", 0, CURRENT_SCREENSHOT.height/2, CURRENT_SCREENSHOT.width/2, CURRENT_SCREENSHOT.height)
# Check if the part needs a shape to be selected
# checkIfTextIsOnScreenLocation("Choose shape", CURRENT_SCREENSHOT.width/3, 0, 2*CURRENT_SCREENSHOT.width/3, CURRENT_SCREENSHOT.height/4)
# Check for installed part
# checkIfTextIsOnScreenLocation("seat", 0, CURRENT_SCREENSHOT.height/3, CURRENT_SCREENSHOT.width/4, CURRENT_SCREENSHOT.height)
# Check "Use which component?"