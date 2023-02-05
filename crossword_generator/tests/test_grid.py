import argparse
import os
import pandas as pd
import time
from tqdm import tqdm

import generation.constants as const
from generation.clue_processor import CollectiveClueProcessor
from generation.grid import Grid


def test_layout_generation(size=7, verbose=True):
    if verbose:
        for n in const.SIZE_RANGE:
            print(str(n) + '\n' + str(Grid(n, verbose=True)) + '\n\n')

    g = Grid(size)
    print('Testing grid:\n' + str(g) + '\n\n')
    print(str(g.across) + '\n' + str(g.down) + '\n\n')

    return g


def test_layout_efficiency(size, num_iters=100):
    runtimes = []
    for i in range(num_iters):
        print('iteration', i)
        start = time.perf_counter()
        Grid(size, verbose=True)
        runtime = time.perf_counter() - start
        print('time:', runtime)
        runtimes.append(runtime)
    
    print(pd.DataFrame(runtimes, columns=['runtime']).describe())

def test_clues(verbose=True):
    for source in const.CLUE_SOURCES:
        source['path'] = os.path.join(const.DATA_PATH, source['file_name'])

    clue_processor = CollectiveClueProcessor(const.CLUE_SOURCES, verbose)
    if verbose:
        print(clue_processor.clues.len.value_counts())
        print(clue_processor.words[const.MIN_WORD_LENGTH])
    return clue_processor


def main(n, results_path='tests/results'):
    """Tests grid layout and fill functionality."""
    import cProfile
    import pstats

    success_path = os.path.join(results_path, f'{n}x{n}.txt')
    fail_path = os.path.join(results_path, f'{n}x{n}_failed.txt')

    with cProfile.Profile() as pr:
        clue_processor = test_clues(verbose=False)
        num_generated_grids = 0
        i = 0
        while num_generated_grids < 10:
            print(f'Processing grid {i}')
            g = Grid(n)
            # TODO: find optimal num_test_strings, 10 seems good?
            g.fill(clue_processor, num_attempts=100, num_sample_strings=10, 
                   num_test_strings=5, time_limit=10, verbosity=0.0001)  

            print(f'Processed grid {i}')
            print('Final grid:')
            print(g)
            print()

            if g.is_filled():
                # continuously opening and closing file to ensure file updates after grid generated
                with open(success_path, 'a') as f:
                    f.write(f'{g.__str__()}\n\n')
                num_generated_grids += 1
            else:
                with open(fail_path, 'a') as f:
                    f.write(f'{g.__str__()}\n\n')
            i += 1

    stats = pstats.Stats(pr)
    stats.sort_stats(pstats.SortKey.TIME)
    stats.dump_stats(
        filename=os.path.join(results_path, 'crossword_generation_multiple.prof'))

    print(g)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', '--size', nargs='?', type=int, default=15)
    parser.add_argument('-it', '--num-iters', nargs='?', type=int, default=100)
    args = parser.parse_args()

    # test_layout_generation()
    # test_layout_efficiency(args.size, args.num_iters)
    main(args.size)
