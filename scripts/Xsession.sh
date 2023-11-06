#!/bin/bash

mydir=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
cd $mydir

echo $mydir

path="/bin/zelo"

echo "#!/bin/bash
while [ true ]
do
	cd $(pwd)/..
    python3 main.py & disown
    cd ~
done" > $path

chmod +x $path

sudo cp ../zelo.desktop /usr/share/xsessions