from dataclasses import dataclass
from queue import PriorityQueue
import random
from .entry import Entry
from .processor import extract_words, grid_to_string
from .word_generator import generate_buckets, possible_words


@dataclass(order=True)
class Grid:
    len_remaining_words: int

    # remaining_words: PriorityQueue(Entry)

    # n: int
    # squares: tuple[tuple[str]]

    # buckets: tuple[tuple[tuple[set]]]
    # buckets[len][pos][char] = possible_words

    def __init__(self, squares=(), buckets=None) -> None:
        if (squares == None):
            raise ValueError('Grid must not be None')
        if (len(squares) > 0 and len(squares) != len(squares[0])):
            raise ValueError('Grid must be square')

        self.squares = squares
        self.n = len(squares)

        self.remaining_words = PriorityQueue()
        words, contains_words = extract_words(self.squares)
        for coords, x in contains_words.items():
            for direction, id in x.items():
                word = words[direction][id]
                if '.' in word:
                    self.remaining_words.put(
                        Entry(grid=self, word=word, r=coords[0], c=coords[1], direction=direction))

        self.len_remaining_words = self.remaining_words.qsize()
        self.buckets = buckets

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
        words = extract_words(self.squares)[0]
        # print(words)
        for direction, more_info in words.items():
            for id, word in more_info.items():
                if debug:
                    print("WORD: " + word)
                    print("POSSIBLE WORDS: " +
                          str(possible_words(word=word, buckets=self.buckets)))
                if possible_words(word=word, buckets=self.buckets) == set():
                    return False
        return True

    def fill(self, entry):
        """Fills the grid with one word

        Args:
            entry (Entry): An Entry describing the word to be filled

        Raises:
            ValueError: Raises if self conflicts with entry.grid; see comment below 

        Returns:
            Grid: Grid with filled entry
        """

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

        res = Grid(res_squares, self.buckets)
        return res

    def possible_next_grids(self):
        """Generates possible grids after filling in one word

        Returns:
            generator[Grid]: A generator containing the first k possible grids
        """
        cur_entry = self.remaining_words.get()

        possible = possible_words(word=cur_entry.word, buckets=self.buckets)

        k = 100
        res = (self.fill(Entry(grid=cur_entry.grid, word=x, r=cur_entry.r, c=cur_entry.c,
               direction=cur_entry.direction)) for x in random.sample(possible, min(k, len(possible))))
        # for x in res:
        #     print(x)cls

        return res

    def solve(self):
        """Solves the grid

        Returns:
            Grid: Solved grid, None if no solution
        """
        # debug
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
            if cnt % 10 == 0:
                print(f'{cnt} valid grids processed, current grid:\n' + str(p))

            # print("NEXT GRIDS:")
            for p_next in p.possible_next_grids():
                pq.put(p_next)
                # print(p_next)

        return None
