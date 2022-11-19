from crossword_generator.grid_generator import make_grid
from crossword_generator.processor import grid_to_string
from crossword_generator.grid import Grid

def test_grid():
    for n in range(5, 16):
        print(f'n = {n}')
        print(Grid(n))

if __name__ == '__main__':
    test_grid()
