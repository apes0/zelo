#!/bin/sh

# idk how good this

git stash
git pull
git stash pop

grep -lr '<<<<<<<' . | xargs git checkout --theirs

rm xcb_cffi.*