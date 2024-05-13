#!/bin/zsh

mypath=${0:a:h}
cd "$mypath/.."
# idk how good this

git fetch

files=$(git diff --name-only | grep -Po 'lib/backends/ffi/\K([^/])*/.*' | grep -o '^[^/]*')

for file in $files
do
    find  . -name $file"_cffi.*" -exec rm {} \;
done

git add *
git stash
git pull
git stash pop

# here we do this so that the update script doesnt override itself lol
grep -lr '<<<<''<<<' . | xargs git checkout --theirs

git submodule update --init --recursive

python3 -m lib.backends.ffi # compile everything that was changed