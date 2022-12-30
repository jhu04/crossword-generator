import json
import os
import string

MIN_SIZE = 4
MAX_SIZE = 15
MIN_WORD_LENGTH = 3
SIZE_RANGE = tuple(range(MIN_SIZE, MAX_SIZE + 1))
WORD_LENGTH_RANGE = tuple(range(MIN_WORD_LENGTH, MAX_SIZE + 1))
SYMMETRIC_SIZES = (11, 12, 13, 14, 15)
ALPHABET = string.ascii_uppercase

RECLEAN = False
CLEANED_SUFFIX = '-cleaned'
FILENAME_SUFFIX = '' if RECLEAN else CLEANED_SUFFIX
DATA_ROOT = 'crossword_generator/data'
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