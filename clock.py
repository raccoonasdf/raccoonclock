from datetime import timedelta
from math import modf
from typing import Optional
from skyfield.searchlib import find_discrete
from skyfield.timelib import Time
from skyfield.units import Angle
import numpy as np

from observer import Observer, Planet


DAY_PHASE = {
    0: 'nighttime',
    1: 'astronomical twilight',
    2: 'nautical twilight',
    3: 'civil twilight',
    4: 'daytime'
}

HALF = {
    0: '☉',
    1: '☽'
}

ASCII_HALF = {
    0: 'r.',
    1: 's.'
}

QUARTER = {
    0: '○□/□🜄🜁/○🜂🜃/♇',
    1: '□□/□🜂🜁/○🜄🜃/♆',
    2: '□○/□🜂🜃/○🜄🜁/⊕',
    3: '○○/□🜄🜃/○🜂🜁/♅',
}

ASCII_QUARTER = {
    0: 'SN./N.mn./S.mf./pn.',
    1: 'N./N.n./S.f./ne.',
    2: 'NS./N.mf./S.mn./ta.',
    3: 'S./N.f./S.n./os.'
}


class RelativeTime:
    def __init__(self, daylight: bool, then: Time, now: Time):
        self.daylight = daylight
        self.then = then
        self.now = now
    
    def update(self, now: Time) -> bool:
        old_polarity = self.then - self.now < 0
        self.now = now
        new_polarity = self.then - self.now < 0
        return bool(old_polarity != new_polarity)

    def __str__(self) -> str:
        then = self.then.utc_datetime()
        now = self.now.utc_datetime()
        if now > then:
            sign = ''
            delta = now - then
        else:
            sign = '-'
            delta = then - now

        half = '☉' if self.daylight else '☽'
        minutes, seconds = divmod(delta.seconds, 60)
        hours, minutes = divmod(minutes, 60)

        return f'{half} {sign}{hours:02}:{minutes:02}:{seconds:02}'


class DayPhase:
    def __init__(self, phase: int):
        self.phase = phase

    def __str__(self) -> str:
        return DAY_PHASE[self.phase]


class Date:
    def __init__(self, eighth: int, day: int):
        self.eighth = eighth
        self.day = day

    def show(self, ascii: bool = False) -> str:
        half = ASCII_HALF if ascii else HALF
        quarter = ASCII_QUARTER if ascii else QUARTER
        spacer = ' ' if ascii else '  '

        return f'{self.day}{half[self.eighth%2]}{spacer}{quarter[self.eighth//2]}'

    def __str__(self) -> str:
        return self.show()


class Altitude:
    def __init__(self, angle: Angle):
        self.angle = angle

        degrees = self.angle.degrees
        minutes, whole_degrees = modf(degrees)
        self.degrees = int(whole_degrees)

        minutes = abs(minutes)*60
        seconds, minutes = modf(minutes)
        self.minutes = int(minutes)

        self.seconds = int(seconds*60)
    
    def show(self, minutes: bool = True, seconds: bool = True) -> str:
        res = f'{self.degrees:03}°'
        if minutes:
            res += f" {self.minutes:02}'"
        if seconds:
            res += f' {self.seconds:02}"'

        return res

    def __str__(self) -> str:
        return self.show()


class Clock:
    def __init__(self, observer: Observer):
        self.observer = observer

    def _since_until(self, since: bool, time: Optional[Time] = None, phase: int = 4) -> RelativeTime:
        time = self.observer.or_now(time)
        ts = self.observer.ts

        now_dt = time.utc_datetime()
        then_dt = now_dt - timedelta(hours=28) if since else now_dt + \
            timedelta(hours=28)

        now = ts.utc(now_dt)
        then = ts.utc(then_dt)

        lesser, greater = (then, now) if since else (now, then)
        idx = -1 if since else 0

        half_times, halves = find_discrete(
            lesser, greater, self.observer.day_phase_func(phase))
        half_time, half = half_times[idx], halves[idx]

        return RelativeTime(half, half_time, now)

    def since(self, time: Optional[Time] = None, phase: int = 4) -> RelativeTime:
        return self._since_until(True, time, phase)

    def until(self, time: Optional[Time] = None, phase: int = 4) -> RelativeTime:
        return self._since_until(False, time, phase)

    def day_phase(self, time: Optional[Time] = None) -> DayPhase:
        return DayPhase(int(self.observer.which_day_phase_func()(time)))

    def date(self, time: Optional[Time] = None) -> Date:
        time = self.observer.or_now(time)
        ts = self.observer.ts

        segment_at = self.observer.segment_func(8)
        daytime_at = self.observer.day_phase_func(4)

        eighth = segment_at(time)

        now_dt = time.utc_datetime()
        # MAGIC: segments can be overlong, a day should be enough leeway?
        then_dt = now_dt - timedelta(days=int(segment_at.step_days) + 1)

        now = ts.utc(now_dt)
        then = ts.utc(then_dt)

        then = find_discrete(then, now, segment_at)[0][-1]

        day = sum(find_discrete(then, now, daytime_at)[1])

        return Date(int(eighth), day)

    def altitude(self, time: Optional[Time] = None) -> Altitude:
        return Altitude(self.observer.observe(Planet.SUN, time).altaz()[0])
