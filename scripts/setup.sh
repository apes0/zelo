#!/usr/bin/zsh

git submodule update --init --recursive

mypath=${0:a:h}
cd $mypath

sudo apt install -y libxcb-util-dev libx11-xcb-dev libxcb-keysyms1-dev libxcb-image0-dev libxcb-randr0-dev libfontconfig-dev libpango1.0-dev libfreetype6-dev libxcb-xtest0-dev pkg-config python3 build-essential libdbus-glib-1-dev libgirepository1.0-dev xutils-dev xcb-proto
# add libxcb-ewmh-dev libxcb-icccm4-dev when we support them
# same for libxcb-xinput-dev

cd ..
pip3 install -r requirements.txt # TODO: install from apt if this doesn't work (or maybe event just install from apt?)

cd libxcb-errors
./autogen.sh
sudo make install
sudo ldconfig # see: https://stackoverflow.com/questions/65366236/error-while-loading-shared-libraries-libxcb-errors-so-0-cannot-open-shared-obj
# and: https://stackoverflow.com/questions/480764/linux-error-while-loading-shared-libraries-cannot-open-shared-object-file-no-s

python3 -m lib.backends.ffi # compile everything

cd $mypath

chmod +x ./keysyms.sh
zsh keysyms.sh # do we need to run this?

sudo ./Xsession.sh
# i think this is all?
