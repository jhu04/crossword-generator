import pandas as pd
import os
import crossword_generator.constants as const


class CollectiveClueProcessor:
    """
    A collection of clue processors.
    """

    def __init__(self, inputs, verbose):
        assert isinstance(inputs, list)
        processors = [ClueProcessor(
            i['path'], i['filter'], i['delimeter'], verbose) for i in inputs]
        self.clues = pd.concat([p.clues for p in processors], ignore_index=True)
        self.words = self.collapse(self.union, [p.words for p in processors])

    def collapse(self, f, ls):
        """Collapse list according to binary operator f. TODO: clean code."""
        res = ls[0]
        for i in range(1, len(ls)):
            res = f(res, ls[i])
        return res

    def union(self, A, B):
        """Union of dictionaries A, B, which have the same 'object structure'"""
        if isinstance(A, set) and isinstance(B, set):
            return A | B
        return {k: self.union(A[k], B[k]) for k in A}


class ClueProcessor:
    """
    Processes clue data from a csv.
        clues: DataFrame storing clues and answers.
        words: Dictionary mapping lengths to dictionaries, which map 
               (pos, char) pairs to lists.

    TODO: currently only processes words for which there exists an associated
    old clue. update this if/when we generate clues ourselves.
    """
    CLEANED_SUFFIX = '-cleaned'

    def __init__(self, path, filter=lambda row: True, delimiter=',', verbose=True):
        print('Processing:', path)

        clues = pd.read_csv(path, sep=delimiter, encoding='ISO-8859-1', engine='python').dropna()
        if ClueProcessor.CLEANED_SUFFIX not in path:
            # TODO: make this readable
            re = r'\d+(?:(?:A|D)|(?:-(?:Across|Down)))'
            clues = clues[clues.apply(filter, axis=1)][['clue', 'answer']]
            clues['clue'] = clues['clue'].astype(str) \
                .apply(lambda s: s.replace('\"\"', '\"').strip()) \
                .apply(lambda s: s[1:-1] if s[0] == s[-1] == '\"' else s)
            clues['answer'] = clues['answer'].astype(str) \
                .apply(lambda s: s.replace(" ", "").replace("-", "").strip().upper())
            clues = clues[clues['answer'].str.contains(r'^[A-Z]*$')]
            clues['len'] = clues['answer'].apply(lambda s: len(s))
            clues = clues[clues['len'].isin(const.WORD_LENGTH_RANGE)]
            clues = clues[~clues['clue'].str.contains(re)]

            root, ext = os.path.splitext(path)
            clues.to_csv(root + ClueProcessor.CLEANED_SUFFIX + ext, sep=delimiter)

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
