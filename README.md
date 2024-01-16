raccoonclock
------------

this is a reference implementation for [a calendar specification](https://www.raccoon.fun/calendar.html) that i wrote for fun. it might be a little messy and unstable inside, i wrote it hastily and it's my first time using skyfield :)

you need the python packages `skyfield`, `blessed`, and `xdg-base-dirs`.

on first run, `raccoonclock.toml` will be generated. edit it to set your desired coordinates.

on second run, the ephemeris will be downloaded to your cache directory before output will be displayed. this only happens once.

the first line of output includes
- the TIME
- the "NEGATIVE TIME" (time until the clock resets)
- the DAY
- the HALF
- the QUART in its absolute format, its relative format from both hemispheres, and its oldstyle format

the second and third line are the amount of time until nautical and astronomical twilight, respectively

the fourth line includes
- the ALTITUDE of the sun in the sky
- the DAY PHASE (nighttime, astronomical twilight, nautical twilight, civil twilight, daytime)