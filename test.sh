#!/bin/bash
DISPLAY=:0
Xephyr -screen 960x540 :1 &
sleep 1
DISPLAY=:1

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