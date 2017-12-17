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
echo "${OLDPIDS[*]}"
# open youtube music url
( chromium-browser --no-sandbox "https://www.youtube.com/watch?v=-zJfwr-SZgY" ) &
# Get chromium PIDs after new window/tab opens
sleep 1
declare -a NEWPIDS=(`pgrep chromium`)
echo "${NEWPIDS[*]}"

# Find new process id, if any
declare -a COPYNEW=("${NEWPIDS[@]}")
for ((i=0; i<${#NEWPIDS[@]}; i++)); do
	for j in "${OLDPIDS[@]}"; do
		if [[ ${NEWPIDS[$i]} == $j ]]; then
			unset COPYNEW[$i]
			break
		fi
	done
done

# Power off after ten minutes
sudo shutdown -P 10 &
# Wait almost 10 minutes, then attempt to close new chromium window/tab
sleep 595
if [ -z "$OLDPIDS" ]; then
	pkill --oldest chromium
elif [[ ${#COPYNEW[@]} -gt 0 ]]; then
	kill ${COPYNEW[*]}
fi
exit
