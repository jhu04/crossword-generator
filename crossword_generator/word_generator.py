from functools import lru_cache
import re

from queue import Empty, PriorityQueue
from queue import Queue

n = 15

# '#' = black square, '.' = blank square
grid = [['.' for j in range(n)] for i in range(n)]
grid_str = '\n'.join(''.join(x) for x in grid)

# example_grid_str = '''   #   A  #    
#    #   N  #    
#    #TANGELOTREE
#       #E    ###
# STRANGELY#     
# ###    S#      
#      # A   #   
#     #  N  #    
#    #   D #     
#       #D    ###
#      #DESDEMONA
# ###    M#      
# CLAUDEMONET#   
#     #  N   #   
#     #  S   #   '''

example_grid_str = '''...#...A..#....
...#...N..#....
...#TANGELOTREE
......#E....###
STRANGELY#.....
###....S#......
.....#.A...#...
....#..N..#....
...#...D.#.....
......#D....###
.....#DESDEMONA
###....M#......
CLAUDEMONET#...
....#..N...#...
....#..S...#...'''

example_grid = [list(x) for x in example_grid_str.split('\n')]

grid = example_grid
grid_str = example_grid_str


def upper_to_int(ch):
  """Returns an integer based on the mapping {'A': 0, ..., 'Z': 25}

  Args:
      ch (char): character to be mapped

  Returns:
      int: mapped value
  """
  return ord(ch) - ord('A')


def transpose(grid):
  """Returns the transpose of a grid

  Args:
      grid (list[list[int]]): grid

  Returns:
      list[list[int]]: transpose
  """
  res = grid
  for i in len(res):
    for j in len(i):
      res[i][j] = grid[j][i]
  return res

# TODO: def cost(grid):

def search(initial, possible_words):
  """Searches for a solution to initial

  Args:
      initial (list[list[int]]): Initial state of crossword to be solved

  Returns:
      list[list[int]]: TODO: Solution to crossword
  """

  return initial

def generate_buckets():
  """Generates buckets

  Returns:
      tuple[tuple[tuple[set]]]: buckets[len][pos][char] = set of possible words
  """
  with open('../data/wordlist.txt', 'r') as f:
    buckets = [[[set([]) for ch in range(26)]
                for ch_pos in range(length + 1)]
               for length in range(n + 1)]

    for x in f:
      x = x.strip()
      if len(x) <= n and x.isalpha():
        for i, ch in enumerate(x):
          buckets[len(x)][i][upper_to_int(ch)].add(x)
    
    # preprocess word = '.' * len
    for length in range(n + 1):
      possible = set()
      for possible_i in buckets[length]:
        for possible_ch in possible_i:
            possible = possible.union(possible_ch)
      
      buckets[length][length] = possible
    
    return buckets

# https://stackoverflow.com/questions/30730983/make-lru-cache-ignore-some-of-the-function-arguments
from cachetools import cached
from cachetools.keys import hashkey

@cached(cache={}, key=lambda buckets, word: hashkey(word))
def possible_words(word, buckets):
  possible = set()
  first = True

  if word == '.' * len(word):
    return buckets[len(word)][len(word)]
  else:
    for i, ch in enumerate(word):
      if ch == '.':
        continue

      if first:
        possible = buckets[len(word)][i][upper_to_int(ch)]
        first = False
      elif possible == set():
        return set()
      else:
        possible = possible.intersection(
            buckets[len(word)][i][upper_to_int(ch)])
  
  return possible

def main():
  buckets = generate_buckets()

  # horizontal
  # words_to_generate = re.split('[\n#]+', grid_str)
  words_to_generate = []
  words_to_generate_index = []

  # https://stackoverflow.com/questions/28828921/python-split-string-and-get-position
  # https://stackoverflow.com/questions/2078915/a-regular-expression-to-exclude-a-word-string
  for x in re.finditer('[^\n#]+', grid_str):
    words_to_generate.append(x.group())
    words_to_generate_index.append(x.start())

  # finds possible words that match criteria
  possible_words_to_generate = [{} for x in words_to_generate]
  for word_i, x in enumerate(words_to_generate):
    print(f'x: {x}')

    possible = set([])

    if x.strip() == '':
      for possible_i in buckets[len(x)]:
        for possible_ch in possible_i:
          possible = possible_ch.union(ch)
    else:
      for i, ch in enumerate(x):
        if ch == '.':
          continue

        if possible == set([]):
          possible = buckets[len(x)][i][upper_to_int(ch)]
        else:
          possible = possible.intersection(
              buckets[len(x)][i][upper_to_int(ch)])

    possible_words_to_generate[word_i] = possible

  print(possible_words_to_generate)

  # search
  pq = PriorityQueue()
  # pq.push(Grid(grid))
  
  while (not pq.empty()):
    p = pq.get()
    
    # get possible grids
    

  # interface
  inp = ['']
  i = 0
  while inp[0] != 'q':
    print('ACTIONS:')
    print('g: print grid')
    print('i: store i, get ith word')
    print('p: prints possible words for ith word')
    print('s: set ith word')
    print('save: save crossword')
    print('q: quit')

    inp = str(input()).split()
    if len(inp) == 0:
      print('invalid')
    elif inp[0] == 'g':
      print(grid_str)
    elif inp[0] == 'i':
      i = int(inp[1])
      print(f'WORD: {words_to_generate[i]}')
      print(f'LEN: {len(words_to_generate[i])}')
    elif inp[0] == 'p':
      print(possible_words_to_generate[i])
    elif inp[0] == 's':
      if len(inp[1]) != len(words_to_generate[i]):
        print('INVALID LENGTH')
        continue

      words_to_generate[i] = inp[1]

      grid_str = grid_str[:words_to_generate_index[i]] + words_to_generate[i] + \
          grid_str[words_to_generate_index[i] + len(words_to_generate[i]):]
    elif inp[0] == 'save':
      with open('crossword.txt', 'w') as f:
        f.write(grid_str)


if __name__ == '__main__':
  main()