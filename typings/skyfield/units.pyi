from numpy import ndarray, float64

class Unit: ...

class Angle(Unit):
    degrees: ndarray | float64
    radians: ndarray | float64

class Distance(Unit): ...