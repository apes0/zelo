#!/usr/bin/zsh

mypath=${0:a:h}
export api="$mypath/../lib/api/"
generic="$mypath/../lib/backends/generic.py"

rm -r $api
mkdir $api

# generating code to generate code lol

(awk '
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
            print "[ -e " file " ] || echo \x27from ..backends.ffi import load\nfrom..backends.generic import *\nloaded = load(\"" import "\")\n\x27 > " file
            print "echo \x27" class ": type[" (start class) "] = loaded." class "\x27 >> " file;
        }
}
' $generic) | sh
