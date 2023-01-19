from __future__ import annotations

import numpy as np
import random
import time
from collections.abc import Sequence
from dataclasses import dataclass, field
from enum import Enum, auto
from functools import lru_cache, cache
from typing import Callable, ClassVar, Final
from unionfind import UnionFind

import generation.constants as const
from generation.clue_processor import ClueProcessor


@dataclass
class Position:
    row: int
    col: int

    def __repr__(self):
        return f'({self.row}, {self.col})'

    def add(p: Position, q: Position):
        return Position(p.row + q.row, p.col + q.col)


class Cardinal(Enum):
    NORTH = Position(-1, 0)
    SOUTH = Position(1, 0)
    EAST = Position(0, 1)
    WEST = Position(0, -1)


class Ordinal(Enum):
    N  = Cardinal.NORTH.value
    S  = Cardinal.SOUTH.value
    E  = Cardinal.EAST.value
    W  = Cardinal.WEST.value
    NE = Position.add(N, E)
    SE = Position.add(S, E)
    SW = Position.add(S, W)
    NW = Position.add(N, W)


class Direction(Enum):
    ACROSS = 'across'
    DOWN = 'down'

    def opposite(self):
        return Direction.DOWN if self is Direction.ACROSS else Direction.ACROSS


class Selector:
    """Base class for 'selector' methods used in Grid.fill()."""
    def __init__(self, heuristic_items: list[tuple[float, str]], 
                    num_test_strings: int,
                    fn: Callable([tuple[float, str]], tuple[float, str])):
        self.heuristic_items = [fn(item) for item in heuristic_items]
        self.num_test_strings = num_test_strings

    def randomize(self, factor) -> None:
        assert factor >= 1, "Randomization factor must be at least 1."
        scores, words = zip(*self.heuristic_items)
        randomize = lambda score: score * factor**random.uniform(-1, 1)
        self.heuristic_items = list(zip(map(randomize, scores), words))
    
    def select(self) -> list[str]:
        """
        List of selected strings. By default, chooses those with the
        highest fn(heuristic) scores.
        """
        return [word for _, word in sorted(self.heuristic_items, reverse=True)[:self.num_test_strings]]


class ProbabilisticSelector(Selector):
    """
    Selector that chooses words with probabilities proportional to their
    fn(heuristic) scores. The logic is the same as Selector, but introduces
    systematic randomization for more varied word choice.
    """
    def __init__(self, *args):
        super().__init__(*args)
    
    def select(self) -> list[str]:
        if self.heuristic_items:
            scores, words = zip(*self.heuristic_items)
            norm_scores = np.array(scores) / sum(scores)
            return list(np.random.choice(a=words, 
                size=min(self.num_test_strings, len(self.heuristic_items)), replace=False, p=norm_scores))
        else:
            return []


