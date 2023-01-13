import os
import pandas as pd

import generation.constants as const
from generation.helper import collapse, union


class CollectiveClueProcessor:
    """A collection of clue processors."""
    
    def __init__(self, inputs, verbose=True):
        assert isinstance(inputs, list)
        processors = [ClueProcessor(i['path'], i['filter'], i['delimeter'], verbose) 
            for i in inputs]
        self.clues = pd.concat([p.clues for p in processors], ignore_index=True)
        self.words = collapse(union)([p.words for p in processors])


class ClueProcessor:
    """
    Processes clue data from a csv.

    Attributes
    ----------
    clues: DataFrame storing clues and answers.
    words: Dictionary mapping lengths to dictionaries, which map 
           (pos, char) pairs to lists.

    TODO: currently only processes words for which there exists an associated
    old clue. update this if/when we generate clues ourselves.
    """

    def __init__(self, path, filter=lambda row: True, delimiter=',', verbose=True):
        print('Processing:', path)

        clues = pd.read_csv(path, sep=delimiter,
                            encoding='ISO-8859-1', engine='python').dropna()
        if const.RECLEAN:
            # TODO: make this readable
            re_clue = r'(?i)\d+((A|D)|-(Across|Down))|<\/|<>'
            re_answer = r'([A-Z])\1{3,}'
            braces = [('\"', '\"'), ('(', ')'), ('[', ']')]

            clues = clues[clues.apply(filter, axis=1)][['clue', 'answer']]
            clues['clue'] = clues['clue'].astype(str) \
                .apply(lambda s: s.replace('\"\"', '\"').strip()) \
                .apply(lambda s: s[1:-1] if (s[0], s[-1]) in braces else s)
            clues['answer'] = clues['answer'].astype(str) \
                .apply(lambda s: s.replace(" ", "").replace("-", "").strip().upper())
            clues = clues[clues['answer'].str.contains(r'^[A-Z]*$')]
            clues['len'] = clues['answer'].apply(lambda s: len(s))
            clues = clues[clues['len'].isin(const.WORD_LENGTH_RANGE)]
            clues = clues[~clues['clue'].str.contains(re_clue)]
            clues = clues[(~clues['answer'].str.contains(re_answer))
                          | (clues['answer'].isin(const.WHITELIST))]

            root, ext = os.path.splitext(path)
            clues.to_csv(root + const.CLEANED_SUFFIX + ext, sep=delimiter)

        if verbose:
            print('Done processing clues')

        words = self.init_words()
        for word in clues['answer'].unique():
            words[len(word)]['all'].add(word)
            for i in range(len(word)):
                words[len(word)][(i, word[i])].add(word)

        if verbose:
            print('Done processing words')

        self.clues = clues
        self.words = words

    def init_words(self):
        words = {i: {} for i in const.WORD_LENGTH_RANGE}
        for i in const.WORD_LENGTH_RANGE:
            words[i]['all'] = set()
            for j in range(i):
                for c in const.ALPHABET:
                    words[i][(j, c)] = set()
        return words
