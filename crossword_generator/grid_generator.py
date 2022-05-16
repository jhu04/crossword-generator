import random


def off_or_black(grid, r, c):
  return r < 0 or r >= len(grid) or c < 0 or c >= len(grid[0]) or grid[r][c] == '#'


def make_grid(n):
  """Returns a grid, subject to some requirements.

  Currently requirements are somewhat contrived and may not be realistic,
  depending on word generation. Eventually they will be replaced with
  superior functions based on expected value.

  Args:
      n (int): grid size

  Returns:
      str: selected grid
  """

  def words_addition(grid, r, c):
    return 2 - (off_or_black(grid, r+1, c) or off_or_black(grid, r-1, c)) \
        - (off_or_black(grid, r, c+1) or off_or_black(grid, r, c-1))

  MAX_BLACK = round(0.15*n*n+0.5*n-3.5)
  MIN_BLACK = MAX_BLACK//2
  NUM_BLACK = random.randint(MIN_BLACK, MAX_BLACK)
  MAX_WORDS = round(0.35*n*n-0.3*n+3)
  MIN_WORD_LENGTH = 3

  black = 0
  words = 2*n
  grid = [['.' for j in range(n)] for i in range(n)]
  available = [(i, j) for i in range(n) for j in range(n)]
  dr = [1, 0, -1, 0]
  dc = [0, 1, 0, -1]

  while black < NUM_BLACK and words <= MAX_WORDS:
    (r, c) = available[random.randint(0, len(available)-1)]
    valid = True
    for dir in range(4):
      within_len = [off_or_black(grid, r+dist*dr[dir], c+dist*dc[dir])
                    for dist in range(1, MIN_WORD_LENGTH+1)]
      if not(within_len[0]) and not(all(v == False for v in within_len)):
        valid = False
    if valid:
      available.remove((r, c))
      if n < 11:
        grid[r][c] = '#'
        black += 1
        words += words_addition(grid, r, c)
      else:
        if n % 2 == 1 and r == n//2 and c == n//2:
          grid[r][c] = '#'
          black += 1
          words += words_addition(grid, r, c)
        else:
          available.remove((n-1-r, n-1-c))
          grid[r][c], grid[n-1-r][n-1-c] = '#', '#'
          black += 2
          words += words_addition(grid, r, c) + \
              words_addition(grid, n-1-r, n-1-c)

  return grid