class Grid:
    """1-indexed n x n grid of Cells"""

    def __init__(self, n, generate_layout=True, verbose=False):
        self.n = n
        self.cell_range = range(1, self.n + 1)
        self.grid = tuple(tuple(Cell(self, r, c)
                                for c in range(n + 2)) for r in range(n + 2))
        for i in range(self.n + 2):
            self.grid[i][0].make_block()
            self.grid[i][self.n + 1].make_block()
            self.grid[0][i].make_block()
            self.grid[self.n + 1][i].make_block()
        self.clear()

        self.MAX_BLOCK = self.n**2//6
        self.MAX_WORDS = int(0.23*self.n**2 + 2*self.n - 3)
        self.MAX_CLUMP_SIZE = self.n//2

        if generate_layout:
            custom_globals = {'self': self}
            num_attempts = 0
            failure_causes = {lengths: 0 for lengths in const.WORD_LENGTH_REQUIREMENTS}
            while True:
                self.generate_layout()
                self.number_cells()
                num_attempts += 1
                length_req = True
                if self.n >= const.LARGE_GRID_CUTOFF:
                    for lengths, req in const.WORD_LENGTH_REQUIREMENTS.items():
                        success = sum(e.length in eval(lengths, custom_globals) \
                            for e in self.entries) in eval(req, custom_globals)
                        if not success:
                            failure_causes[lengths] += 1
                            length_req = False
                if self.is_connected and length_req:
                    if verbose:
                        failure_causes_str = {eval(k, custom_globals): v for k, v in failure_causes.items()}
                        print(f"attempts: {num_attempts}; failure counts: {failure_causes_str}")
                    break
                else:
                    self.clear()

    def cell(self, r: int, c: int) -> Cell | None:
        in_bounds = (0 <= r <= len(self.grid)) and (
            0 <= c <= len(self.grid[0]))
        return self.grid[r][c] if in_bounds else None

    def clear(self) -> None:
        for i in self.cell_range:
            for j in self.cell_range:
                self.cell(i, j).label = Cell.BLANK
        self.across = {}
        self.down = {}
        self.entries = []
        self.ids = {}

    def generate_layout(self) -> None:
        """Generates a 2D array of Cells, subject to requirements on the number of 
        blocks and words and lengths of words it contains. Implemented via repeatedly 
        adding blocks that satisfy these requirements."""
        curr_block = 0
        curr_words = 2 * self.n
        curr_attempts = 0
        attempt_limit = 0.5*self.n**2
        available_cells = [(r, c) for r in self.cell_range for c in self.cell_range]
        uf = UnionFind()

        def num_added_words(r: int, c: int) -> int:
            """
            Returns the number of additional words that would be obtained by 
            adding a block at (r, c).
            """
            return 2 - sum(self.grid[r + dir.value.row][c + dir.value.col].is_block()
                for dir in Cardinal)

        def add_block(r: int, c: int, block_neighbors: list[tuple[int, int]]) -> None:
            nonlocal curr_block, curr_words
            self.cell(r, c).make_block()
            curr_block += 1
            curr_words += num_added_words(r, c)
            available_cells.remove((r, c))
            uf.add((r, c))
            for n in block_neighbors:
                uf.union((r, c), n)

        if self.n in const.SYMMETRIC_SIZES:
            if self.n % 2 == 1:
                for i in range(-(const.MIN_WORD_LENGTH-1)//2, (const.MIN_WORD_LENGTH+1)//2):
                    try:
                        available_cells.remove((i + (self.n+1)//2, (self.n+1)//2))
                        available_cells.remove(((self.n+1)//2, i + (self.n+1)//2))
                    except ValueError:
                        pass
            else:
                for i in (0, 1):
                    for j in (0, 1):
                        available_cells.remove((self.n//2 + i, self.n//2 + j))

        while curr_block < self.MAX_BLOCK and curr_words < self.MAX_WORDS:
            r, c = available_cells[random.randint(0, len(available_cells) - 1)]
            curr_attempts += 1
            if curr_attempts > attempt_limit:
                break
            if all(self.cell(r, c).get_neighbor(cardinal_dir).is_block()
                   or len(self.cell(r, c).in_direction(cardinal_dir)) > const.MIN_WORD_LENGTH
                   for cardinal_dir in Cardinal):
                if (r, c) in available_cells:
                    curr_attempts = 0
                    block_neighbors = set(uf) & set(
                        (r + dir.value.row, c + dir.value.col) for dir in Ordinal)
                    adj_components = [uf.component(n) for n in block_neighbors]
                    if len(set().union(*adj_components)) < self.MAX_CLUMP_SIZE:
                        add_block(r, c, block_neighbors)
                        if self.n in const.SYMMETRIC_SIZES:
                            add_block(self.n + 1 - r, self.n + 1 - c, block_neighbors)

    def number_cells(self) -> None:
        """Assigns clue numbers to cells. Specifically, assigns `across`,
        `down`, `ids`, and `entries`."""
        identifier = 1
        for r in self.cell_range:
            for c in self.cell_range:
                if self.cell(r, c).is_block():
                    continue
                is_entry = False
                if self.cell(r, c).get_neighbor(Cardinal.WEST).is_block():
                    is_entry = True
                    self.across[identifier] = self.cell(r, c)
                    self.ids[(r, c)] = identifier
                    self.entries.append(
                        Entry(self, self.cell(r, c).get_across()))
                if self.cell(r, c).get_neighbor(Cardinal.NORTH).is_block():
                    is_entry = True
                    self.down[identifier] = self.cell(r, c)
                    self.ids[(r, c)] = identifier
                    self.entries.append(
                        Entry(self, self.cell(r, c).get_down()))
                if is_entry:
                    identifier += 1
        self.entries.sort(key=lambda e: -e.length)

    def is_connected(self) -> bool:
        r, c = 1, 1
        while self.cell(r, c).is_block():
            r = random.randint(1, self.n)
            c = random.randint(1, self.n)
        num_not_block = sum(not self.cell(i, j).is_block()
                            for i in self.cell_range for j in self.cell_range)
        queue, visited = [], set()
        queue.append(self.cell(r, c))
        visited.add(self.cell(r, c))
        while queue:
            u = queue.pop(0)
            for cardinal_dir in Cardinal:
                v = u.get_neighbor(cardinal_dir)
                if 1 <= v.row <= self.n and 1 <= v.col <= self.n and \
                        not v.is_block() and v not in visited:
                    queue.append(v)
                    visited.add(v)
        return len(visited) == num_not_block

    def is_filled(self) -> bool:
        return all(not (self.cell(r, c).is_blank())
                   for c in self.cell_range for r in self.cell_range)

    def fill(self, clue_processor: ClueProcessor,
             num_attempts=10, num_sample_strings=20, num_test_strings=10,
             time_limit=float('inf'), verbosity=0,
             selector_class: type[Selector] = Selector,
             fn: Callable([tuple[int, str]], tuple[int, str]) = lambda x: x,
             randomize_factor=1) -> None:
        """
        Fills with letters to form words from clue_processor.words.

        Arguments
        ---------
        num_attempts:       Number of times grid tries filling from scratch.
        num_sample_strings: Number of strings to sample per entry. A subset of 
                            this sample will be taken for testing.
        num_test_strings:   Number of strings grid tests per entry.
        verbosity:          Proportion of the time things will print.
        fn:                 Function applied to Selector.
        randomize_factor:   Randomization factor applied to Selector.
        """
        res: Grid | None = None
        used_words = set()
        counter = 0
        start_time = time.perf_counter()
        print_every = int(1 / verbosity) if verbosity else float('inf')

        # TODO: make faster
        @cache
        def constraints_intersection(length: int, constraints: tuple[tuple[int, str]]) -> set[str]:
            if constraints:
                words = [clue_processor.words[length][constraint]
                         for constraint in constraints]
                return set.intersection(*words)
            else:
                return clue_processor.words[length]['all']

        def get_candidates(entry: Entry) -> set[str]:
            """Returns a tuple of all possible words that fit the constraints 
            of the entry."""
            constraints = tuple((i, entry.cells[i].label) for i in range(
                entry.length) if not entry.cells[i].is_blank())
            return constraints_intersection(entry.length, constraints)

        def heuristic(e): 
            return len(get_candidates(e))

        def helper(grid: Grid, entries: list[Entry]) -> Entry | None:
            """
            Fills in one word at a time, proceeding by DFS.

            Returns:
                An entry that failed to be filled, or None if all entries were filled.
            """
            nonlocal res, counter
            if res:
                return
            if not entries:  # if all entries have been previously processed
                res = grid.copy()
                return
            counter += 1
            if counter % print_every == 0:
                print(grid, '\n')

            if time.perf_counter() - start_time > time_limit:
                return

            entries.sort(key=heuristic)
            entry = entries[0]
            candidates = tuple(get_candidates(entry))
            words = random.sample(candidates, min(num_sample_strings, len(candidates)))

            # compute heuristics for each word
            heuristic_items: list[tuple[float, str]] = []
            for word in words:
                if word in used_words:
                    continue
                previously_blank_cells = []
                heuristic_score = 1

                for i in range(entry.length):
                    if entry.cells[i].label == Cell.BLANK:
                        previously_blank_cells.append(entry.cells[i])
                        entry.cells[i].label = word[i]
                    orthogonal = Entry(grid, entry.cells[i].get_entry_list(
                        entry.direction.opposite()))
                    heuristic_score *= heuristic(orthogonal)
                    if heuristic_score == 0:
                        break
                
                if heuristic_score:
                    heuristic_items.append((heuristic_score, word))
                for cell in previously_blank_cells:  # backtrack
                    cell.label = Cell.BLANK

            if heuristic_items:
                selector = selector_class(heuristic_items, num_test_strings, fn)
                selector.randomize(randomize_factor)
                for word in selector.select():
                    previously_blank_cells = []
                    for i in range(entry.length):
                        if entry.cells[i].label == Cell.BLANK:
                            previously_blank_cells.append(entry.cells[i])
                            entry.cells[i].label = word[i]
                    used_words.add(word)

                    failed_entry = helper(grid, entries[1:])
                    for cell in previously_blank_cells:  # backtrack
                        cell.label = Cell.BLANK
                    used_words.remove(word)
                    if not entries[0].intersects(failed_entry):  # backjump
                        break

            return entries[0]

        for _ in range(num_attempts):
            helper(self, self.entries)
            if res and res.is_filled():
                self.__dict__.update(res.__dict__)
                return

    def copy(self) -> Grid:
        g = Grid(self.n, generate_layout=False)
        for r in self.cell_range:
            for c in self.cell_range:
                g.cell(r, c).label = self.cell(r, c).label
        g.number_cells()
        return g

    def __str__(self):
        return '\n'.join(' '.join(self.cell(i, j).label 
            for j in self.cell_range) for i in self.cell_range)


@dataclass(unsafe_hash=True)
class Cell:
    # WARNING: Cell.BLANK and Cell.BLOCK are NOT Cells!
    BLANK: ClassVar[str] = "."
    BLOCK: ClassVar[str] = "#"

    grid: Final[Grid] = field(hash=True)
    row: Final[int] = field(hash=True)
    col: Final[int] = field(hash=True)
    label: str = field(default=BLANK, hash=False)

    def __post_init__(self):
        # allow memoization without memory leaks
        self.get_entry_list = lru_cache(maxsize=4)(self.get_entry_list)

    def get_neighbor(self, dir: Cardinal | Ordinal) -> Cell:
        return self.grid.cell(self.row + dir.value.row, self.col + dir.value.col)

    def is_blank(self) -> bool:
        return self.label == Cell.BLANK

    def is_block(self) -> bool:
        return self.label == Cell.BLOCK

    def make_block(self) -> None:
        self.label = Cell.BLOCK

    def get_across(self) -> list[Cell]:
        """Across array of Cells containing self, ordered from left to right"""
        return self.in_direction(Cardinal.WEST)[:0:-1] + [self] + self.in_direction(Cardinal.EAST)[1:]

    def get_down(self) -> list[Cell]:
        """Down array of Cells containing self, ordered from top to bottom"""
        return self.in_direction(Cardinal.NORTH)[:0:-1] + [self] + self.in_direction(Cardinal.SOUTH)[1:]

    def get_entry_list(self, direction: Direction) -> list[Cell]:
        return self.get_across() if direction is Direction.ACROSS else self.get_down()

    def in_direction(self, cardinal_direction: Cardinal) -> list[Cell]:
        """Returns a list of cells starting at self (inclusive) until hitting a block."""
        res = []
        cur_cell = self
        while not cur_cell.is_block():
            res.append(cur_cell)
            cur_cell = cur_cell.get_neighbor(cardinal_direction)
        return res

    def __repr__(self):
        return f'<Cell row={self.row} col={self.col} label={self.label}>'


@dataclass()
class Entry:
    """
    Stores a grid entry, i.e. a list of Cells.

    TODO: there are many optimizations if all Entry.grid refer to the same grid 
          (i.e. if Entry is an inner class of grid). Currently, some methods use
          this assumption. Plan to make Entry an inner class of Grid in the future.
    """
    grid: Grid
    cells: Sequence[Cell]
    length: int = field(init=False)
    direction: Direction = field(init=False)
    id: int = field(init=False)

    def __post_init__(self):
        self.length = len(self.cells)

        # TODO: fix possible bug if len(self.cells) <= 1
        self.direction = Direction.ACROSS if len(self.cells) >= 2 and \
            self.cells[0].row == self.cells[1].row else Direction.DOWN

        self.id = self.grid.ids[(self.cells[0].row, self.cells[0].col)]

    @cache
    def positions(self) -> tuple[Position]:
        """Returns a tuple of Positions corresponding to the cells in this entry."""
        return tuple(Position(cell.row, cell.col) for cell in self.cells)

    def get_start_cell(self) -> Cell:
        return self.cells[0]

    def get_end_cell(self) -> Cell:
        return self.cells[-1]

    def get_contents(self) -> str:
        return ''.join(cell.label for cell in self.cells)

    def intersects(self, other: Entry | None) -> bool:
        if other is None:
            return False
        if self.direction is other.direction:
            return self.get_start_cell() == other.get_start_cell() and self.get_end_cell() == other.get_end_cell()
        if self.direction is Direction.ACROSS:
            return (
                # other has a cell in this entry's row
                other.get_start_cell().row <= self.get_start_cell().row <= other.get_end_cell().row and
                # this entry has a cell in other's column
                self.get_start_cell().col <= other.get_start_cell().col <= self.get_end_cell().col
            )
        else:   # if self.direction is Direction.DOWN
            return (
                # other has a cell in this entry's column
                other.get_start_cell().col <= self.get_start_cell().col <= other.get_end_cell().col and
                # this entry has a cell in other's row
                self.get_start_cell().row <= other.get_start_cell().row <= self.get_end_cell().row
            )

    def __repr__(self):
        return f"{self.id}-{self.direction.value}"
