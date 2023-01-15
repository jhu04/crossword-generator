import json
import os
import string

"""Grid generation"""
MIN_SIZE = 4
MAX_SIZE = 21
MIN_WORD_LENGTH = 3
LARGE_GRID_CUTOFF = 11
WORD_LENGTH_REQUIREMENTS = {
    '(3,)': 'range(0, int(0.18 * self.MAX_WORDS + 5.4))',
    '(4,)': 'range(0, int(0.4 * self.MAX_WORDS))',
    '(self.n-2, self.n-1, self.n)': 'range(1, 5)'
}
ALPHABET = string.ascii_uppercase

SIZE_RANGE = range(MIN_SIZE, MAX_SIZE + 1)
WORD_LENGTH_RANGE = range(MIN_WORD_LENGTH, MAX_SIZE + 1)
SYMMETRIC_SIZES = range(LARGE_GRID_CUTOFF, MAX_SIZE + 1)
DAILY_MINI_SIZES = (5)
DAILY_MAXI_SIZES = (11)

"""Clue processing"""
RECLEAN = False
CLEANED_SUFFIX = '-cleaned'
FILENAME_SUFFIX = '' if RECLEAN else CLEANED_SUFFIX
DATA_PATH = os.path.join(os.path.dirname(__file__), '..', 'data')
CLUE_SOURCES = [
    {
        'file_name': 'xd' + FILENAME_SUFFIX + '.txt',
        'filter': (lambda row: row['year'] > 2010) if RECLEAN else (lambda _: True),
        'delimeter': '\t'
    },
    {
        'file_name': 'ginsberg-clues' + FILENAME_SUFFIX + '.txt',
        'filter': lambda _: True,
        'delimeter': '\t'
    },
    {
        'file_name': 'ginsberg-puns' + FILENAME_SUFFIX + '.csv',
        'filter': lambda _: True,
        'delimeter': ','
    },
    {
        'file_name': 'scraped-clues-xwordinfo' + FILENAME_SUFFIX + '.csv',
        'filter': lambda _: True,
        'delimeter': ','
    }
]
with open(os.path.join(DATA_PATH, 'custom-lists.json'), 'r') as f:
    custom_lists = json.load(f)
    WHITELIST = custom_lists['whitelist']
