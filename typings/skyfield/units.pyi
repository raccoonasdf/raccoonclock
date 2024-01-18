from typing import Any
import numpy as np
import numpy.typing as npt

class Unit: ...

class Angle(Unit):
    degrees: npt.NDArray[np.float64] | np.float64
    radians: npt.NDArray[np.float64] | np.float64

class Distance(Unit): ...