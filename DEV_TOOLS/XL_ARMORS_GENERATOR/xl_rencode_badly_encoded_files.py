# stolen from https://stackoverflow.com/questions/191359/how-to-convert-a-file-to-utf-8-in-python
# this is just a script to reencoded non UTF-8 encoded files
import os    
import pathlib
from chardet import detect

# get file encoding type
def get_encoding_type(file):
    with open(file, 'rb') as f:
        raw_data = f.read()
    return detect(raw_data)['encoding']



mods_folder_path = "C:/Games/CDDA_MODDING_BN_dummy/cdda/data/mods/"

every_mod_files = pathlib.Path(mods_folder_path).glob('**/*.json')


for mod_file in every_mod_files:
	src_file = mod_file

	trg_file = f"C:\Games\CDDA_MODDING_BN_dummy\cdda\whatever.json"

	from_codec = get_encoding_type(src_file)

	# add try: except block for reliability
	try: 
	    with open(src_file, 'r', encoding=from_codec) as f, open(trg_file, 'w', encoding='utf-8') as e:
	        text = f.read() # for small files, for big use chunks
	        e.write(text)

	    os.remove(src_file) # remove old encoding file
	    os.rename(trg_file, src_file) # rename new encoding
	except UnicodeDecodeError:
	    print('Decode Error ' + str(src_file) )
	except UnicodeEncodeError:
	    print('Encode Error' + str(src_file) )