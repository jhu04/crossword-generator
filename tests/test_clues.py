import os
import crossword_generator.constants as const
from crossword_generator.clue_processor import CollectiveClueProcessor

def test_clues(verbose=True):
    for source in const.CLUE_SOURCES:
        source['path'] = os.path.join(const.DATA_ROOT, source['file_name'])

    clue_processor = CollectiveClueProcessor(const.CLUE_SOURCES, verbose)
    if verbose:
        print(clue_processor.clues.len.value_counts())
        print(clue_processor.words[const.MIN_WORD_LENGTH])

if __name__ == '__main__':
    test_clues()