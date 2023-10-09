#!/usr/bin/zsh

keysymdef=$(cpp <(echo "#include <X11/keysymdef.h>") | grep -o '\/.*X11\/keysymdef.h')
# ^ cpp returns an empty file for some reason here, so you cannot just use its result

mypath=${0:a:h}
file="$mypath/../lib/backends/x11/keysyms.py"

awk '
BEGIN {
    print "keys = {"
}
{
    start="XK_"
    if (match($2, start) && match($3, "0x")) 
        {print "\t\x27" tolower(substr($2, length(start) + 1)) "\x27: " $3 ","}
}
END {
    print "}"
}' $keysymdef > $file
