import os
import functools
import numpy as np
import pandas as pd
import re
import wordninja
from nltk.corpus import words, wordnet
from nltk.stem.wordnet import WordNetLemmatizer

import generation.constants as const
from generation.helper import union


class CollectiveClueProcessor:
    """A collection of clue processors."""
    
    def __init__(self, inputs, verbose=True):
        assert isinstance(inputs, list)
        processors = [ClueProcessor(i['path'], i['filter'], i['delimeter'], verbose) 
                      for i in inputs]
        self.clues = pd.concat([p.clues for p in processors], ignore_index=True)
        self.words = functools.reduce(union, [p.words for p in processors])


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

    def __init__(self, path, filter, delimiter=',', verbose=True):
        print('Processing:', path)

        clues = pd.read_csv(path, sep=delimiter,
                            encoding='ISO-8859-1', engine='python').dropna()
        self.filter = filter
        if const.RECLEAN:
            clues = self.clean_clues(clues)
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

    def clean_clues(self, clues):
        # TODO: make this readable
        re_clue = r'(?i)\d+((A|D)|-(Across|Down))|<\/|<>'
        re_answer = r'([A-Z])\1{3,}'
        braces = [('\"', '\"'), ('(', ')'), ('[', ']')]

        clues = clues[clues.apply(self.filter, axis=1)][['clue', 'answer']]
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

        answers = np.unique(clues['answer'])
        answers = {answer: list({answer.lower(), ClueProcessor.split_words(answer).lower()})
                    for answer in answers}
        answers = {answer: [variant.split() for variant in variants] 
                    for answer, variants in answers.items()}
        
        lem = WordNetLemmatizer()
        p = re.compile('^[a-zA-Z]+$')
        with open(os.path.join(const.DATA_PATH, 'dwyl-words.txt'), 'r') as f:
            dwyl_words = [line.rstrip().lower() for line in f if p.match(line)]
        english = set([w.lower() for w in words.words()] + 
                      [w.lower() for w in wordnet.words()] + 
                      dwyl_words)
        parts_of_speech = ['n', 'v', 'a', 'r', 's']
        english_answers = [
            answer for answer, variants in answers.items() if any(any(any(
                lem.lemmatize(word, pos=pos) in english 
                for pos in parts_of_speech) 
                for word in variant) 
                for variant in variants)
        ]
        return clues[clues['answer'].isin(english_answers)]

    def split_words(s):
        """Probabilistically splits strings into English words."""
        contractions = ['d', 'm', 's', 't', 'll', 're', 've']
        split = wordninja.split(s)
        for i in range(len(split)-1, 0, -1):
            if split[i] in contractions:
                split[i-1] += split.pop(i)
        return ' '.join(split)
