from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum, auto
import random
from functools import cache, lru_cache
from typing import ClassVar

from crossword_generator.clue_processor import ClueProcessor


@dataclass()
class Position:
    """Should be an inner class for Cardinal, but isn't due to Enum"""

    row: int
    col: int

    def __repr__(self):
        return f'({self.row}, {self.col})'


class Cardinal(Enum):
    NORTH = Position(-1, 0)
    SOUTH = Position(1, 0)
    EAST = Position(0, 1)
    WEST = Position(0, -1)

    value: Position


class Direction(Enum):
    ACROSS = auto()
    DOWN = auto()

    def opposite(self):
        return Direction.DOWN if self is Direction.ACROSS else Direction.ACROSS


class Grid:
    """1-indexed N x N grid of Cells"""

    def __init__(self, n, set_layout=True):
        self.n = n
        self.grid = tuple(tuple(Cell(self, r, c) for c in range(n + 2)) for r in range(n + 2))
        for i in range(self.n + 2):
            self.grid[i][0].make_wall()
            self.grid[i][self.n + 1].make_wall()
            self.grid[0][i].make_wall()
            self.grid[self.n + 1][i].make_wall()

        self.across = {}
        self.down = {}
        self.ids = {}
        self.entries = []
        if set_layout:
            self.generate_layout()
            self.number_cells()

    def cell(self, r: int, c: int) -> Cell | None:
        if r < 0 or r >= len(self.grid) or c < 0 or c >= len(self.grid[0]):
            return None
        return self.grid[r][c]

    def generate_layout(self) -> None:
        """Generates a 2D array of Cells, subject to requirements on the number of 
        walls and words and lengths of words it contains. Implemented via repeatedly 
        adding walls that satisfy these requirements."""

        # TODO: make cleaner bounds
        MAX_WALL = int(0.17 * self.n ** 2 + 0.066 * self.n - 1.1)
        MAX_WORDS = int(0.34 * self.n ** 2 - 0.3 * self.n + 4)
        MIN_WORD_LENGTH = 3
        SYMMETRIC_SIZES = (11, 12, 13, 14, 15)

        curr_wall = 0
        curr_words = 2 * self.n
        available_cells = [(i, j) for i in range(1, self.n + 1) for j in
                           range(1, self.n + 1)]  # TODO: optimize to use set instead of list

        def num_added_words(r: int, c: int) -> int:
            """Returns the number of additional words that would be obtained by adding a wall at (r, c).

            Args:
                r: The row.
                c: The column.

            Returns:
                The number of additional words that would be obtained by adding a wall at (r, c).
            """
            return 2 - sum(
                self.grid[r + direction.value.row][c + direction.value.col].is_wall() for direction in Cardinal)

        def add_wall(r: int, c: int) -> None:
            nonlocal curr_wall, curr_words
            self.cell(r, c).make_wall()
            curr_wall += 1
            curr_words += num_added_words(r, c)
            available_cells.remove((r, c))

        illegal_cells = []
        if self.n in SYMMETRIC_SIZES and self.n % 2 == 1:
            for i in range(int(-(MIN_WORD_LENGTH + 1) / 2), int((MIN_WORD_LENGTH + 1) / 2)):
                illegal_cells.append((i + (self.n + 1) / 2, (self.n + 1) / 2))
                illegal_cells.append(((self.n + 1) / 2, i + (self.n + 1) / 2))

        while curr_wall < MAX_WALL and curr_words < MAX_WORDS:
            r, c = available_cells[random.randint(0, len(available_cells) - 1)]
            if all(self.cell(r, c).get_neighbor(dir).is_wall()
                   or len(self.cell(r, c).in_direction(dir)) > MIN_WORD_LENGTH for dir in Cardinal):
                if (r, c) not in illegal_cells:
                    add_wall(r, c)
                    if self.n in SYMMETRIC_SIZES:
                        add_wall(self.n + 1 - r, self.n + 1 - c)

    def number_cells(self) -> None:
        """Assigns clue numbers to cells. Specifically, assigns `across`,
        `down`, `ids`, and `entries`."""
        identifier = 1
        for r in range(1, self.n + 1):
            for c in range(1, self.n + 1):
                if self.cell(r, c).is_wall():
                    continue
                is_entry = False
                if self.cell(r, c).get_neighbor(Cardinal.WEST).is_wall():
                    is_entry = True
                    self.across[identifier] = self.cell(r, c)
                    self.ids[(r, c)] = identifier
                    self.entries.append(Entry(self, self.cell(r, c).get_across()))
                if self.cell(r, c).get_neighbor(Cardinal.NORTH).is_wall():
                    is_entry = True
                    self.down[identifier] = self.cell(r, c)
                    self.ids[(r, c)] = identifier
                    self.entries.append(Entry(self, self.cell(r, c).get_down()))
                if is_entry:
                    identifier += 1
        self.entries.sort(key=lambda e: -e.length)

    def is_filled(self) -> bool:
        return all(not (self.cell(r, c).is_blank()) for c in range(1, self.n + 1) for r in range(1, self.n + 1))

    def fill(self, clue_processor: ClueProcessor, num_attempts=10, num_sample_strings=20, num_test_strings=10,
             verbosity=0) -> None:
        """Fills in the grid, roughly* in order of decreasing word length. TODO: make this faster!

        *We actually want words to be entered in order of the number of blank cells. However,
        this is pretty annoying (and probably slow) to implement.

        Args:
            clue_processor: The clue processor.
            num_attempts: Number of times grid tries filling from scratch.
            num_sample_strings: Number of strings to sample per entry. A subset of this sample will be taken for testing.
            num_test_strings: Number of strings grid tests per entry.
            verbosity: Proportion of the time things will print.

        Returns:
            None
        """

        res: Grid | None = None
        counter = 0
        print_every = int(1 / verbosity) if verbosity else 0

        def intersection(sets: tuple[set, ...]):
            if len(sets) == 1:
                return sets[0]
            return sets[0].intersection(*sets[1:])

        # TODO: make faster
        @lru_cache(maxsize=None)
        def constraints_intersection(length: int, constraints: tuple[tuple[int, str]]):
            return tuple(
                intersection(tuple(clue_processor.words[length][constraint] for constraint in constraints))
                if len(constraints) > 0 else clue_processor.words[length]['all']
            )

        def get_candidates(entry: Entry) -> tuple[str, ...]:
            """Returns a tuple of all possible words that fit the constraints of the entry.

            Args:
                entry: the entry

            Returns:
                A tuple of all possible words that fit the constraints of the entry.
            """
            constraints = tuple((i, entry.cells[i].label) for i in range(entry.length) if not entry.cells[i].is_blank())
            return constraints_intersection(entry.length, constraints)

        def helper(grid: Grid, entries: tuple[Entry, ...] | list[Entry, ...]) -> None:
            """Fills in one word at a time, proceeding by DFS. TODO: set to list cast is slow!"""

            # TODO: memoize get_across(), get_down() after layout is set

            nonlocal res
            if res:  # if solution already exists
                return

            # verbose information
            nonlocal counter
            counter += 1
            if verbosity and counter % print_every == 0:
                print(grid)
                print()

            if not entries:  # if all entries have been previously processed
                res = grid.copy()
                return

            # process word candidates for next entry
            entry = entries[0]
            candidates = get_candidates(entry)
            words = random.sample(candidates, min(num_sample_strings, len(candidates)))

            # calculate heuristics for each word
            heuristic_scores: list[tuple[int, str]] = []

            # compute heuristics
            for word in words:
                previously_blank_cells = []
                heuristic_score = 1

                for i in range(entry.length):
                    # fill cell
                    if entry.cells[i].label == Cell.BLANK:
                        previously_blank_cells.append(entry.cells[i])
                        entry.cells[i].label = word[i]

                    # calculate heuristic score
                    orthogonal = Entry(grid, entry.cells[i].get_entry_list(entry.direction.opposite()))
                    heuristic_score *= len(get_candidates(orthogonal))
                    if heuristic_score == 0:  # optimization
                        break

                if heuristic_score != 0:
                    heuristic_scores.append((heuristic_score, word))

                # backtrack
                for cell in previously_blank_cells:
                    cell.label = Cell.BLANK

            # dfs
            for heuristic_score, word in sorted(heuristic_scores, reverse=True)[:num_test_strings]:
                previously_blank_cells = []

                # fill word
                for i in range(entry.length):
                    if entry.cells[i].label == Cell.BLANK:
                        previously_blank_cells.append(entry.cells[i])
                        entry.cells[i].label = word[i]

                helper(grid, entries[1:])

                # backtrack
                for cell in previously_blank_cells:
                    cell.label = Cell.BLANK

        for _ in range(num_attempts):
            helper(self, self.entries)
            if res and res.is_filled():
                self.__dict__.update(res.__dict__)
                return

    def copy(self) -> Grid:
        g = Grid(self.n, set_layout=False)
        for r in range(1, self.n + 1):
            for c in range(1, self.n + 1):
                g.cell(r, c).label = self.cell(r, c).label
        g.number_cells()
        return g

    def __str__(self):
        return '\n'.join(' '.join(self.cell(i, j).label for j in range(1, self.n + 1)) for i in range(1, self.n + 1))


