#!/usr/bin/zsh

mypath=${0:a:h}
cd $mypath

sudo apt install libxcb-util-dev libx11-xcb-dev libxcb-keysyms1-dev libxcb-image0-dev libxcb-randr0-dev libfontconfig-dev libpango1.0-dev libfreetype6-dev pkg-config python3
# add libxcb-ewmh-dev libxcb-icccm4-dev when we support them
pip3 install -r requirements.txt # TODO: install from apt if this doesn't work (or maybe event just install from apt?)


python3 -m lib.backends.ffi # compile everything

chmod +x ./keysyms.sh
zsh keysyms.sh # do we need to run this?

sudo ./Xsession.sh
# i think this is all?
