import os
import argparse
import csv
from datetime import datetime
import math
import numpy as np
import pandas as pd
import time
from sklearn.feature_extraction.text import CountVectorizer
from tqdm import tqdm

import generation.constants as const
from generation.clue_processor import CollectiveClueProcessor
from generation.grid import Grid, Selector, ProbabilisticSelector
from generation.helper import collapse, merge_sum

results_path = 'tests/results'


class FillTester:
    """Tests grid fill efficiency to determine optimal parameters. TODO: Clean code."""

    columns = ['num_attempts', 'num_sample_strings', 'num_test_strings',
               'time_limit', 'selector', 'fn', 'randomize_factor',
               'success_time_mean', 'success_time_stdev', 'generate_num',
               'total_attempts', 'word_similarity']

    def __init__(self, **kwargs):
        self.params = kwargs
        for source in const.CLUE_SOURCES:
            source['path'] = os.path.join(const.DATA_PATH, source['file_name'])
        self.clue_processor = CollectiveClueProcessor(const.CLUE_SOURCES)


    def test_individual(self, params):
        """
        Tests an individual set of params. Returns counts of words reused in
        generated grid entries.
        """
        num_generated, total_attempts = 0, 0
        time_to_success, grids = [], []
        fn = eval(params['fn_str'])

        with tqdm(total=self.params['generate_num'], disable=not params['verbose']) as pbar:
            start_time = time.perf_counter()
            while num_generated < self.params['generate_num']:
                g = Grid(params['n'], verbose=False)
                g.fill(clue_processor=self.clue_processor,
                        num_attempts=params['num_attempts'],
                        num_sample_strings=params['num_sample_strings'],
                        num_test_strings=params['num_test_strings'],
                        time_limit=params['time_limit'],
                        selector_class=params['selector_class'],
                        fn=fn,
                        randomize_factor=params['randomize_factor'])
                if g.is_filled():
                    time_to_success.append(time.perf_counter() - start_time)
                    grids.append(g)
                    start_time = time.perf_counter()
                    num_generated += 1
                    pbar.update(1)
                total_attempts += 1

        time_to_success = np.array(time_to_success)
        success_time_mean = time_to_success.mean()
        success_time_stdev = time_to_success.std()
        word_similarity, reused_words = self.test_word_similarity(grids)
        with open(params['path'], 'a', newline='') as file:
            csv.writer(file).writerow([params['num_attempts'],
                                       params['num_sample_strings'],
                                       params['num_test_strings'],
                                       params['time_limit'],
                                       params['selector_class'].__name__,
                                       params['fn_str'],
                                       params['randomize_factor'],
                                       success_time_mean,
                                       success_time_stdev,
                                       self.params['generate_num'],
                                       total_attempts,
                                       word_similarity])
        return reused_words


    def grid_search(self, overwrite=False, verbose=True):
        """'Grid search' method for testing all params."""
        for n in self.params['n_range']:
            path = os.path.join(results_path, f"{n}x{n}_param_results.csv")
            if overwrite or not os.path.exists(path):
                with open(path, 'w', newline='') as file:
                    csv.writer(file).writerow(FillTester.columns)
            reused_words = []
            for num_attempts in self.params['num_attempts_range']:
                for num_sample_strings in self.params['num_sample_strings_range']:
                    for num_test_strings in self.params['num_test_strings_range']:
                        if num_test_strings >= num_sample_strings:
                            continue
                        for time_limit in self.params['time_limit_range']:
                            for selector_class in self.params['selectors']:
                                for fn_str in self.params['fns_str']:
                                    for randomize_factor in self.params['randomize_factors']:
                                        if verbose:
                                            print(
                                                "\n"
                                                f"n={n}"
                                                f"  num_attempts={num_attempts}"
                                                f"  num_sample_strings={num_sample_strings}"
                                                f"  num_test_strings={num_test_strings}"
                                                f"  time_limit={time_limit}"
                                                f"  selector_class={selector_class.__name__}"
                                                f"  fn={fn_str}"
                                                f"  randomize_factor={randomize_factor}"
                                            )
                                        reused_words.append(self.test_individual(locals()))
            
            _postprocess(n, collapse(merge_sum)(reused_words))


    def test_word_similarity(self, grids: list[Grid]):
        """
        Returns a float in [0, 1], with larger values indicating higher
        word similarity, along with a dictionary containing the counts for
        words that appeared more than once in `grids`. In practice, 
        len(grids) == generate_num. Low-rank approximation of the normalized 
        bag-of-words matrix.

        See https://stats.stackexchange.com/a/239211.
        """
        corpus = [' '.join(e.get_contents() for e in g.entries) for g in grids]
        vectorizer = CountVectorizer()
        counts = vectorizer.fit_transform(corpus).toarray().T
        bow = dict(zip(vectorizer.get_feature_names_out(), counts.sum(axis=1)))
        reused_words = {word: freq for word, freq in bow.items() if freq > 1}
        U, s, V = np.linalg.svd(counts / np.linalg.norm(counts, axis=0))
        return (s[0]**2-1) / (len(grids)-1), reused_words

    
