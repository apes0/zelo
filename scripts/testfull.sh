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
    sudo $0 $PYTHONPATH $(whoami) # make sure that we become root (and keep the PYTHONPATH and user)
    exit 1
fi

n="${$(cat /sys/class/tty/tty0/active):3}"

chvt $(($n + 1))

# NOTE: this is basically a minimal copy of startx

client='/usr/bin/xterm'
clientargs='-font lucidasanstypewriter-24 -bg black -fg white -e /bin/sh /tmp/test.sh'
server='/usr/bin/X'
serverargs="vt$(($n + 1)) -quiet"

DISPLAY=0
while true ; do
    [ -e "/tmp/.X$DISPLAY-lock" -o -S "/tmp/.X11-unix/X$DISPLAY" ] || break
    DISPLAY=$(($DISPLAY + 1))
done

mypath=${0:a:h}

# xauth bs
xauth=$(timeout 2 bash -c "xauth -i info | grep -Po '[^\/]*\K(\/.*)'")
# in case xauth stops working, we will save everything we need for subsequent runs in a file in /tmp
[ $xauth ] && (cp $xauth /tmp/xauth; echo $xauth > /tmp/xauthpath) || xauth=$(cat /tmp/xauthpath)

echo xauth file is $xauth

# add xauth stuff

mcookie=`/usr/bin/mcookie`
echo magic cookie is $mcookie
authfile=`mktemp --tmpdir serverauth.XXXXXXXXXX`
echo new xauth file is $authfile

serverargs=${serverargs}" -auth "${authfile}

echo "
# apply the xauth magic now that we have a running server
xhost +local:
chmod 777 $authfile

for add in :$DISPLAY $(uname -n):$DISPLAY
do
    echo adding \$add
    xauth -i -q -f $authfile << EOF
add \$add . $mcookie
EOF
    chmod 777 $authfile
done

cd $mypath/..
PYTHONPATH=$PYTHONPATH python3 main.py > /dev/null &
xterm -font lucidasanstypewriter-24 -bg black -fg white -e 'su $2' &
while [ 1 ]
do
    sleep 1000000000000
done
" > /tmp/test.sh
chmod +x /tmp/test.sh

echo starting X with args $serverargs
startx $client "$clientargs" -- $server :$DISPLAY "$serverargs"

# remove our auth file
rm $authfile

# recover the xauth magic
cp /tmp/xauth $xauth
chmod 777 $xauth

chvt $n