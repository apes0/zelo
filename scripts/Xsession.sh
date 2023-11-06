#!/bin/bash

mydir=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
cd $mydir

echo $mydir

path="/bin/zelo"

echo "#!/bin/bash
cd $(pwd)/..
while [ true ]
do
    python3 main.py
done" > $path

chmod +x $path

sudo cp ../zelo.desktop /usr/share/xsessions