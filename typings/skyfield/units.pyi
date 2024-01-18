from typing import Any
import numpy as np

class Unit: ...

class Angle(Unit):
    degrees: np.ndarray[Any, np.dtype[np.float64]] | np.float64
    radians: np.ndarray[Any, np.dtype[np.float64]] | np.float64

class Distance(Unit): ...