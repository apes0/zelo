# rebuild all cffi modules

rm *cffi.*
python3 -m lib.backends.ffi
python3 scripts/genTypes.py
