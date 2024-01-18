from collections.abc import Callable
from enum import Enum
from typing import Any, Generic, Optional, TypeVar
import numpy as np
import numpy.typing as npt
from skyfield.constants import tau
from skyfield.framelib import ecliptic_frame
from skyfield.nutationlib import iau2000b_radians
from skyfield.timelib import Time, Timescale
from skyfield.jpllib import SpiceKernel
from skyfield.positionlib import Apparent, Barycentric
from skyfield.toposlib import wgs84


class Planet(Enum):
    SUN = 'SUN',
    MOON = 'MOON',
    EARTH = 'EARTH',
    MERCURY = 'MERCURY',
    VENUS = 'VENUS',
    MARS = 'MARS'


T = TypeVar('T')
class SearchlibCallable(Generic[T]):
    def __init__(self, f: Callable[[Optional[Time]], T], step_days: float):
        self.f = f
        self.step_days = step_days

    def __call__(self, time: Optional[Time]) -> T:
        return self.f(time)


class Observer:
    def __init__(self, ephemeris: SpiceKernel, ts: Timescale, topos: tuple[float, float]):
        self.planets = ephemeris
        self.planet = self.planets[Planet.EARTH.name]
        self.topos = wgs84.latlon(*topos)
        self.obs = self.planet + self.topos
        self.ts = ts

    def or_now(self, time: Optional[Time] = None) -> Time:
        return time if time is not None else self.ts.now()
    
    def pos(self, time: Optional[Time] = None) -> Barycentric:
        time = self.or_now(time)

        res = self.obs.at(time)
        # this should never happen? but it pleases the typechecker
        if not isinstance(res, Barycentric):
            raise TypeError(f'invalid planet: {self.planet} isn\'t barycentric')
        
        return res

    def observe(self, planet: Planet, time: Optional[Time] = None) -> Apparent:
        time = self.or_now(time)

        return self.pos(time).observe(self.planets[planet.name]).apparent()

    def segment_func(self, segments: int) -> SearchlibCallable[npt.NDArray[np.int64] | np.int64]:
        sun = self.planets[Planet.SUN.name]

        def segment_at(time: Optional[Time] = None) -> npt.NDArray[np.int64] | np.int64:
            time = self.or_now(time)
            time._nutation_angles_radians = iau2000b_radians(time)

            _, lon, _ = self.pos(time).observe(sun).apparent().frame_latlon(ecliptic_frame)

            return (lon.radians // (tau / segments)).astype(int)

        return SearchlibCallable(segment_at, step_days=365/segments)

    def which_day_phase_func(self) -> SearchlibCallable[npt.NDArray[np.float64]]:
        sun = self.planets[Planet.SUN.name]

        def which_day_phase_at(time: Optional[Time] = None) -> npt.NDArray[np.float64]:
            time = self.or_now(time)
            time._nutation_angles_radians = iau2000b_radians(time)

            #alt, _, _ = planet.at(time).observe(sun).apparent().altaz()
            alt, _, _ = self.pos(time).observe(sun).apparent().altaz()
            alt_deg = alt.degrees

            r = np.zeros_like(alt_deg, int)
            r[alt_deg >= -18.0] = 1
            r[alt_deg >= -12.0] = 2
            r[alt_deg >= -6.0] = 3
            r[alt_deg >= -0.8333] = 4

            return r

        return SearchlibCallable(which_day_phase_at, step_days=0.02)

    def day_phase_func(self, phase: int) -> SearchlibCallable[np.bool_ | npt.NDArray[np.bool_]]:
        def day_phase_at(time: Optional[Time] = None) -> np.bool_ | npt.NDArray[np.bool_]:
            res: np.bool_ | npt.NDArray[np.bool_] = self.which_day_phase_func()(time) == phase
            return res

        return SearchlibCallable(day_phase_at, step_days=0.02)