# TODO: eq is set to False to allow hashing of Cell and thus allow get_entry_list to be cached. Refactor to not have to
#  set eq to False
@dataclass(eq=False)
class Cell:
    # WARNING: Cell.BLANK and Cell.WALL are NOT Cells!
    BLANK: ClassVar[str] = "."
    WALL: ClassVar[str] = "#"

    grid: Grid
    row: int
    col: int
    label: str = BLANK

    def __post_init__(self):
        self.get_entry_list = lru_cache(maxsize=4)(self.get_entry_list)  # allow memoization without memory leaks

    def get_neighbor(self, cardinal_direction: Cardinal) -> Cell:
        return self.grid.cell(self.row + cardinal_direction.value.row, self.col + cardinal_direction.value.col)

    def is_blank(self) -> bool:
        return self.label == Cell.BLANK

    def is_wall(self) -> bool:
        return self.label == Cell.WALL

    def make_wall(self) -> None:
        self.label = Cell.WALL

    def get_across(self) -> list[Cell, ...]:
        """Across array of Cells containing self"""
        res = self.in_direction(Cardinal.WEST)[:0:-1]  # cells in left direction
        res.append(self)
        res.extend(self.in_direction(Cardinal.EAST)[1:])  # cells in right direction
        return res

    def get_down(self) -> list[Cell, ...]:
        """Down array of Cells containing self"""
        res = self.in_direction(Cardinal.NORTH)[:0:-1]  # cells in up direction
        res.append(self)
        res.extend(self.in_direction(Cardinal.SOUTH)[1:])  # cells in down direction
        return res

    def get_entry_list(self, direction: Direction) -> list[Cell, ...]:
        return self.get_across() if direction is Direction.ACROSS else self.get_down()

    def in_direction(self, cardinal_direction: Cardinal) -> list[Cell, ...]:
        """Returns a list of cells starting at self (inclusive) until hitting a wall.

        Only used internally (for get_across and get_down).
        """
        res = []
        cur_cell = self
        while not cur_cell.is_wall():
            res.append(cur_cell)
            cur_cell = cur_cell.get_neighbor(cardinal_direction)
        return res

    def __repr__(self):
        return f'Cell({self.row}, {self.col})'


@dataclass()
class Entry:
    grid: Grid
    cells: tuple[Cell] | list[Cell]
    length: int = field(init=False)
    direction: Direction = field(init=False)
    id: int = field(init=False)

    def __post_init__(self):
        self.length = len(self.cells)

        # TODO: fix possible bug if len < 1
        self.direction = Direction.ACROSS if self.cells[0].row == self.cells[1].row else Direction.DOWN

        self.id = self.grid.ids[(self.cells[0].row, self.cells[0].col)]

    def positions(self) -> tuple[Position]:
        return tuple(Position(c.row, c.col) for c in self.cells)

    def __repr__(self):
        return f"{self.id}-{self.direction.value}"
