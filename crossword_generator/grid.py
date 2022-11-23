from enum import Enum
import random
from crossword_generator.clue_processor import ClueProcessor

class Position:
    """Should be an inner class for Cardinal, but isn't due to Enum"""
    def __init__(self, row, col):
        self.row = row
        self.col = col

    def __repr__(self):
        return f'({self.row}, {self.col})'

class Cardinal(Enum): 
    NORTH = Position(-1, 0)
    SOUTH = Position(1, 0)
    EAST = Position(0, 1)
    WEST = Position(0, -1)

class Direction(Enum):
    ACROSS = 'across'
    DOWN = 'down'

    @classmethod
    def opposite(dir):
        return Direction.DOWN if dir is Direction.ACROSS else Direction.ACROSS

class Grid:
    """1-indexed N x N grid of Cells"""

    def __init__(self, n, set_layout=True):
        assert 4 <= n <= 15
        self.n = n
        self.grid = [[Cell(self, r, c) for c in range(n + 2)] for r in range(n + 2)]
        for i in range(self.n + 2):
            self.grid[i][0].make_wall()
            self.grid[i][self.n + 1].make_wall()
            self.grid[0][i].make_wall()
            self.grid[self.n + 1][i].make_wall()
        for i in range(self.n + 2):
            for j in range(self.n + 2):
                self.cell(i, j).set_neighbors()
        
        self.across = {}
        self.down = {}
        self.ids = {}
        self.entries = []
        if set_layout:
            self.generate_layout()
            self.number_cells()

    def cell(self, r, c):
        if r < 0 or r >= len(self.grid) or c < 0 or c >= len(self.grid[0]):
            return None
        return self.grid[r][c]
    
    def generate_layout(self):
        """Generates a 2D array of Cells, subject to requirements on the number of 
        walls and words and lengths of words it contains. Implemented via repeatedly 
        adding walls that satisfy these requirements."""
        
        # TODO: make cleaner bounds
        MAX_WALL = int(0.17 * self.n**2 + 0.066 * self.n - 1.1)
        MAX_WORDS = int(0.35 * self.n**2 - 0.3 * self.n + 3)
        MIN_WORD_LENGTH = 3
        SYMMETRY_CUTOFF = 11

        curr_wall = 0
        curr_words = 2 * self.n
        available_cells = [(i, j) for i in range(1, self.n + 1) for j in range(1, self.n + 1)]

        def added_words(r, c):
            """Incremented number of words by adding a wall at (r, c)"""
            return 2 - sum([self.grid[r + dir.value.row][c + dir.value.col].is_wall() for dir in Cardinal])

        def add_wall(r, c):
            nonlocal curr_wall, curr_words
            self.cell(r, c).make_wall()
            curr_wall += 1
            curr_words += added_words(r, c)
            available_cells.remove((r, c))

        illegal_cells = []
        if self.n >= SYMMETRY_CUTOFF and self.n % 2 == 1:
            for i in range(int(-(MIN_WORD_LENGTH + 1) / 2), int((MIN_WORD_LENGTH + 1) / 2)):
                illegal_cells.append((i + (self.n + 1) / 2, (self.n + 1) / 2))
                illegal_cells.append(((self.n + 1) / 2, i + (self.n + 1) / 2))
       
        while curr_wall < MAX_WALL and curr_words < MAX_WORDS:
            r, c = available_cells[random.randint(0, len(available_cells) - 1)]
            if all(self.cell(r, c).neighbors[dir].is_wall() \
                or len(self.cell(r, c).in_direction(dir)) > MIN_WORD_LENGTH for dir in Cardinal):
                if (r, c) not in illegal_cells:
                    add_wall(r, c)
                    if self.n >= SYMMETRY_CUTOFF:
                        add_wall(self.n + 1 - r, self.n + 1 - c)

    def number_cells(self):
        """Assigns clue numbers to cells. Specifically, assigns `across`,
        `down`, `ids`, and `entries`."""
        id = 1
        for r in range(1, self.n + 1):
            for c in range(1, self.n + 1):
                if self.cell(r, c).is_wall():
                    continue
                is_entry = False
                if self.cell(r, c).neighbors[Cardinal.WEST].is_wall():
                    is_entry = True
                    self.across[id] = self.cell(r, c)
                    self.ids[(r, c)] = id
                    self.entries.append(Entry(self, self.cell(r, c).get_across()))
                if self.cell(r, c).neighbors[Cardinal.NORTH].is_wall():
                    is_entry = True
                    self.down[id] = self.cell(r, c)
                    self.ids[(r, c)] = id
                    self.entries.append(Entry(self, self.cell(r, c).get_down()))
                if is_entry:
                    id += 1
        self.entries.sort(key=lambda e: -e.length)

    def fill(self, clue_processor: ClueProcessor, num_attempts=10, num_test_strings=10, verbose=True):
        """
        Fills in the grid, roughly* in order of decreasing word length. TODO: make this faster!
        
        *We actually want words to be entered in order of the number of blank cells. However,
        this is pretty annoying (and probably slow) to implement.
        """

        def intersection(sets):
            if len(sets) == 1:
                return sets[0]
            return sets[0].intersection(*sets[1:])

        def filled(grid: Grid):
            return all(not (grid.cell(r, c).is_blank()) \
                for c in range(1, grid.n + 1) for r in range(1, grid.n + 1))

        res = None

        def helper(grid: Grid, entries: list):
            """Fills in one word at a time, proceeding by DFS. TODO: set to list cast is slow!"""
            # TODO: memoize get_across(), get_down() after layout is set
            
            def get_candidates(entry: Entry):
                constraints = [(i, entry.cells[i].label) \
                    for i in range(entry.length) if not entry.cells[i].is_blank()]
                return list(intersection([clue_processor.words[entry.length][x] for x in constraints])) \
                    if constraints else list(clue_processor.words[entry.length]['all'])

            nonlocal res
            if res:
                return
            if verbose:
                print(grid, '\n')
            entries = [Entry(grid, [grid.cell(p.row, p.col)
                for p in entry.positions()]) for entry in entries]
            if not entries:
                res = grid
            entry = entries[0]
            candidates = get_candidates(entry)
            if candidates:
                if verbose:
                    print(entry, candidates[:num_test_strings], entries)
                words = random.sample(candidates, min(num_test_strings, len(candidates)))
                for word in words:
                    orthogonal_conflict = False
                    for i in range(entry.length):
                        entry.cells[i].label = word[i]
                        orthogonal = Entry(grid, entry.cells[i].get_entry(entry.direction.opposite()))
                        if not get_candidates(orthogonal):
                            orthogonal_conflict = True
                            break
                    if not orthogonal_conflict:
                        helper(grid.copy(), entries[1:])
        
        for _ in range(num_attempts):
            helper(self.copy(), self.entries)
            if res and filled(res):
                return res

    def copy(self):
        g = Grid(self.n, set_layout=False)
        for r in range(1, self.n + 1):
            for c in range(1, self.n + 1):
                g.cell(r, c).label = self.cell(r, c).label
        g.number_cells()
        return g

    def __str__(self):
        return '\n'.join(' '.join(self.cell(i, j).label \
            for j in range(1, self.n + 1)) for i in range(1, self.n + 1))


    # def valid(self, debug=False) -> bool:
    #     words = extract_words(self.squares)[0]
    #     # print(words)
    #     for direction, more_info in words.items():
    #         for id, word in more_info.items():
    #             if debug:
    #                 print("WORD: " + word)
    #                 print("POSSIBLE WORDS: " +
    #                       str(possible_words(word=word, buckets=self.buckets)))
    #             if possible_words(word=word, buckets=self.buckets) == set():
    #                 return False
    #     return True

    # def fill(self, entry):
    #     """Fills the grid with one word
    #     """

    #     if self != entry.grid:
    #         # techinically self is unnecessary, but this check is likely good to make sure the right grid is modified
    #         raise ValueError('Self should be equal to entry.grid')

    #     res_squares = [list(x) for x in self.squares]
    #     for i in range(len(entry.word)):
    #         if entry.direction == 'across':
    #             res_squares[entry.r][entry.c + i] = entry.word[i]
    #         else:
    #             res_squares[entry.r + i][entry.c] = entry.word[i]
    #     res_squares = tuple(tuple(x) for x in res_squares)

    #     res = Grid(res_squares, self.buckets)
    #     return res

    # def possible_next_grids(self):
    #     """Generates possible grids after filling in one word
    #     """
    #     cur_entry = self.remaining_words.get()

    #     possible = possible_words(word=cur_entry.word, buckets=self.buckets)

    #     k = 100
    #     res = (self.fill(Entry(grid=cur_entry.grid, word=x, r=cur_entry.r, c=cur_entry.c,
    #            direction=cur_entry.direction)) for x in random.sample(possible, min(k, len(possible))))
    #     # for x in res:
    #     #     print(x)cls

    #     return res

    # def solve(self):
    #     """Solves the grid
    #     """
    #     # debug
    #     cnt = 0

    #     pq = PriorityQueue()

    #     pq.put(self)

    #     while not pq.empty():
    #         p = pq.get()

    #         # print("ORIGINAL GRID:")
    #         # print(p)

    #         if not p.valid():
    #             continue

    #         if p.len_remaining_words == 0:
    #             return p

    #         cnt += 1
    #         if cnt % 10 == 0:
    #             print(f'{cnt} valid grids processed, current grid:\n' + str(p))

    #         # print("NEXT GRIDS:")
    #         for p_next in p.possible_next_grids():
    #             pq.put(p_next)
    #             # print(p_next)

    #     return None


