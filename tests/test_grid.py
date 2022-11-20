from crossword_generator.clue_processor import ClueProcessor
from crossword_generator.grid import Grid

def test_grid(verbose=True):
    if verbose:
        for n in range(4, 16):
            print(f"n = {n}\n{Grid(n)}\n")

    g = Grid(6)
    print(g)
    if verbose:
        print(f"{g.across}\n{g.down}\n{g.clues}")
    return g

def test_clues(verbose=True):
    clue_processor = ClueProcessor('crossword_generator/data/clues.csv')
    if verbose:
        print(clue_processor.words[3])
    return clue_processor

if __name__ == '__main__':
    g = test_grid(verbose=False)
    clue_processor = test_clues(verbose=False)
    g.fill(clue_processor)
    print(g)