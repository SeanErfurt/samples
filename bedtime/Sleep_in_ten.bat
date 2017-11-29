@echo off
setlocal EnableDelayedExpansion
set "newPIDlist="
set "oldPIDlist=p"
::find old PIDs
for /f "TOKENS=1" %%a in ('wmic PROCESS where "Name='chrome.exe'" get ProcessID ^| findstr [0-9]') do (set "oldPIDlist=!oldPIDlist!%%ap")
::start preferred music
start chrome "https://www.youtube.com/watch?v=-zJfwr-SZgY"
::find new PIDs
for /f "TOKENS=1" %%a in ('wmic PROCESS where "Name='chrome.exe'" get ProcessID ^| findstr [0-9]') do (
if "!oldPIDlist:p%%ap=zz!"=="%oldPIDlist%" (set "newPIDlist=/PID %%a !newPIDlist!")
)
echo %newPIDlist%
::Initiate 10min countdown to sleep mode
C:\WINDOWS\system32\ps_tools\psshutdown.exe -d -t 600
::call PS script to dim brightness
::Note security work-around of starting an inner PowerShell process as Administrator (impossible from within cmd.exe)
powershell -executionPolicy bypass -command "& {Start-Process PowerShell -ArgumentList '-ExecutionPolicy Bypass -Command ""C:\Users\dragu_000\Documents\Misc\brightness_control.ps1 -Dim""' -Verb RunAs}";
::kill new tab process 10s before sleep
timeout /t 590 /nobreak >nul
taskkill /f %newPIDlist% /T > NUL 2>&1
