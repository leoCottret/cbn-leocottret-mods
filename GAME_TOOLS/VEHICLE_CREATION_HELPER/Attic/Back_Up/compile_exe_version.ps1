# This devops script will build the vch windows version, without any extra action needed
# If you don't have pyinstaller installed yet -> `pip3 install pyinstaller`
# Create exe from .py file
env:Path += "C:\Users\%USER%\AppData\Local\Programs\Python\"
pyinstaller --onefile -w '..\Python_Version\vch.py'
# Copy exe and relevant files
cp ".\dist\vch.exe" "..\Windows_Version\"
cp "..\Python_Version\vch_original.json" "..\Windows_Version\"
cp "..\Python_Version\options.json" "..\Windows_Version\"
# Remove tmp files from exe compilation
rm "vch.spec"
rm "dist" -Recurse
rm "build" -Recurse
# Remove useless files to have a clean release folder
rm "..\Windows_Version\vch_updated.json"
rm "..\Windows_Version\debug.txt"
