import random
from sortedcontainers import SortedList
from crossword_generator.cell import Cell
from crossword_generator.clue_processor import ClueProcessor
from crossword_generator.direction import Direction


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
        self.clues = []
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
            return 2 - sum([self.grid[r + dir.value.r][c + dir.value.c].is_wall() for dir in Direction])

        def add_wall(r, c):
            nonlocal curr_wall, curr_words
            self.cell(r, c).make_wall()
            curr_wall += 1
            curr_words += added_words(r, c)
            available_cells.remove((r, c))

        illegal_cells = []
        if self.n >= SYMMETRY_CUTOFF and self.n % 2 == 1:
            for i in range(int(-(MIN_WORD_LENGTH + 1) / 2), int((MIN_WORD_LENGTH + 1) / 2)):
                illegal_cells.append((i + (self.n+1)/2, (self.n+1)/2))
                illegal_cells.append(((self.n+1)/2, i + (self.n+1)/2))
       
        while curr_wall < MAX_WALL and curr_words < MAX_WORDS:
            (r, c) = available_cells[random.randint(0, len(available_cells) - 1)]
            if all(self.cell(r, c).neighbors[dir].is_wall() \
                or len(self.cell(r, c).in_direction(dir)) > MIN_WORD_LENGTH for dir in Direction):
                if (r, c) not in illegal_cells:
                    add_wall(r, c)
                    if self.n >= SYMMETRY_CUTOFF:
                        add_wall(self.n + 1 - r, self.n + 1 - c)

    def number_cells(self):
        """Assigns clue numbers to cells"""
        id = 1
        for r in range(1, self.n + 1):
            for c in range(1, self.n + 1):
                if self.cell(r, c).is_wall():
                    continue
                is_clue = False
                if self.cell(r, c).neighbors[Direction.WEST].is_wall():
                    is_clue = True
                    self.across[id] = self.cell(r, c)
                    self.clues.append((len(self.cell(r, c).get_across()), 'across', id))
                if self.cell(r, c).neighbors[Direction.NORTH].is_wall():
                    is_clue = True
                    self.down[id] = self.cell(r, c)
                    self.clues.append((len(self.cell(r, c).get_down()), 'down', id))
                if is_clue:
                    id += 1
        self.clues.sort(key=lambda x:-x[0])

    def fill(self, clue_processor: ClueProcessor):
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

        def helper(grid: Grid, clues: list, iterations=2):
            """Fills in one word. TODO: set to list cast is slow!"""
            # TODO: memoize get_across(), get_down() after layout is set
            print(grid)
            if not clues:
                return grid
            length, direction, id = clues[0]
            to_fill = grid.across[id].get_across() if direction == 'across' else grid.down[id].get_down()
            constraints = [(i, to_fill[i].label) for i in range(length) if not to_fill[i].is_blank()]
            if constraints:
                candidates = list(intersection([clue_processor.words[length][x] for x in constraints]))
            else:
                candidates = list(clue_processor.words[length]['all'])
            if candidates:
                print(direction, id, candidates, clues)
                words = random.sample(candidates, min(iterations, len(candidates)))
                for word in words:
                    for i in range(length):
                        to_fill[i].label = word[i]
                    helper(grid.copy(), clues[1:])
        
        for _ in range(69):
            g = helper(self.copy(), self.clues)
            if g and filled(g):
                return g

    def copy(self):
        g = Grid(self.n, set_layout=False)
        for r in range(1, self.n + 1):
            for c in range(1, self.n + 1):
                g.cell(r, c).label = self.cell(r, c).label
        g.across, g.down, g.clues = self.across, self.down, self.clues
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
