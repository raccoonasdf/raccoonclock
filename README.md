raccoonclock
------------

this is a reference implementation for [a calendar specification](https://www.raccoon.fun/calendar.html) that i wrote for fun. it might be a little messy and unstable inside, i wrote it hastily and it's my first time using skyfield :)

you need some python packages first: `pip install -r requirements.txt`

on first run, `raccoonclock.toml` will be generated. edit it to set your desired coordinates.

on second run, the ephemeris will be downloaded to your cache directory before output will be displayed. this only happens once.

the first line of output includes
- the TIME
- the "NEGATIVE TIME" (time until the clock resets)
- the DAY
- the HALF
- the QUART in its absolute format, its relative format from both hemispheres, and its oldstyle format

the second and third line are the amount of time until nautical and astronomical twilight, respectively. the second line also reduplicates the DAY, HALF, and QUART in ASCII mode.

the fourth line includes
- the ALTITUDE of the sun in the sky
- the DAY PHASE (nighttime, astronomical twilight, nautical twilight, civil twilight, daytime)


example output:
```
[ ☉ 00:05:13 ☽ -08:59:45 ] 1☉  ○○/□🜄🜃/○🜂🜁/♅
 n. twilight ☉ -09:31:43   1r. S./N.f./S.n./os. 
 a. twilight ☉ -10:07:10
000° 00' (daytime)
```