def write():
    parser = argparse.ArgumentParser()
    parser.add_argument('--generate-num', nargs='?', type=int, default=10)
    parser.add_argument('--n-range', nargs='*', type=int, default=[5, 7, 9, 11, 13, 15])
    parser.add_argument('--num-attempts-range', nargs='*', type=int, default=[10])
    parser.add_argument('--num-sample-range', nargs='*', type=int, default=[10, 20, 50])
    parser.add_argument('--num-test-range', nargs='*', type=int, default=[5, 10, 20])
    parser.add_argument('--time-limit-range', nargs='*', type=float, default=[2, 5, 10])
    parser.add_argument('--selectors', nargs='*', type=str, default=['s', 'ps'])
    parser.add_argument('--fns', nargs='*', type=str, default=['lambda x: x'])
    parser.add_argument('--randomize-factors', nargs='*', type=float, default=[1])
    args = parser.parse_args()

    selector_map = {'s': Selector, 'ps': ProbabilisticSelector}
    selectors = [eval(s.lower(), selector_map) for s in args.selectors]

    tester = FillTester(generate_num=args.generate_num,
                        n_range=args.n_range,
                        num_attempts_range=args.num_attempts_range,
                        num_sample_strings_range=args.num_sample_range,
                        num_test_strings_range=args.num_test_range,
                        time_limit_range=args.time_limit_range,
                        selectors=selectors,
                        fns_str=args.fns,
                        randomize_factors=args.randomize_factors)
    tester.grid_search(overwrite=True, verbose=True)

def _postprocess(n, reused_words: dict[int]):
    postprocess([n], {n: reused_words})

def postprocess(n_range=None, reused_words=None):
    if n_range is None:
        parser = argparse.ArgumentParser()
        parser.add_argument('-n', '--sizes', nargs='*', type=int, default=[5, 7, 9, 11, 13, 15])
        args = parser.parse_args()
        if not args.sizes:
            raise ValueError('Provide at least one grid size to postprocess.')
        n_range = args.sizes

    if reused_words is not None:
        assert all(n in reused_words for n in n_range)
    
    params = ['num_attempts', 'num_sample_strings', 'num_test_strings', 'time_limit',
              'selector', 'fn', 'randomize_factor']
    performance = [col for col in FillTester.columns if col not in set(params)]

    for n in n_range:
        df = pd.read_csv(os.path.join(results_path, f"{n}x{n}_param_results.csv"))
        write_path = os.path.join(results_path, f"{n}x{n}_summary.md")
        with open(write_path, 'a') as f:
            if os.stat(write_path).st_size == 0:
                f.write(f'# {n}x{n} `test_fill` result summary\n')
            f.write(f'## {datetime.now().strftime("%m/%d/%Y %H:%M:%S")}\n')
            for col in params:
                f.write(
                    '```\n' +
                    df[[col, *performance]].groupby(col).mean().to_string() + 
                    '\n```\n'
                )
            if reused_words is not None:
                f.write(
                    'Reused words:\n```\n' +
                    str(reused_words[n]) +
                    '\n```\n'
                )


if __name__ == '__main__':
    write()
    # postprocess()