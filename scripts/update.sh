#!/bin/zsh

mypath=${0:a:h}
cd $mypath

# idk how good this

git add *

git fetch

files=$(git diff --name-only | grep -Po 'lib/backends/ffi/\K([^/])*/.*' | grep -o '^[^/]*')

for file in $files
do
    find  . -name $file"_cffi.*" -exec rm {} \;
done

git stash
git merge
git stash pop

grep -lr '<<<<<<<' . | xargs git checkout --theirs

cd ..
python3 -m lib.backends.ffi # compile everything that was changed