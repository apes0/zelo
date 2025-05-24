#!/usr/bin/zsh

timeout 20 git submodule update --init --recursive --depth=1 || (
echo 'anongit timed out'

# sometimes anongit is down lol, pia implemented a fix for this, so im copying it :)
# https://github.com/pia-foss/desktop-dep-build/blob/master/anongit-freedesktop-org-is-down.sh

for config in .git/modules/libxcb-*/config; do
    echo "editing $config"
    git config --file="$config" submodule.m4.url "https://gitlab.freedesktop.org/xorg/util/xcb-util-m4.git"
done

git submodule update --init --recursive --depth=1
)


mypath=${0:a:h}
cd $mypath

sudo apt install -y libxcb-util-dev libx11-xcb-dev libxcb-keysyms1-dev libxcb-image0-dev libxcb-randr0-dev libxcb-icccm4-dev libfontconfig-dev libpango1.0-dev libfreetype6-dev libxcb-xtest0-dev pkg-config python3 build-essential libdbus-glib-1-dev libgirepository1.0-dev xutils-dev xcb-proto libtool autoconf libxcb-xinerama0-dev
# TODO: does python3-dev work independent of the python version?
# add libxcb-ewmh-dev when we support it
# same for libxcb-xinput-dev

cd ..
pip3 install -r requirements.txt # TODO: install from apt if this doesn't work (or maybe event just install from apt?)

cd libxcb-errors
./autogen.sh
sudo make install
sudo ldconfig # see: https://stackoverflow.com/questions/65366236/error-while-loading-shared-libraries-libxcb-errors-so-0-cannot-open-shared-obj
# and: https://stackoverflow.com/questions/480764/linux-error-while-loading-shared-libraries-cannot-open-shared-object-file-no-s

cd ..

python3 -m lib.backends.ffi # compile everything

cd $mypath

chmod +x ./keysyms.sh
zsh keysyms.sh # do we need to run this?

sudo ./Xsession.sh
# i think this is all?
