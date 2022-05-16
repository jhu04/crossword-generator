from crossword_generator.grid_generator import make_grid
from crossword_generator.processor import grid_to_string


def test_grid():
  for n in range(5, 16):
    print(f'n = {n}')
    print(grid_to_string(make_grid(n)), '\n')


if __name__ == '__main__':
  test_grid()
