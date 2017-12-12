#!/bin/bash

# find the brightness file on this system
# see: https://askubuntu.com/questions/57236/unable-to-change-brightness-in-a-lenovo-laptop
BRIGHTFILE=`ls /sys/class/backlight/*/brightness`

# get current brightness
BRIGHTVAL=`cat $BRIGHTFILE`
# set to very dim
echo 1 | sudo tee $BRIGHTFILE

# Tell crontab to set brightness back to previous brightness on startup
# see: https://stackoverflow.com/questions/878600/how-to-create-a-cron-job-using-bash-automatically-without-the-interactive-editor
CRONCMD="@reboot echo $BRIGHTVAL | sudo tee $BRIGHTFILE"
( crontab -l 2> /dev/null | grep -v -F "$CRONCMD" ; echo "$CRONCMD" ) | crontab -

# Get chromium PIDs
declare -a OLDPIDS=(`pgrep chromium`)
# open youtube music url
sudo chromium-browser --no-sandbox "https://www.youtube.com/watch?v=-zJfwr-SZgY"
# Get chromium PIDs after new window/tab opens
declare -a NEWPIDS=(`pgrep chromium`)

# Find new process id, if any
let NEWPID=-1
for i in "${NEWPIDS[@]}"; do
	for j in "${OLDPIDS[@]}"; do
		if [[ $i == $j ]]; then
			NEWPID=$j
			break
		fi
	done
done

# Power off after ten minutes
sudo shutdown -P 10
# Wait almost 10 minutes, then attempt to close new chromium window/tab
sleep 595
if [ -z "$OLDPIDS" ]; then
	pkill chromium
elif [[ $NEWPID -gt 0 ]]; then
	kill $NEWPID
fi
