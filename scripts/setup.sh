sudo apt install libxcb-util-dev libx11-xcb-dev libxcb-keysyms1-dev libxcb-image0-dev python3
# add libxcb-ewmh-dev libxcb-icccm4-dev when we support them
pip3 install -r requirements.txt
./keysyms.sh
# i think this is all?