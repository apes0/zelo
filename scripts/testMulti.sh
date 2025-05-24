#!/bin/bash

w=960
h=540

args="+xinerama -ac -br"
_DISPLAY=:$(for i in {0..10}; do [ -e "/tmp/.X11-unix/X$i" ] || break; done; echo $i)

for _ in {0..2}
do
    # TODO: fix keymaps
    Xephyr +xinerama -ac -br -screen $(echo $w)x$(echo $h) -xkb-rules evdev -xkb-model pc105 -xkb-layout us $_DISPLAY &
    args="$args -display $_DISPLAY -input $_DISPLAY"
    inotifywait --timeout 2 /tmp/.X11-unix/
    # xkbcomp $DISPLAY $_DISPLAY
    _DISPLAY=`echo $_DISPLAY | awk '{print ":" strtonum(substr($1, 2)) + 1}'`
done

Xdmx $args $_DISPLAY 2>/dev/null &

DISPLAY=$_DISPLAY

inotifywait --timeout 2 /tmp/.X11-unix/

progs=('glxgears' 'ulauncher' 'alacritty')

while [ true ]
do
#    clear
    echo
    echo starting new session
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
    sleep 2.5
#    echo enter to restart
#    read
done
