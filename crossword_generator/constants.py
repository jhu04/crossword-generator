MIN_SIZE = 4
MAX_SIZE = 15
MIN_WORD_LENGTH = 3
SIZE_RANGE = range(MIN_SIZE, MAX_SIZE + 1)
WORD_LENGTH_RANGE = range(MIN_WORD_LENGTH, MAX_SIZE + 1)
SYMMETRIC_SIZES = (11, 12, 13, 14, 15)
ALPHABET = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
DATA_ROOT = 'crossword_generator/data'
CLUE_SOURCES = [
    {
        'file_name': 'xd-cleaned.txt',
        'filter': lambda row: True,  # uncleaned: row['year'] > 2010,
        'delimeter': '\t'
    },
    {
        'file_name': 'ginsberg-clues-cleaned.txt',
        'filter': lambda row: True,
        'delimeter': '\t'
    },
    {
        'file_name': 'ginsberg-puns-cleaned.csv',
        'filter': lambda row: True,
        'delimeter': ','
    }
]
