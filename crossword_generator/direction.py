from enum import Enum

class RowCol:
    def __init__(self, r, c):
        self.r = r
        self.c = c

    def __repr__(self):
        return f'({self.r}, {self.c})'

class Direction(Enum):
    NORTH = RowCol(-1, 0)
    SOUTH = RowCol(1, 0)
    EAST = RowCol(0, 1)
    WEST = RowCol(0, -1)