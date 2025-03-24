#!/bin/zsh

echo running as $(whoami)

if [ $1 ]
then
    PYTHONPATH=$1
else
    PYTHONPATH=$(python3 -m pip show trio 2>/dev/null | grep -Po 'Location:[^\/]*\K(\/.*)')
fi

echo PYTHONPATH is $PYTHONPATH

# https://superuser.com/a/1577212
if [ "$(id -u)" != 0 ]
then
    echo "becoming root"
    sudo $0 $PYTHONPATH # make sure that we become root (and keep the PYTHONPATH)
    exit 1
fi

n="${$(cat /sys/class/tty/tty0/active):3}"

chvt $(($n + 1))

# NOTE: this is basically a minimal copy of startx

client='/usr/bin/xterm'
clientargs='-e /bin/sh /tmp/test.sh'
server='/usr/bin/X'
serverargs="vt$(($n + 1)) -quiet"

DISPLAY=0
while true ; do
    [ -e "/tmp/.X$DISPLAY-lock" -o -S "/tmp/.X11-unix/X$DISPLAY" ] || break
    DISPLAY=$(($DISPLAY + 1))
done

mypath=${0:a:h}

# xauth bs
xauth=$(timeout 2 bash -c "xauth info | grep -Po '[^\/]*\K(\/.*)'")
# in case xauth stops working, we will save everything we need for subsequent runs in a file in /tmp
[ $xauth ] && (cp $xauth /tmp/xauth; echo $xauth > /tmp/xauthpath) || xauth=$(cat /tmp/xauthpath)

echo xauth file is $xauth

echo "
cd $mypath/..
PYTHONPATH=$PYTHONPATH python3 main.py > /dev/null &
xterm &
while [ 1 ]
do
    sleep 1000000000000
done
" > /tmp/test.sh
chmod +x /tmp/test.sh


startx $client "$clientargs" -- $server :$DISPLAY "$serverargs"

# recover the xauth magic
cp /tmp/xauth $xauth
chmod 777 $xauth

chvt $n