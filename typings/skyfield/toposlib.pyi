from .vectorlib import VectorFunction

class ITRSPosition(VectorFunction): ...

class GeographicPosition(ITRSPosition): ...

class Geoid:
    def latlon(self, latitude_degrees: float, longitude_degrees: float, elevation_m: float = ...) -> GeographicPosition: ...

wgs84: Geoid
