#!/usr/bin/env python3

from argparse import ArgumentParser
from pathlib import Path
from typing import Optional
from dateutil.parser import isoparse
import sys
import time
from blessed import Terminal
from skyfield.iokit import Loader
from skyfield.jpllib import SpiceKernel
from skyfield.timelib import Time
import toml
from xdg_base_dirs import xdg_config_home, xdg_cache_home

from clock import Clock
from observer import Observer

def existing_path(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path

def make_default_config_location() -> Path:
    path = existing_path(xdg_config_home()/'raccoonclock')
    return path/'raccoonclock.toml'


parser = ArgumentParser(description='raccoonclock')
parser.add_argument('date', nargs='?', help='ISO datetime')
parser.add_argument('--config', default=make_default_config_location(), help='location of the config file')
args = parser.parse_args()

try:
    config = toml.load(args.config)
except FileNotFoundError:
    with open(args.config, 'w') as f:
        toml.dump({
            'ephemeris': 'de423',
            'observer': {
                'latitude': '42.0303 N',
                'longitude': '87.9123 W'
            }}, f)
        print(f'edit newly created config and rerun: {args.config}')
        sys.exit(1)

term = Terminal()


def interpret_coords(latlon: tuple[str, str]) -> tuple[float, float]:
    def coord_str_to_float(coord_str: str, pos_suffix: str, neg_suffix: str) -> float:
        try:
            coord_str_unsuffixed = coord_str[:-1]

            # throws ValueError
            coord = float(coord_str_unsuffixed)
            # throws IndexError
            suffix = coord_str[-1]

            if suffix == pos_suffix:
                pass
            elif suffix == neg_suffix:
                coord = -coord
            else:
                raise ValueError
        except (ValueError, IndexError):
            raise ValueError(f'invalid coordinate string: "{coord_str}"')

        return coord

    return (coord_str_to_float(latlon[0], 'N', 'S'),
            coord_str_to_float(latlon[1], 'E', 'W'))

load = Loader(existing_path(xdg_cache_home()/'raccoonclock'))

ephemeris = load(f"{config['ephemeris']}.bsp")
if not isinstance(ephemeris, SpiceKernel):
    raise ValueError(f'invalid ephemeris: "{ephemeris}.bsp"')
    
observer = Observer(ephemeris, load.timescale(),
                    interpret_coords((config['observer']['latitude'], config['observer']['longitude'])))

clock = Clock(observer)


class ClockDisplay:
    def __init__(self):
        self.last_update = None

        # avoid computing initial values until needed
        class FakeRelativeTime:
            def update(_) -> bool:
                return True

        self.since = FakeRelativeTime
        self.until = FakeRelativeTime
        self.date = FakeRelativeTime

        self.until_nautical_twilight = FakeRelativeTime
        self.until_astronomical_twilight = FakeRelativeTime

        self.day_phase = None

    def show(self, time: Optional[Time] = None):
        time = clock.observer.or_now(time)

        if self.last_update is None or time - self.last_update >= 0.000005:
            self.last_update = time

            if self.since.update(time):
                self.since = clock.since(time)

            if self.until.update(time):
                self.until = clock.until(time)

            new_phase = False

            if self.until_nautical_twilight.update(time):
                self.until_nautical_twilight = clock.until(time, 2)
                new_phase = True
        
            if self.until_astronomical_twilight.update(time):
                self.until_astronomical_twilight = clock.until(time, 1)
                new_phase = True
        
            if self.day_phase is None or new_phase:
                self.date = clock.date(time)
                self.day_phase = clock.day_phase(time)


            self.altitude = clock.altitude(time)

        def clear_and_print(value=''):
            print(f'{term.clear_eol()}{value}')

        clear_and_print()
        clear_and_print()
        clear_and_print(f'  [ {self.since} {self.until} ] {self.date}')
        clear_and_print(f'   n. twilight {self.until_nautical_twilight}   {self.date.show(ascii=True)}')
        clear_and_print(f'   a. twilight {self.until_astronomical_twilight}')
        clear_and_print(f'  {self.altitude.show(seconds=False)} ({self.day_phase})')


clock_display = ClockDisplay()

if args.date:
    try:
        date = isoparse(args.date)
    except ValueError:
        print('invalid datetime')
        sys.exit(1)
    if date.tzinfo is None:
        print('time needs timezone')
        sys.exit(1)

    clock_display.show(observer.ts.utc(date))
else:
    try:
        while True:
            with term.location():
                clock_display.show()
            time.sleep(0.1)
    except (KeyboardInterrupt, EOFError):
        pass
