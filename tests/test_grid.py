from crossword_generator.clue_processor import ClueProcessor
from crossword_generator.grid import Grid


def test_grid_layout_generation(size, verbose=True):
    if verbose:
        for n in range(4, 16):
            print(f"n = {n}\n{Grid(n)}\n")

    g = Grid(size)

    print('Testing grid:')
    print(g)
    print()

    if verbose:
        print(f"{g.across}\n{g.down}\n{g.clues}")
        print()

    return g


def test_clues(verbose=True):
    clue_processor = ClueProcessor('crossword-generator/data/clues.csv')
    print('Done processing clues')
    if verbose:
        print(clue_processor.words[3])
    return clue_processor


def main():
    import cProfile
    import pstats

    with cProfile.Profile() as pr:
        clue_processor = test_clues(verbose=False)
        for i in range(1):
            print(f'Processing grid {i}')

            # test layout generation
            g = test_grid_layout_generation(7, verbose=False)

            # test fill
            g.fill(clue_processor, num_attempts=10, num_sample_strings=10, num_test_strings=10, verbosity=0.01)

            print(f'Processed grid {i}')
            print('Final grid:')
            print(g)
            print()

    stats = pstats.Stats(pr)
    stats.sort_stats(pstats.SortKey.TIME)
    stats.dump_stats(filename='crossword-generator/tests/results/crossword_generation.prof')

    print(g)


if __name__ == '__main__':
    main()
