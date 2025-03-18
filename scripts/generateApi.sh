#!/usr/bin/zsh

mypath=${0:a:h}
old=$(pwd)
cd $mypath
export api="../lib/api/"
generic="../lib/backends/generic.py"
backends="../lib/backends/"

rm -r $api
mkdir $api

# generating code to generate code lol

a=$(gawk '
{
    start="G"
    if (match($1, "#"))
        {
            import=$2;
        }

    if (match($1, "class") && match($2, start))
        {
            class=substr($2, length(start) + 1)
            class=substr(class, 0, length(class) - 1) # remove the :
            file=(ENVIRON["api"] import ".py")
            print "[ -e " file " ] || echo \x27from ..backends.ffi import load\nfrom ..backends.generic import *\n\nloaded = load(\"" import "\")\n\x27 > " file
            print "echo \x27" class ": type[" (start class) "] = loaded." class "\x27 >> " file
            print "echo \"# sources:\" >> " file
            print "ls " ENVIRON["backends"] "*/" import ".py | sed \"s/\\.py//g;s/\\.//g;s/^\\///g;s/\\//\\./g\;s/.*/#&/\" >> " file
        }
}
' $generic)

echo running $a
echo $a | sh
cd $old