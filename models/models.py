from typing import NamedTuple

class SignCoordinates(NamedTuple):
    index: int
    sign: str
    coordinates: dict

class Coordinates(NamedTuple):
    x: int
    y: int
    width: int
    height: int
