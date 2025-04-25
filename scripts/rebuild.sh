# rebuild all cffi modules

rm lib/backends/build/*cffi.*
python3 -m lib.backends.ffi
python3 scripts/genTypes.py
