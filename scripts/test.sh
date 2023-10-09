#!/bin/bash

_DISPLAY=`echo $DISPLAY | awk '{print ":" strtonum(substr($1, 2)) + 1}'`
#Xnest -geometry 960x540 $_DISPLAY &
#Xephyr -screen 1280x720 $_DISPLAY &
Xephyr +extension RANDR +xinerama -screen 960x540 -screen 960x540 -ac $_DISPLAY &
sleep 1
#setxkbmap -display $DISPLAY -print | xkbcomp - $_DISPLAY
DISPLAY=$_DISPLAY

progs=('glxgears' 'ulauncher' 'alacritty')

while [ true ]
do
    clear
    python3 main.py
#    echo opening profile
#    pgrep tuna | xargs kill -9
#    tuna program.prof &
    for prog in $progs
    do
        (kill -15 $(pgrep $prog) 2>&1) >/dev/null
    done
    (pgrep Xephyr 2>&1) >/dev/null || exit
    echo enter to restart
    read
done