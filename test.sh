#!/bin/bash
DISPLAY=:1
Xephyr -screen 920x540 :2 &
sleep 1
DISPLAY=:2

progs=('glxgears' 'ulauncher' 'alacritty')

while [ true ]
do
    python3 main.py
    echo restarting
    for prog in $progs
    do
        (kill -15 $(pgrep $prog) 2>&1) >/dev/null
    done
    (pgrep Xephyr 2>&1) >/dev/null || exit
done