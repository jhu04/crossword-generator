import json
import os
import string

MIN_SIZE = 4
MAX_SIZE = 21
MIN_WORD_LENGTH = 3
LARGE_GRID_CUTOFF = 11
WORDS_LENGTH_N_MIN = 2
WORDS_LENGTH_N_MAX = 2
ALPHABET = string.ascii_uppercase

SIZE_RANGE = range(MIN_SIZE, MAX_SIZE + 1)
WORD_LENGTH_RANGE = range(MIN_WORD_LENGTH, MAX_SIZE + 1)
WORDS_LENGTH_N_RANGE = range(WORDS_LENGTH_N_MIN, WORDS_LENGTH_N_MAX + 1)
SYMMETRIC_SIZES = range(LARGE_GRID_CUTOFF, MAX_SIZE + 1)

RECLEAN = True
CLEANED_SUFFIX = '-cleaned'
FILENAME_SUFFIX = '' if RECLEAN else CLEANED_SUFFIX
DATA_ROOT = os.path.abspath('../data')
CLUE_SOURCES = [
    {
        'file_name': f'xd{FILENAME_SUFFIX}.txt',
        'filter': (lambda row: row['year'] > 2010) if RECLEAN else (lambda _: True),
        'delimeter': '\t'
    },
    {
        'file_name': f'ginsberg-clues{FILENAME_SUFFIX}.txt',
        'filter': lambda _: True,
        'delimeter': '\t'
    },
    {
        'file_name': f'ginsberg-puns{FILENAME_SUFFIX}.csv',
        'filter': lambda _: True,
        'delimeter': ','
    }
]
with open(os.path.join(DATA_ROOT, 'custom-lists.json'), 'r') as f:
    custom_lists = json.load(f)
    WHITELIST = custom_lists['whitelist']