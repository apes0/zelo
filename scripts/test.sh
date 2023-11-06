#!/bin/bash

_DISPLAY=`echo $DISPLAY | awk '{print ":" strtonum(substr($1, 2)) + 1}'`
w=960
h=540
#Xnest -geometry 960x540 $_DISPLAY &
#Xephyr -screen 1280x720 $_DISPLAY &
# here ``+extension RANDR`` does nothing (altho randr support works i think) :/
#TODO: figure out how to do multiple monitors, without maybe faking them in the config
Xephyr +extension RANDR +xinerama -ac -br -screen $(($w*2))x$(echo $h) $_DISPLAY &
DISPLAY=$_DISPLAY
#sleep .5
#xrandr --setmonitor vl $(echo $w)/0x$(echo $h)/1+0+0 0
#xrandr --setmonitor vr $(echo $w)/1x$(echo $h)/1+$(echo $w)+0 null
##xrandr --fb $(($w*2))/$(($h+1)); xrandr --fb $(($w*2))/$(echo $h)
sleep .5

#setxkbmap -display $DISPLAY -print | xkbcomp - $_DISPLAY

progs=('glxgears' 'ulauncher' 'alacritty')

while [ true ]
do
    clear
    python3 main.py
#    [ $? == 1 ] && rm xcb_cffi.* 
#    echo opening profile
#    pgrep tuna | xargs kill -9
#    tuna program.prof &
    for prog in $progs
    do
        (kill -15 $(pgrep $prog) 2>&1) >/dev/null
    done
    (pgrep Xephyr 2>&1) >/dev/null || exit
#    echo enter to restart
#    read
done