import random


def grid_to_string(grid):
  return '\n'.join(''.join(row) for row in grid)


def make_grid(n):
  """Returns a grid, subject to some requirements.

  Currently these requirements are somewhat contrived and are obtained
  from estimates for small n and official rules for n=15. See definitions
  of MIN_BLACK, MAX_BLACK, and MAX_WORDS. They may also not be realistic,
  depending on word generation. Eventually they will be replaced with
  superior functions based on expected value.

  5/15: Glitch in generation for odd n: weird things happen near (n//2, n//2),
  i.e. it is possible to have 1-cell gaps if (n//2, n//2) is not selected
  and neighboring cells are. The fix should be straightforward, but one 
  must be careful to not cause more local failures.

  Args:
      n (int): grid size

  Returns:
      str: selected grid
  """

  def off_or_black(grid, r, c):
    return r < 0 or r >= n or c < 0 or c >= n or grid[r][c] == '#'

  MIN_BLACK = round(0.04*n*n+0.6*n-3.3)
  MAX_BLACK = round(0.15*n*n+0.5*n-3.5)
  NUM_BLACK = random.randint(MIN_BLACK, MAX_BLACK)
  MAX_WORDS = round(0.35*n*n-0.3*n+3)
  MIN_WORD_LENGTH = 3

  black = 0
  words = 2*n
  grid = [['.' for j in range(n)] for i in range(n)]
  available = [(i, j) for i in range(n) for j in range(n)]
  dr = [1, 0, -1, 0]
  dc = [0, 1, 0, -1]

  if n % 2 == 1:
    grid[n//2][n//2] = '#'
    black += 1
    words += 2
    available.remove((n//2, n//2))

  while black < NUM_BLACK and words < MAX_WORDS:
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
      words += 4 - (off_or_black(grid, r+1, c) or off_or_black(grid, r-1, c)) \
          - (off_or_black(grid, r, c+1) or off_or_black(grid, r, c-1)) \
          - (off_or_black(grid, n-r, n-1-c) or off_or_black(grid, n-2-r, n-1-c)) \
          - (off_or_black(grid, n-1-r, n-c) or off_or_black(grid, n-1-r, n-2-c))

  return grid


for n in range(4, 16):
  print(f"n = {n}")
  print(grid_to_string(make_grid(n)), "\n")
