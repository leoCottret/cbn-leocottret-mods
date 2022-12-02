# Was used to lint the vch_updated.json file, but I now use a custom native python solution instead
$files = Get-ChildItem -Recurse -Include vch_updated.json "../Python_Version/" | Resolve-Path -Relative
$files | ForEach-Object { Invoke-Expression "..\..\..\DEV_TOOLS\XL_ARMORS_GENERATOR\json_formatter.exe $_" }
