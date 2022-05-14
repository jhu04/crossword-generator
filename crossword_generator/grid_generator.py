from ast import Pass
import random


def grid_to_string(grid):
  """Returns a string used to visualize a 2D array.

  Args:
    grid (list(list(char))]): 2D array

  Returns:
    str

  """
  return '\n'.join(' '.join(row) for row in grid)


def make_grid(n):
  """Returns a grid, subject to some requirements.

  Args:
      n (int): grid size

  Works for n=15 only, working on other n

  Returns:
      str: selected grid, or `null` if failed
  """

  def off_or_black(grid, r, c):
    return r < 0 or r >= n or c < 0 or c >= n or grid[r][c] == '#'

  MAX_BLACK = random.randint(15, 38)
  MAX_WORDS = 78
  MIN_WORD_LENGTH = 3
  black = 0
  words = 2*n
  grid = [['.' for j in range(n)] for i in range(n)]
  available = [(i, j) for i in range(n) for j in range(n)]
  dr = [1, 0, -1, 0]
  dc = [0, 1, 0, -1]

  if MAX_BLACK % 2 == 1:
    grid[7][7] = '#'
    black += 1
  available.remove((7, 7))

  while black < MAX_BLACK and words < MAX_WORDS:
    (r, c) = available[random.randint(0, len(available)-1)]
    valid = True
    for dir in range(4):
      within_len = [off_or_black(grid, r+dist*dr[dir], c+dist*dc[dir])
                    for dist in range(1, MIN_WORD_LENGTH+1)]
      if not(within_len[0]) and not(all(v == False for v in within_len)):
        valid = False
    if valid:
      available.remove((r, c))
      available.remove((n-1-r, n-1-c))
      grid[r][c], grid[n-1-r][n-1-c] = ['#', '#']
      black += 2
      words += 2-off_or_black(grid, r+dr[0], c+dc[0])\
          - off_or_black(grid, r+dr[1], c+dc[1])

  return grid


print(grid_to_string(make_grid(15)))
