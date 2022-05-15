from crossword_generator.grid_generator import grid_to_string, make_grid


def grid_test():
  for n in range(5, 16):
    print(f'n = {n}')
    print(grid_to_string(make_grid(n)), '\n')


if __name__ == '__main__':
  grid_test()
