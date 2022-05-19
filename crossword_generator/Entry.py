from dataclasses import dataclass

from grid_generator import off_or_black

@dataclass(order=True)
class Entry:
    num_blank_sqaures: int
    
    word: str
    
    r: int
    c: int
    direction: str
    
    possible_answers: tuple[str]
    
    grid: object
    
    def __init__(self, grid, word, r, c, direction, possible_answers=None):
        self.grid = grid
        self.word = word
        if off_or_black(grid.squares, r, c):
            raise ValueError('r, c must be in range')
        self.r = r
        self.c = c
        
        if direction != 'across' and direction != 'down':
            raise ValueError('direction must be "across" or "down"')
        self.direction = direction
        
        self.num_blank_sqaures = sum(1 for ch in word if ch == ' ')
        
        self.possible_answers = possible_answers