class Cell:
    # WARNING: Cell.BLANK and Cell.WALL are NOT Cells!
    BLANK = "."
    WALL = "#"

    def __init__(self, grid, row, col, label=BLANK):
        self.grid = grid
        self.row = row
        self.col = col
        self.label = label
        self.neighbors = {}

    def set_neighbors(self):
        for dir in Cardinal:
            self.neighbors[dir] = self.grid.cell(self.row + dir.value.row, self.col + dir.value.col)

    def is_blank(self):
        return self.label == Cell.BLANK

    def is_wall(self):
        return self.label == Cell.WALL

    def make_wall(self):
        self.label = Cell.WALL
    
    def get_across(self):
        """Across array of Cells containing self"""
        left = self.in_direction(Cardinal.WEST)[:0:-1]
        right = self.in_direction(Cardinal.EAST)[1:]
        return left + [self] + right
    
    def get_down(self):
        """Down array of Cells containing self"""
        up = self.in_direction(Cardinal.NORTH)[:0:-1]
        down = self.in_direction(Cardinal.SOUTH)[1:]
        return up + [self] + down

    def get_entry(self, dir: Direction):
        return self.get_across() if dir is Direction.ACROSS else self.get_down()

    def in_direction(self, dir: Cardinal):
        """Returns a list of cells starting at self (inclusive) until hitting a wall.
        Only used internally (for get_across and get_down)."""
        if self.is_wall():
            return []
        return [self] + self.neighbors[dir].in_direction(dir)

    def __repr__(self):
        return f'Cell({self.row}, {self.col})'
    

class Entry:
    def __init__(self, grid: Grid, cells):
        self.grid = grid
        self.cells = cells
        self.length = len(cells)
        self.direction = Direction.ACROSS if cells[0].row == cells[1].row else Direction.DOWN
        self.id = grid.ids[(cells[0].row, cells[0].col)]

    def positions(self):
        return [Position(c.row, c.col) for c in self.cells]

    def __repr__(self):
        return f"{self.id}-{self.direction.value}"