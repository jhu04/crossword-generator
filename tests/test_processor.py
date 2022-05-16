from more_itertools import sample
from crossword_generator.processor import extract_words, string_to_grid

sample_grid = """ABC#
EFGH
IJKL
#MNO"""

if __name__ == '__main__':
  print(extract_words(string_to_grid(sample_grid)))
