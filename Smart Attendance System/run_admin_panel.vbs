Set WshShell = CreateObject("WScript.Shell")
strPath = WshShell.CurrentDirectory
' Run the python script with python command to ensure it runs with interpreter
' The 0 at the end hides the console window
WshShell.Run "python " & chr(34) & strPath & "\desktop_app\main.py" & chr(34), 0
Set WshShell = Nothing
