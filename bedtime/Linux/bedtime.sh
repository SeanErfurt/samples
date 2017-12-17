#!/bin/bash

# find the brightness file on this system
# see: https://askubuntu.com/questions/57236/unable-to-change-brightness-in-a-lenovo-laptop
BRIGHTFILE=`ls /sys/class/backlight/*/brightness`

# get current brightness
BRIGHTVAL=`cat $BRIGHTFILE`
# set to very dim
echo 1 | sudo tee $BRIGHTFILE > /dev/null

# Tell crontab to set brightness back to previous brightness on startup
# see: https://stackoverflow.com/questions/878600/how-to-create-a-cron-job-using-bash-automatically-without-the-interactive-editor
SUBSTRING="sudo tee $BRIGHTFILE"
CRONCMD="@reboot echo $BRIGHTVAL | sudo tee $BRIGHTFILE"
( crontab -l 2> /dev/null | grep -v -F "$SUBSTRING" ; echo "$CRONCMD" ) | crontab -

# open music url in $1 (default is youtube relaxing music)
# using new profile "system" to avoid messing with the default profile's startup
# will prompt you with profile manager on first run, create new profile named "system"
if [ "$1" == "" ]; then
	( firefox --new-window "https://www.youtube.com/watch?v=-zJfwr-SZgY" -P system) &>/dev/null &
else
	( firefox --new-window "$1" -P system) &>/dev/null &
fi

# Power off after ten minutes
sudo shutdown -P 10 &
# Wait almost 10 minutes, then close new firefox window (assuming user hasn't changed active window)
sleep 595
wmctrl -c :ACTIVE:
