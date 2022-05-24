from dataclasses import dataclass
from queue import PriorityQueue
from functools import cache
import random

from crossword_generator.grid_generator import off_or_black
from .Entry import Entry
from .processor import extract_words, grid_to_string

from time import time

@dataclass(order=True)
class Grid:
    len_remaining_words: int

    # remaining_words: PriorityQueue(Entry)

    # n: int
    # squares: tuple[tuple[str]]

    # buckets: tuple[tuple[tuple[set]]]
    # buckets_split: tuple[int]
    
    buckets = {}
    buckets_split = {}
    
    # debug
    global valid_cnt, valid_time
    valid_cnt, valid_time = 0, 0
        
    global fill_cnt, fill_time
    fill_cnt, fill_time = 0, 0
    
    global loop_time, loop_cnt
    loop_time, loop_cnt = 0, 0
    
    global res_squares_cnt, res_squares_time
    res_squares_cnt, res_squares_time = 0, 0
    
    global res_init_cnt, res_init_time
    res_init_cnt, res_init_time = 0, 0
    
    global res_remaining_words_cnt, res_remaining_words_time
    res_remaining_words_cnt, res_remaining_words_time = 0, 0

    # TODO: optimization: only change words that are needed to be changed in extract_words?
    def __init__(self, squares=(), remaining_words=PriorityQueue(), buckets=None, buckets_split=()) -> None:
        if (squares == None):
            raise ValueError('Grid must not be None')
        if (len(squares) > 0 and len(squares) != len(squares[0])):
            raise ValueError('Grid must be square')

        self.squares = squares
        self.n = len(squares)
        
        s = time()
        
        if remaining_words != PriorityQueue():
            self.remaining_words = PriorityQueue()
            words, contains_words = extract_words(self.squares)
            for coords, x in contains_words.items():
                for direction, id in x.items():
                    word = words[direction][id]
                    if '.' in word:
                        self.remaining_words.put(
                            Entry(grid=self, word=word, r=coords[0], c=coords[1], direction=direction))
        else:
            self.remaining_words = remaining_words
        
        global res_remaining_words_cnt, res_remaining_words_time
        res_remaining_words_cnt += 1
        res_remaining_words_time += time() - s

        self.len_remaining_words = self.remaining_words.qsize()
        # self.buckets = buckets
        # self.buckets_split = buckets_split

    def __str__(self) -> str:
        return grid_to_string(self.squares)

    def off_or_black(self, r, c):
        return r < 0 or r >= self.n or c < 0 or c >= self.n or self.squares[r][c] == '#'

    def generate_blank(self):
        """Returns a grid, subject to some requirements.

        Currently requirements are somewhat contrived and may not be realistic,
        depending on word generation. Eventually they will be replaced with
        superior functions based on expected value.

        Args:
            n (int): grid size

        Returns:
            str: selected grid
        """

        def words_addition(grid, r, c):
            return 2 - (self.off_or_black(grid, r+1, c) or self.off_or_black(grid, r-1, c)) \
                - (self.off_or_black(grid, r, c+1)
                   or self.off_or_black(grid, r, c-1))

        MAX_BLACK = round(0.15*self.n*self.n+0.5*self.n-3.5)
        MIN_BLACK = MAX_BLACK//2
        NUM_BLACK = random.randint(MIN_BLACK, MAX_BLACK)
        MAX_WORDS = round(0.35*self.n*self.n-0.3*self.n+3)
        MIN_WORD_LENGTH = 3

        black = 0
        words = 2*self.n
        grid = [['.' for j in range(self.n)] for i in range(self.n)]
        available = [(i, j) for i in range(self.n) for j in range(self.n)]
        dr = [1, 0, -1, 0]
        dc = [0, 1, 0, -1]

        while black < NUM_BLACK and words <= MAX_WORDS:
            (r, c) = available[random.randint(0, len(available)-1)]
            valid = True
            for dir in range(4):
                within_len = [self.off_or_black(grid, r+dist*dr[dir], c+dist*dc[dir])
                              for dist in range(1, MIN_WORD_LENGTH+1)]
                if not(within_len[0]) and not(all(v == False for v in within_len)):
                    valid = False
            if valid:
                available.remove((r, c))
                if self.n < 11:
                    grid[r][c] = '#'
                    black += 1
                    words += words_addition(grid, r, c)
                else:
                    if self.n % 2 == 1 and r == self.n//2 and c == self.n//2:
                        grid[r][c] = '#'
                        black += 1
                        words += words_addition(grid, r, c)
                    else:
                        available.remove((self.n-1-r, self.n-1-c))
                        grid[r][c], grid[self.n-1-r][self.n-1-c] = '#', '#'
                        black += 2
                        words += words_addition(grid, r, c) + \
                            words_addition(grid, self.n-1-r, self.n-1-c)

        return grid

    def valid(self, debug=False) -> bool:
        """Checks if grid has a valid solution

        Returns:
            bool: True if the grid has a valid solution, False else
        """
        global valid_cnt, valid_time
        s = time()
        words = extract_words(self.squares)[0]
        # print(words)
        for direction, more_info in words.items():
            for id, word in more_info.items():
                if debug:
                    print("WORD: " + word)
                    print("POSSIBLE WORDS: " +
                          str(Grid.possible_words(word=word)))
                if Grid.possible_words(word=word) == set():
                    valid_cnt += 1
                    valid_time += time() - s
                    return False
        valid_cnt += 1
        valid_time += time() - s
        return True

    @cache
    def possible_words(word):
        # TODO: make this not hardcoded for only len(buckets_split) == 2
        
        # possible = set()
        # first = True

        if len(word) <= Grid.buckets_split[0] or word == '.' * len(word):
            return Grid.buckets[0][word] if word in Grid.buckets[0] else set()
        return Grid.buckets[0][word[:Grid.buckets_split[0]]].intersection(Grid.buckets[1][word[Grid.buckets_split[0]:]])

    def get_word(self, r, c, direction, length):
        """_summary_

        Args:
            r (int): row
            c (int): column
            direction (string): direction ('across' or 'down')
            length (int): length of word

        Raises:
            ValueError: _description_
            ValueError: _description_

        Returns:
            str: word
        """
        if not (direction == 'across' or direction == 'down'):
            raise ValueError('direction must be across or down')
        if off_or_black(self.squares, r, c):
            raise ValueError('r or c invalid')
        
        string_buffer = []
        for i in range(length):
            string_buffer.append(self.squares[r][c + i] if direction == 'across' else self.squares[r + i][c])
        
        return ''.join(string_buffer)
                

    def fill(self, entry):
        """Fills the grid with one word

        Args:
            entry (Entry): An Entry describing the word to be filled

        Raises:
            ValueError: Raises if self conflicts with entry.grid; see comment below 

        Returns:
            Grid: Grid with filled entry
        """
        
        s = time()

        if self != entry.grid:
            # techinically self is unnecessary, but this check is likely good to make sure the right grid is modified
            raise ValueError('Self should be equal to entry.grid')

        res_squares = [list(x) for x in self.squares]
        for i in range(len(entry.word)):
            if entry.direction == 'across':
                res_squares[entry.r][entry.c + i] = entry.word[i]
            else:
                res_squares[entry.r + i][entry.c] = entry.word[i]
        res_squares = tuple(tuple(x) for x in res_squares)

        global res_squares_cnt, res_squares_time

        res_squares_cnt += 1
        res_squares_time += time() - s

        res = Grid(squares=res_squares, remaining_words=self.remaining_words)
        
        global res_init_cnt, res_init_time
        res_init_cnt += 1
        res_init_time += time() - s
        
        global fill_cnt, fill_time
        fill_cnt += 1
        fill_time += time() - s
        
        return res

    def possible_next_grids(self):
        """Generates possible grids after filling in one word

        Returns:
            generator[Grid]: A generator containing the first k possible grids
        """
        
        s = time()
        
        cur_entry = self.remaining_words.get()

        possible = Grid.possible_words(word=cur_entry.word)
        
        k = 50
        # possible bottleneck since need to duplicate tuple?
        res = (self.fill(Entry(grid=cur_entry.grid, word=x, r=cur_entry.r, c=cur_entry.c,
               direction=cur_entry.direction)) for x in random.sample(possible, min(k, len(possible))))
        
        # python passes by reference
        self.remaining_words.put(cur_entry)
        
        global loop_time, loop_cnt
        loop_time += time() - s
        loop_cnt += 1

        return res

    def solve(self):
        """Solves the grid

        Returns:
            Grid: Solved grid, None if no solution
        """
        # debug
        push_time = 0
        push_cnt = 0
        
        cnt = 0

        pq = PriorityQueue()

        pq.put(self)

        while not pq.empty():
            p = pq.get()

            # print("ORIGINAL GRID:")
            # print(p)

            if not p.valid():
                continue

            if p.len_remaining_words == 0:
                return p

            cnt += 1
            if cnt % 100 == 0:
                global valid_cnt, valid_time
                print(f'{cnt} valid grids processed, current grid:\n' + str(p))
                print(f'VALID AVERAGE: {valid_time / valid_cnt}, VALID TIME: {valid_time}, VALID CNT: {valid_cnt}')
                print(f'PUSH AVERAGE: {push_time / push_cnt}, PUSH TIME: {push_time}, PUSH CNT: {push_cnt}')
                print(f'LOOP AVERAGE: {loop_time / loop_cnt}, LOOP TIME: {loop_time}, LOOP CNT: {loop_cnt}')
                print(f'FILL AVERAGE: {fill_time / fill_cnt}, FILL TIME: {fill_time}, FILL CNT: {fill_cnt}')
                print(f'RES_SQUARES AVERAGE: {res_squares_time / res_squares_cnt}, RES_SQUARES TIME: {res_squares_time}, RES_SQUARES CNT: {res_squares_cnt}')
                print(f'RES_INIT AVERAGE: {res_init_time / res_init_cnt}, RES_INIT TIME: {res_init_time}, RES_INIT CNT: {res_init_cnt}')
                print(f'RES_REMAINING_WORDS AVERAGE: {res_remaining_words_time / res_remaining_words_cnt}, RES_REMAINING_WORDS TIME: {res_remaining_words_time}, RES_REMAINING_WORDS CNT: {res_remaining_words_cnt}')

            # print("NEXT GRIDS:")
            s = time()
            for p_next in p.possible_next_grids():
                pq.put(p_next)
                # print(p_next)
            push_time += time() - s
            push_cnt += 1

        return None
