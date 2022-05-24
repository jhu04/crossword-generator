from crossword_generator.fill_grid import Grid
from crossword_generator.grid_generator import make_grid
from crossword_generator.processor import grid_to_string, extract_words
from crossword_generator.word_generator import generate_buckets

from time import time

def test_word():
    s = time()
    
    from json import load
    
    # debug since JSON 1 takes a while to load
    buckets = [{'.': 'a'}, {}]
    buckets_split = (7,)
    
    with open('./crossword_generator/buckets_7_8_1.json', 'r') as f:
        print('STARTING JSON 1 LOAD')
        buckets[0] = load(f)
        print('JSON 1 LOADED SUCCESSFULLY')

    with open('./crossword_generator/buckets_7_8_2.json', 'r') as f:
        print('STARTING JSON 2 LOAD')
        buckets[1] = load(f)
        print('JSON 2 LOADED SUCCESSFULLY')

    # cast lists to sets
    print('CASTING LISTS TO SETS')
    for x in buckets:
        for key, val in x.items():
            x[key] = set(val)
    print('CASTING SUCCESSFUL')
        
    print('PREPROCESSING "." * n')
    # preprocess for '.' * n, put into buckets[0]
    for i, x in enumerate(buckets):
        if i == 0:
            continue
        
        for key, val in buckets[i].items():
            if key == '.' * len(key):
                full_key = '.' * (buckets_split[i - 1] + len(key) + 1)
                if full_key in buckets[0]:
                    buckets[0][full_key].union(set(tuple(val)))
                else:
                    buckets[0][full_key] = set(tuple(val))
            
    print('PREPROCESSING "." * n SUCCESSFUL')
    
    pre_time = time() - s
    
    Grid.buckets = buckets
    Grid.buckets_split = buckets_split
    
    squares = make_grid(7)
    words, contains_words = extract_words(squares)
    
    print(extract_words(squares))
    
    print('INITIAL GRID:\n' + grid_to_string(squares))
    g = Grid(squares)
    solved = g.solve()
    print('SOLVED GRID:\n' + str(solved))
    
    print('Time taken: ', time() - s)
    print(f'PREPROCESSING TIME: {pre_time}')

if __name__ == '__main__':
    test_word()
