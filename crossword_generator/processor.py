from crossword_generator.grid_generator import off_or_black


def grid_to_string(grid):
  return '\n'.join(''.join(row) for row in grid)


def string_to_grid(s):
  return [list(row) for row in s.split('\n')]


def extract_words(grid):
  """
  Extracts horizontal and vertical words from a filled grid

  Args:
      grid (list(list(char)))

  Returns:
      dict(dict(str))
  """
  words = {"across": {}, "down": {}}
  id = 1
  for r in range(len(grid)):
    for c in range(len(grid[0])):
      if grid[r][c] == '#':
        continue
      word = False
      if off_or_black(grid, r, c-1):
        word, x, s = True, c, ""
        while(x < len(grid[0]) and grid[r][x] != '#'):
          s += grid[r][x]
          x += 1
        words['across'][id] = s
      if off_or_black(grid, r-1, c):
        word, x, s = True, r, ""
        while(x < len(grid) and grid[x][c] != '#'):
          s += grid[x][c]
          x += 1
        words['down'][id] = s
      id += word
  return words


def grid_equality(grid1, grid2):
  """
  Checks if two grids are identical
  """
  if len(grid1) != len(grid2) or len(grid1[0]) != len(grid2[0]):
    return False
  for i in range(len(grid1)):
    for j in range(len(grid2)):
      if grid1[i][j] != grid2[i][j]:
        return False
  return True