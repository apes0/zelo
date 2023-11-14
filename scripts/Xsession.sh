#!/bin/bash

mydir=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
cd $mydir

echo $mydir

path="/bin/zelo"

file="#!/bin/bash
while [ true ]
do
    cd /home/$(whoami)
    python3 $(pwd)/../main.py
done"

sudo sh -c "echo \"$file\" > $path"

sudo chmod +x $path

sudo cp ../zelo.desktop /usr/share/xsessions
