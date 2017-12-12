Under Windows there is a simple pair of scripts for use before bed-time.

Sleep_in_ten.bat opens a Chrome window with a hard-coded Youtube stream
url that plays relaxing sounds 24/7. It calls brightness_control.ps1
with the parameter for dimming the display. It also initiates a 10-minute
countdown before it attempts to close the chrome window (by comparing
processes running before and after the script opens it) and go into Sleep
mode. The Youtube tab may not close if Chrome is already running at
execution, because Chrome tabs do not correspond exactly to unique PIDs.

brightness_control.ps1 simply exposes the wmiMonitorBrightNessMethods
class with two options (selected with the optional -Dim param): dim
monitor down to 0% or set monitor brightness to 70%. This script can be
used in a Windows Task Scheduler action to restore brightness to 70% on
startup by starting Powershell.exe with the following arguments:
-executionPolicy bypass -command "& {Start-Process PowerShell -ArgumentList '-ExecutionPolicy Bypass -Command ""C:\Example\Path\To\brightness_control.ps1""' -Verb RunAs}"
The nested powershell sessions are necessary because the Task Scheduler
'Start a Program' action uses the command prompt internally, and "We
can’t call the PowerShell script as admin from the command prompt, but we
can from PowerShell."
(Source: http://blog.danskingdom.com/tag/run-as-admin/)

Under Linux you will find the equivalent bash script. Should work on most
Ubuntu-like systems, definitely works on Linux Mint (14.04.1-Ubuntu),
with VGA compatible controller: Intel Corporation Haswell-ULT Integrated 
Graphics Controller (rev 0b)
