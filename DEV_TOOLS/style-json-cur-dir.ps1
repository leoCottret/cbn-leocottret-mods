$files = Get-ChildItem -Recurse -Include *.json "." | Resolve-Path -Relative
$files | ForEach-Object { Invoke-Expression ".\json_formatter.exe $_" }
