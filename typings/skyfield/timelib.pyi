from collections.abc import Iterable
from datetime import date, datetime, timedelta
from typing import Any
import numpy as np

class Timescale:
    def now(self) -> Time: ...
    def utc(self, year: datetime | date | Iterable[datetime] | int, month: int = ..., day: int = ..., hour: int = ..., minute: int = ..., second: float = ...) -> Time: ...

class Time:
    def __sub__(self, other: Time | timedelta | int | float) -> np.float64: ...
    # TODO: is this array type correct?
    def utc_datetime(self) -> np.ndarray[Any, np.dtype[np.object_]] | datetime: ...
    _nutation_angles_radians: tuple[float, float]