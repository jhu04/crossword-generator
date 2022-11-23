import pandas as pd

class ClueProcessor:
    """
    Processes clue data from a csv.
        clues: DataFrame storing clues and answers.
        words: Dictionary mapping lengths to dictionaries, which map (pos, char) pairs to lists.

    TODO: currently only processes words for which there exists an associated
    old clue. update this if/when we generate clues ourselves.
    """

    def __init__(self, path):
        clues = pd.read_csv(path)
        clues = clues[['clue', 'answer']]
        clues['clue'] = clues['clue'].astype(str).apply(lambda s : s.split("(")[0].strip())
        clues['answer'] = clues['answer'].astype(str).apply(
            lambda s : s.replace(" ", "").replace("-", "").strip().upper())
        clues = clues[clues['answer'].str.contains(r'^[A-Z]*$')]
        clues['len'] = clues['answer'].apply(lambda s : len(s))
        clues = clues[(clues['len']>=3) & (clues['len']<=15)]

        words = {i: {} for i in range(3, 16)}
        for i in range(3, 16):
            words[i]['all'] = set()
            for j in range(i):
                for c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
                    words[i][(j, c)] = set()
        for word in clues['answer'].unique():
            words[len(word)]['all'].add(word)
            for i in range(len(word)):
                words[len(word)][(i, word[i])].add(word)

        self.clues = clues
        self.words = words
        